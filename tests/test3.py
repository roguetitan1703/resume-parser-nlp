import os
import sys
import re
import json
from ultra_logger import Logger
from pprint import pprint
import spacy
from spacy.matcher import PhraseMatcher

# Appending the path to services
project_root = os.getcwd()
sys.path.append(f"{project_root}\\app")

from services import Scraper, OCRProcessor, ResumeProcessor, NERProcessor

test_data_path = "D:\\TY\\resume-parser-nlp\\data\\test_data"
resume_files = ["resume_1.txt", "resume_2.txt", "resume_3.txt", "resume_4.txt", "resume_5.txt"]

NERArrays = {
    "external_links": {
        "github": ["github.com"],
        "linkedin": ["linkedin.com"],
        "hackerrank": ["hackerrank.com"],
        "leetcode": ["leetcode.com"],
        "codechef": ["codechef.com"],
        "codingninjas": ["codingninjas.com"]
    },
    "social_links": {
        "instagram": ["instagram.com"],
        "twitter": ["twitter.com", "x.com"],
        "facebook": ["facebook.com"]
    },
    "programming_languages": [
        "python", "java", "javascript", "js", "c#", "c-sharp", "c++", "cpp", "ruby",
        "go", "golang", "swift", "kotlin", "php", "typescript", "ts", "scala", "rust",
        "perl", "clojure", "bash", "shell", "objective-c", "dart", "r", "matlab",
        "elixir", "haskell", "lua", "erlang", "f#", "fortran", "cobol", "sas"
    ],
    "frameworks": [
        "django", "flask", "react", "react.js", "angular", "angular.js", "vue.js", "vue",
        "spring", "spring boot", "asp.net", "ruby on rails", "express.js", "express",
        "node.js", "node", "laravel", "symfony", "ember.js", "backbone.js", "next.js",
        "nuxt.js", "svelte", "pyramid", "fastapi", "bottle", "phoenix", "meteor",
        "gatsby", "blazor", "uikit",
    ],
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "oracle", "sql server",
        "sqlserver", "ms sql", "ms-sql", "sqlite", "redis", "cassandra", "mariadb",
        "elasticsearch", "db2", "couchdb", "dynamodb", "neo4j", "influxdb", "hbase",
        "firebase", "firestore", "cockroachdb", "memcached", "sql"
    ],
    "tools": [
        "git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp",
        "google cloud platform", "tensorflow", "pytorch", "postman", "visual studio code",
        "vs code", "intellij idea", "intellij", "eclipse", "jira", "slack", "bitbucket",
        "circleci", "travisci", "heroku", "rancher", "openshift", "gitlab", "kibana",
        "airflow", "hadoop", "jupyter", "databricks", "zepl"
    ],
    "cloud_platforms": [
        "aws", "azure", "google cloud platform", "gcp", "ibm cloud", "oracle cloud",
        "alibaba cloud", "digitalocean", "linode", "rackspace", "cloudflare"
    ],
    "devops_tools": [
        "jenkins", "ansible", "terraform", "terraform cloud", "puppet", "chef", "nagios",
        "prometheus", "prom", "grafana", "splunk", "docker swarm", "saltstack",
        "new relic", "elk stack", "zabbix"
    ],
    "frontend_technologies": [
        "html", "css", "bootstrap", "tailwind css", "materialize", "bulma", "foundation",
        "semantic ui", "sass", "less", "stylus"
    ]
}

# Load resumes
def load_resumes(resume_files):
    resumes = []
    for file in resume_files:
        with open(f"{test_data_path}\\{file}", "r") as f:
            resumes.append(f.read())
    return resumes

resumes = load_resumes(resume_files)

# Initialize logger
logger = Logger(log_file="resume_processing.log", log_name="Resume processing", log_to_console=False, clear_previous=True)

# Load NLP models
custom_model = "en_tech_resume_ner_model"
nlp = spacy.load(custom_model)
default_nlp = spacy.load("en_core_web_sm")

