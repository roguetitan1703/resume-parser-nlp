import logging
import re
import os
from bson import ObjectId

import json, random, string
from pymongo import MongoClient
from spacy.matcher import PhraseMatcher
import spacy

# from NERData import NER_ARRAYS as NERArrays
from .NERData import *
class NERProcessor:
    
    def __init__(self, logger: logging.Logger = None, mongo_uri: str = "mongodb://localhost:27017/", db_name: str = "resume_db"):
        # Initialize logger
        """
        Initialize the NERProcessor.

        Parameters
        ----------
        logger : logging.Logger, optional
            The logger to use. If None, a new logger will be created.
        mongo_uri : str, optional
            The MongoDB URI. Defaults to "mongodb://localhost:27017/"
        db_name : str, optional
            The name of the MongoDB database to use. Defaults to "resume_db"

        Notes
        -----
        The NERProcessor is responsible for processing text data and extracting relevant information such as
        skills, education, and work experience using Named Entity Recognition (NER). It uses a custom NER model
        trained on a dataset of resumes, and also uses a default English language model for general NER tasks.
        """
        if logger is None:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
            
        # Make sure the records.json is empty
        self.record_file_path = "D:\\TY\\resume-parser-nlp\\app\\static\\record.json"
        if os.path.exists(self.record_file_path):
            open(self.record_file_path, 'w').close()
            
        # Initialize Data Strings and Arrays
        self.education_keywords = EDUCATION_WORDS
        self.NERArrays = NER_ARRAYS
        self.Email_regex = EMAIL_REGEX
        self.Phone_regex = PHONE_REGEX
        
        # Initialize MongoDB client
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]

        # Initialize your NLP models
        self.custom_model = "app\\services\\en_tech_resume_ner_model"
        self.nlp = spacy.load(self.custom_model)
        self.default_nlp = spacy.load("en_core_web_sm")

    def preprocess_text(self, text):
        """
        Preprocesses the text by replacing newline characters with spaces and stripping the text.

        Parameters
        ----------
        text : str
            The text to preprocess.

        Returns
        -------
        str
            The preprocessed text.
        """
        # handle \n, \r, \t
        text = text.replace('\r', " ")
        return text.replace('\n', ' ').strip()

    def extract_entities(self, text):
        """
        Extracts entities from the text using spaCy NER.

        Parameters
        ----------
        text : str
            The text from which to extract entities.

        Returns
        -------
        dict
            A dictionary with the following keys: name, emails, phones, education. The values are lists of strings.
        """
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
        raw_emails = re.findall(self.Email_regex, text)
        extracted_info["emails"] = [email_parts[0] + '@' + email_parts[1] + '.' + email_parts[2] for email_parts in raw_emails]
        extracted_info["phones"] = re.findall(self.Phone_regex, text)

        return extracted_info
    
    def extract_custom_entities(self, text):
        """
        Extracts custom entities from the text using a custom spaCy NER model.

        Parameters
        ----------
        text : str
            The text from which to extract entities.

        Returns
        -------
        dict
            A dictionary with the following keys: 'Graduation Year', 'Designation', 'Location', 'Companies worked at'. The values are lists of strings.
        """
        
        # Entities to extract
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

        return extracted_info
    
    def extract_matched_skills(self, text):
        """
        Extracts matched skills from the text using a PhraseMatcher and updates the record.json.

        Parameters
        ----------
        text : str
            The text from which to extract matched skills.

        Returns
        -------
        dict
            A dictionary with the following keys: 'Programming Languages', 'Frameworks', 'External Links', 'Social Links'. 
            The values are lists of strings.
        """
        
        # Initialize PhraseMatcher
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        matched_skills = {}

        # Add patterns to the matcher for each skill category
        for category, skills in self.NERArrays.items():  # Assuming NERArrays is defined elsewhere
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

        # Load existing records from the record.json file
        if os.path.exists(self.record_file_path):
            with open(self.record_file_path, 'r', encoding='utf-8') as file:
                try:
                    existing_records = json.load(file)
                except json.JSONDecodeError:
                    existing_records = {}  # Initialize empty if file is corrupted or empty
        else:
            existing_records = {}

        # Update existing records with the new matched skills
        for category, skills in matched_skills.items():
            if category in existing_records:
                # Add new skills that are not already in the record
                existing_records[category].extend([skill for skill in skills if skill not in existing_records[category]])
            else:
                # Create a new category if it doesn't exist
                existing_records[category] = skills

        # Write updated records back to the record.json file
        with open(self.record_file_path, 'w', encoding='utf-8') as file:
            json.dump(existing_records, file, ensure_ascii=False, indent=4)

        return matched_skills

    def extract_all_entities(self, text):
        """
        Extracts all entities from the text using multiple methods.

        Parameters
        ----------
        text : str
            The text from which to extract entities.

        Returns
        -------
        dict
            A dictionary with all the extracted entities as keys and their corresponding values as lists of strings.

        """
        
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
    
    def bulk_extract_all_entities(self, texts):
        all_entities = []
        for text in texts:
            combined_info = {}
            info = self.extract_all_entities(text)
            for key, value in info.items():
                if key not in combined_info:
                    combined_info[key] = value
            all_entities.append(combined_info)

        # Also return the record.json
        with open(self.record_file_path, 'r', encoding='utf-8') as file:
            record = json.load(file)
            
        return [all_entities, record]
    
    def bulk_save_to_mongo(self, data):
        """
        Saves a list of extracted information to a MongoDB database. into a particular collection (random name) and returns the collection name for later fetching

        Parameters
        ----------
        data : list
            A list of dictionaries containing the extracted information.

        Returns
        -------
        None

        Raises
        ------
        Exception
            If there is any error while saving data to MongoDB.
        """
        
        # initiate the connection with mongo
        # generate a random collection
        collection_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            self.logger.error(f"Error connecting to MongoDB: {e}")
            
        try:
            self.db[collection_name].insert_many(data)
            self.logger.info("Data saved to MongoDB successfully.")
        except Exception as e:
            self.logger.error(f"Error saving to MongoDB: {e}")
        
        return collection_name

    def save_to_mongo(self, data):
        """
        Saves the extracted information to a MongoDB database.

        Parameters
        ----------
        data : dict
            The dictionary containing the extracted information.

        Returns
        -------
        None

        Raises
        ------
        Exception
            If there is any error while saving data to MongoDB.
        """
        try:
            self.db.resumes.insert_one(data)
            self.logger.info("Data saved to MongoDB successfully.")
        except Exception as e:
            self.logger.error(f"Error saving to MongoDB: {e}")

    def fetch_data_from_mongo(self, collection_name):
        """
        Fetches all the data from the specified MongoDB collection.

        Parameters
        ----------
        collection_name : str
            The name of the collection to fetch the data from.

        Returns
        -------
        data : list
            A list of documents fetched from the collection.
        """
        try:
                
            # try:
                # self.client = MongoClient(self.mongo_uri)
                # self.db = self.client[self.db_name]
                # self.logger.info("Connected to MongoDB successfully.")
            # except Exception as e:
                # self.logger.error(f"Error connecting to MongoDB: {e}")

            collection = self.db[collection_name]
            data = list(collection.find({}))

            # Convert ObjectId fields to strings for serialization
            def serialize_mongo_id(entity):
                if isinstance(entity, ObjectId):
                    return str(entity)
                if isinstance(entity, dict):
                    return {k: serialize_mongo_id(v) for k, v in entity.items()}
                elif isinstance(entity, list):
                    return [serialize_mongo_id(i) for i in entity]
                return entity
            
            # Serialize ObjectIds in the fetched data
            serialized_data = [serialize_mongo_id(doc) for doc in data]

            self.logger.info(f"Fetched {len(serialized_data)} documents from collection '{collection_name}'.")
            return serialized_data
        except Exception as e:
            self.logger.error(f"Error fetching data from MongoDB: {e}")
            raise
