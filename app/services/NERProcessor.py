import spacy
import re
from pymongo import MongoClient
from spacy.matcher import PhraseMatcher
import logging

# Define NERArrays directly in the code
NERArrays = {
    "external_links": {
        "GitHub": ["github.com"],
        "LinkedIn": ["linkedin.com"],
        "HackerRank": ["hackerrank.com"],
        "LeetCode": ["leetcode.com"],
        "CodeChef": ["codechef.com"],
        "CodingNinjas": ["codingninjas.com"]
    },
    "social_links": {
        "Instagram": ["instagram.com"],
        "Twitter": ["twitter.com", "x.com"],
        "Facebook": ["facebook.com"]
    },
    "programming_languages": [
        "Python", "Java", "JavaScript", "C#", "C++", "Ruby", "Go", "Swift", "Kotlin", 
        "PHP", "TypeScript", "Scala", "Rust", "Perl", "Clojure"
    ],
    "frameworks": [
        "Django", "Flask", "React", "Angular", "Vue.js", "Spring", "ASP.NET", 
        "Ruby on Rails", "Express.js", "Node.js", "Laravel", "Symfony", "Ember.js", 
        "Backbone.js"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQL Server", "SQLite", "Redis", 
        "Cassandra", "MariaDB", "Elasticsearch"
    ],
    "tools": [
        "Git", "Docker", "Kubernetes", "Jenkins", "AWS", "Azure", "GCP", 
        "TensorFlow", "PyTorch", "Postman", "Visual Studio Code", "IntelliJ IDEA", 
        "Eclipse", "JIRA", "Slack"
    ],
    "cloud_platforms": [
        "AWS", "Azure", "Google Cloud Platform", "IBM Cloud", "Oracle Cloud"
    ],
    "devops_tools": [
        "Jenkins", "Ansible", "Terraform", "Puppet", "Chef", "Nagios", 
        "Prometheus", "Grafana"
    ]
}

