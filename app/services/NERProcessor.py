import spacy
import re
from pymongo import MongoClient
from spacy.matcher import PhraseMatcher
import logging

# Define NERArrays directly in the code, converted to lowercase
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
        "gatsby", "blazor", "uikit"
    ],
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "oracle", "sql server", 
        "sqlserver", "ms sql", "ms-sql", "sqlite", "redis", "cassandra", "mariadb", 
        "elasticsearch", "db2", "couchdb", "dynamodb", "neo4j", "influxdb", "hbase", 
        "firebase", "firestore", "cockroachdb", "memcached"
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

class NERProcessor:
    def __init__(self, logger, mongo_uri='', db_name='', collection_name='', save_to_mongo=True):
        """Initializes the NERProcessor with the provided logger and MongoDB connection details."""
        self.log = logger
        self.save_to_mongo = save_to_mongo
        if self.save_to_mongo:
            try:
                self.client = MongoClient(mongo_uri)
                self.db = self.client[db_name]
                self.collection = self.db[collection_name]
                self.log.info(f"Connected to MongoDB: {db_name}, collection: {collection_name}")
            except Exception as e:
                self.log.error(f"Failed to connect to MongoDB: {e}")
                raise e

        # Load SpaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.log.info("Loaded SpaCy model 'en_core_web_sm'.")
        except Exception as e:
            self.log.error(f"Failed to load SpaCy model: {e}")
            raise e

        # Assign NERArrays data
        self.skill_categories = {
            "programming_languages": NERArrays["programming_languages"],
            "frameworks": NERArrays["frameworks"],
            "databases": NERArrays["databases"],
            "tools": NERArrays["tools"],
            "cloud_platforms": NERArrays["cloud_platforms"],
            "devops_tools": NERArrays["devops_tools"],
            "frontend_technologies": NERArrays["frontend_technologies"]
        }
        self.external_links_categories = NERArrays["external_links"]
        self.social_links_categories = NERArrays["social_links"]
        self.log.info("Loaded NERArrays data directly from the code.")

        # Initialize PhraseMatcher for skills
        self.skill_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        for category, patterns in self.skill_categories.items():
            patterns = [self.nlp.make_doc(text) for text in patterns]
            self.skill_matcher.add(category, patterns)
        self.log.info("Initialized PhraseMatcher with skill patterns.")

        # Precompile regex patterns for emails, phones, and URLs
        self.email_regex = re.compile(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}')
        self.phone_regex = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{3}\)|\d{3})[\s-]?\d{2,4}[\s-]?\d{2,4}")
        self.url_regex = re.compile(r'(https?://[^\s]+)', re.IGNORECASE)
        self.log.info("Precompiled regex patterns for emails, phones, and URLs.")

    def preprocess_text(self, text):
        """Cleans the extracted text by removing special characters, newlines, and extra spaces."""
        text = re.sub(r'\n+', ' ', text)  # Remove newlines
        text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
        return text.strip().lower()  # Normalize to lowercase

    def extract_entities(self, text):
        """Extracts entities from the preprocessed text, including personal details, skills, certifications, and links."""
        doc = self.nlp(text)
        entities = {
            "name": None,
            "email": None,
            "phone": None,
            "skills": {category: [] for category in self.skill_categories},
            "education": [],
            "certifications": [],
            "external_links": {key: [] for key in self.external_links_categories.keys()},
            "social_links": {key: [] for key in self.social_links_categories.keys()}
        }

        # Define educational keywords for heuristic
        educational_keywords = ["university", "college", "institute", "academy", "school"]

        # Attempt to extract name from PERSON entities
        possible_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        if possible_names:
            entities["name"] = ' '.join(possible_names).lower()  # Normalize name to lowercase
            self.log.debug(f"Extracted name: {entities['name']}")

        # If no name is found, use a heuristic based on the first few words
        if not entities["name"]:
            words = text.split()
            if len(words) >= 2:
                entities["name"] = f"{words[0]} {words[1]}".lower()  # Using the first two words as a potential name
                self.log.debug(f"Fallback name extracted: {entities['name']}")

        # Extract educational institutions
        for ent in doc.ents:
            if ent.label_ == "ORG" and any(keyword in ent.text.lower() for keyword in educational_keywords):
                entities["education"].append(ent.text.lower())  # Normalize education to lowercase
                self.log.debug(f"Extracted education: {ent.text}")

        # Extract email and phone using regex
        email_match = self.email_regex.search(text)
        phone_match = self.phone_regex.search(text)

        if email_match:
            entities["email"] = email_match.group().lower()  # Normalize email to lowercase
            self.log.debug(f"Extracted email: {entities['email']}")
        if phone_match:
            entities["phone"] = phone_match.group()  # Phone number normalization may not be needed
            self.log.debug(f"Extracted phone: {entities['phone']}")

        # Extract skills using PhraseMatcher
        skills = self.extract_skills(text)
        entities["skills"] = skills

        # Extract certifications
        certifications = self.extract_certifications(text)
        entities["certifications"] = certifications

        # Extract external links
        external_links = self.extract_external_links(text)
        entities["external_links"] = external_links

        # Extract social links
        social_links = self.extract_social_links(text)
        entities["social_links"] = social_links

        return entities

    def extract_skills(self, text):
        """Extracts and categorizes skills from the text using PhraseMatcher."""
        doc = self.nlp(text)
        matches = self.skill_matcher(doc)
        skills = {category: [] for category in self.skill_categories}

        for match_id, start, end in matches:
            category = self.nlp.vocab.strings[match_id]
            skill = doc[start:end].text.strip().lower()  # Convert skill to lowercase
            if skill not in skills[category]:
                skills[category].append(skill)
                self.log.debug(f"Extracted skill - Category: {category}, Skill: {skill}")

        return skills

    def extract_certifications(self, text):
        """Extracts certifications from the text using predefined regex patterns."""
        certifications = []
        certification_patterns = [
            r'certified\s+[a-z\s]+',
            r'certification\s+in\s+[a-z\s]+',
            r'[a-z\s]+ certification'
        ]
        for pattern in certification_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend([cert.lower() for cert in matches])  # Normalize certifications to lowercase
            if matches:
                self.log.debug(f"Extracted certifications with pattern '{pattern}': {matches}")
        return certifications

    def extract_external_links(self, text):
        """Extracts and categorizes external links (e.g., GitHub, LinkedIn) from the text."""
        urls = self.url_regex.findall(text)
        categorized_links = {key: [] for key in self.external_links_categories.keys()}

        for url in urls:
            for platform, patterns in self.external_links_categories.items():
                if any(pattern.lower() in url.lower() for pattern in patterns):
                    categorized_links[platform].append(url)
                    self.log.debug(f"Extracted external link - Platform: {platform}, URL: {url}")
                    break  # Stop checking other platforms if a match is found

        return categorized_links

    def extract_social_links(self, text):
        """Extracts and categorizes social links (e.g., Instagram, Twitter) from the text."""
        urls = self.url_regex.findall(text)
        categorized_social_links = {key: [] for key in self.social_links_categories.keys()}

        for url in urls:
            for platform, patterns in self.social_links_categories.items():
                if any(pattern.lower() in url.lower() for pattern in patterns):
                    categorized_social_links[platform].append(url)
                    self.log.debug(f"Extracted social link - Platform: {platform}, URL: {url}")
                    break  # Stop checking other platforms if a match is found

        return categorized_social_links

    def store_in_mongodb(self, resume_data):
        """Stores the extracted resume data in MongoDB. Only called if save_to_mongo is True."""
        if self.save_to_mongo:
            try:
                self.collection.update_one(
                    {"email": resume_data.get("email")},
                    {"$set": resume_data},
                    upsert=True
                )
                self.log.info(f"Resume data for '{resume_data.get('email')}' inserted/updated successfully.")
            except Exception as e:
                self.log.error(f"Error inserting/updating MongoDB: {e}")
        else:
            self.log.debug("Skipping MongoDB storage as save_to_mongo is False.")

    def process_resume(self, text):
        """Processes the raw resume text by cleaning it, extracting entities, and storing the data in MongoDB."""
        cleaned_text = self.preprocess_text(text)
        self.log.debug("Preprocessed resume text.")
        entities = self.extract_entities(cleaned_text)
        self.store_in_mongodb(entities)
        return entities