class InfoNERProcessor:
    EMAIL_REGEX = r'[^.]([a-zA-Z0-9._%+-]+[^.])@([a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)(\s*\.[a-zA-Z]{2,})'
    PHONE_REGEX = r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{3}\)|\d{3})[\s-]?\d{2,4}[\s-]?\d{2,4}"

    def __init__(self):
        self.nlp = nlp
        self.default_nlp = default_nlp
        self.education_keywords = ["educational","university", "college", "institute", "school", "academy", "faculty", "polytechnic","iit","nit","mit",'iiit',"bit","vit","viit"]

    def preprocess_text(self,text):
        # Replace newline characters with spaces
        return text.replace('\n', ' ').strip()

    def extract_entities(self, text):
        doc = self.default_nlp(text)
        extracted_info = {
            "name": None,
            "emails": [],
            "phones": [],
            "education": [],
        }

        all_entities = []  # Store all entities

        # Extract using spaCy NER
        for ent in doc.ents:
            all_entities.append((ent.text, ent.label_))  # Collect all entities
            if ent.label_ == "PERSON" and not extracted_info["name"]:
                extracted_info["name"] = ent.text
            elif ent.label_ == "ORG":
                # Check if the ORG entity contains any education keywords
                for keyword in self.education_keywords:
                    if keyword.lower() in ent.text.lower():
                        extracted_info["education"].append(ent.text)
                        break

        # Extract emails and phones using regex
        raw_emails = re.findall(self.EMAIL_REGEX, text)
        extracted_info["emails"] = [email_parts[0]+'@'+email_parts[1]+email_parts[2] for email_parts in raw_emails]

        extracted_info["phones"] = re.findall(self.PHONE_REGEX, text)

        # print("Default NER Extracted Entities:")
        # for entity in all_entities:
        #     print(f" - {entity[0]}: {entity[1]}")

        return extracted_info
    
    def extract_custom_entities(self, text):
        # entities = ['Graduation Year', 'Skills', 'College Name', 'Designation', 'Email Address', 'Location', 'Name', 'Companies worked at']
        # Keeping the ones we need
        entities = ['Graduation Year', 'Designation', 'Location', 'Companies worked at']
        
        doc = self.nlp(text)
        
        extracted_info = {}
        all_entities = []  # Store all entities

        # Extract using custom spaCy NER
        for ent in doc.ents:
            all_entities.append((ent.text, ent.label_))  # Collect all entities
            if ent.label_ in entities:
                if ent.label_ in extracted_info.keys():
                    extracted_info[ent.label_].append(ent.text)
                else:
                    extracted_info[ent.label_] = [ent.text]

        # print("Custom NER Extracted Entities:")
        # for entity in all_entities:
        #     print(f" - {entity[0]}: {entity[1]}")

        return extracted_info
    
    def extract_matched_skills(self, text):
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        matched_skills = {}

        # Add patterns to the matcher for each skill category
        for category, skills in NERArrays.items():
            patterns = [self.nlp.make_doc(skill) for skill in skills]
            matcher.add(category, patterns)

        # Process the sample text
        doc = self.nlp(text.lower())  # Convert text to lowercase to match the patterns

        # Find matches in the text
        matches = matcher(doc)

        # Extract matched skills with their categories
        for match_id, start, end in matches:
            category = self.nlp.vocab.strings[match_id]  # Get the category name
            skill = doc[start:end].text.strip().lower()  # Get the matched skill
            if category not in matched_skills:
                matched_skills[category] = []
            if skill not in matched_skills[category]:
                matched_skills[category].append(skill)

        return matched_skills

    def extract_all_entities(self, text):
        
         # Preprocess the text before extracting entities
        text = self.preprocess_text(text)

        # Extract information from various methods
        general_info = self.extract_entities(text)
        custom_info = self.extract_custom_entities(text)
        matched_skills = self.extract_matched_skills(text)

        # Combine all the extracted information into one dictionary without a subkey
        combined_info = {}
        for info in [general_info, custom_info, matched_skills]:
            for key, value in info.items():
                if key not in combined_info:
                    combined_info[key] = value
                                    
        return combined_info

    

def matchResumes(resumes):
    processor = InfoNERProcessor()
    all_extracted_info = {}
    for n in range(len(resumes)):
        ch = input(f"Test resume_{n + 1}.txt? (y/n): ")
        if ch.lower() == 'y':
            extracted_info = processor.extract_all_entities(resumes[n])
            all_extracted_info[f"resume_{n + 1}"] = extracted_info
            
            # Print the extracted information for the current resume
            print(f"\nExtracted Information for resume_{n + 1}.txt:")
            print(json.dumps(extracted_info, indent=2))
            
    return all_extracted_info

if __name__ == "__main__":
    extracted_resumes = matchResumes(resumes)
    print(json.dumps(extracted_resumes, indent=2))