class NERProcessor:
    def __init__(self, logger, mongo_uri = '', db_name= '', collection_name = '', save_to_mongo=True):
        """
        Initializes the NERProcessor with the provided logger, MongoDB connection details,
        and the predefined NERArrays data.

        :param logger: Logger object for logging information and errors.
        :param mongo_uri: MongoDB connection URI.
        :param db_name: Name of the MongoDB database.
        :param collection_name: Name of the MongoDB collection.
        """

        # Assign the injected logger
        self.log = logger
        self.save_to_mongo = save_to_mongo  # New flag
        # Initialize MongoDB connection only if save_to_mongo is True
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
        try:
            ner_data = NERArrays  # Use the predefined NERArrays dictionary
            # Extract skills and links
            self.skill_categories = {
                "programming_languages": ner_data.get("programming_languages", []),
                "frameworks": ner_data.get("frameworks", []),
                "databases": ner_data.get("databases", []),
                "tools": ner_data.get("tools", []),
                "cloud_platforms": ner_data.get("cloud_platforms", []),
                "devops_tools": ner_data.get("devops_tools", [])
            }
            self.external_links_categories = ner_data.get("external_links", {})
            self.social_links_categories = ner_data.get("social_links", {})
            self.log.info("Loaded NERArrays data directly from the code.")
        except Exception as e:
            self.log.error(f"Failed to assign NERArrays data: {e}")
            raise e

        # Initialize PhraseMatcher for skills
        try:
            self.skill_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
            for category, patterns in self.skill_categories.items():
                patterns = [self.nlp.make_doc(text) for text in patterns]
                self.skill_matcher.add(category, patterns)
            self.log.info("Initialized PhraseMatcher with skill patterns.")
        except Exception as e:
            self.log.error(f"Failed to initialize PhraseMatcher: {e}")
            raise e

        # Precompile regex patterns for emails, phones, and URLs
        self.email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_regex = re.compile(r'\b\d{10}\b|\+\d{1,3}\s?\d{1,14}\b')
        
        self.url_regex = re.compile(r'(?P<url>https?://[^\s]+)')
        self.log.info("Precompiled regex patterns for emails, phones, and URLs.")

    def preprocess_text(self, text):
        """
        Cleans the extracted text by removing special characters, newlines, and extra spaces.

        :param text: Raw text extracted from the resume.
        :return: Cleaned text.
        """
        text = re.sub(r'\n+', ' ', text)  # Remove newlines
        text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
        return text.strip()

    def extract_entities(self, text):
        """
        Extracts entities from the preprocessed text, including personal details,
        skills, certifications, and links.

        :param text: Cleaned resume text.
        :return: Dictionary containing extracted entities.
        """
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
        educational_keywords = ["University", "College", "Institute", "Academy", "School"]

        # Extract general entities using SpaCy's NER
        for ent in doc.ents:
            if ent.label_ == "PERSON" and not entities["name"]:
                entities["name"] = ent.text
                self.log.debug(f"Extracted name: {ent.text}")
            elif ent.label_ == "ORG":
                # Heuristic: Check if the organization is an educational institution
                if any(keyword.lower() in ent.text.lower() for keyword in educational_keywords):
                    entities["education"].append(ent.text)
                    self.log.debug(f"Extracted education: {ent.text}")
                else:
                    # Optionally, handle companies separately if needed
                    self.log.debug(f"Found organization (not education): {ent.text}")
            elif ent.label_ == "GPE":
                # Handle location if needed
                self.log.debug(f"Found geopolitical entity: {ent.text}")

        # Extract email and phone using regex
        email_match = self.email_regex.search(text)
        phone_match = self.phone_regex.search(text)

        if email_match:
            entities["email"] = email_match.group()
            self.log.debug(f"Extracted email: {entities['email']}")
        if phone_match:
            entities["phone"] = phone_match.group()
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
        """
        Extracts and categorizes skills from the text using PhraseMatcher.

        :param text: Cleaned resume text.
        :return: Dictionary of categorized skills.
        """
        doc = self.nlp(text)
        matches = self.skill_matcher(doc)
        skills = {category: [] for category in self.skill_categories}

        for match_id, start, end in matches:
            category = self.nlp.vocab.strings[match_id]
            skill = doc[start:end].text
            if skill not in skills[category]:
                skills[category].append(skill)
                self.log.debug(f"Extracted skill - Category: {category}, Skill: {skill}")
        
        return skills

    def extract_certifications(self, text):
        """
        Extracts certifications from the text using predefined regex patterns.

        :param text: Cleaned resume text.
        :return: List of extracted certifications.
        """
        certifications = []
        certification_patterns = [
            r'Certified\s+[A-Za-z\s]+',
            r'Certification\s+in\s+[A-Za-z\s]+',
            r'[A-Za-z\s]+ Certification'
        ]
        for pattern in certification_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)
            if matches:
                self.log.debug(f"Extracted certifications with pattern '{pattern}': {matches}")
        return certifications

    def extract_external_links(self, text):
        """
        Extracts and categorizes external links (e.g., GitHub, LinkedIn) from the text.

        :param text: Cleaned resume text.
        :return: Dictionary of categorized external links.
        """
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
        """
        Extracts and categorizes social links (e.g., Instagram, Twitter) from the text.

        :param text: Cleaned resume text.
        :return: Dictionary of categorized social links.
        """
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
        """
        Stores the extracted resume data in MongoDB. Only called if save_to_mongo is True.
        """
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
        """
        Processes the raw resume text by cleaning it, extracting entities, and storing the data in MongoDB.

        :param text: Raw text extracted from the resume.
        :return: Dictionary containing all extracted entities.
        """
        cleaned_text = self.preprocess_text(text)
        self.log.debug("Preprocessed resume text.")
        entities = self.extract_entities(cleaned_text)
        self.store_in_mongodb(entities)
        return entities
