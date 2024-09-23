# from . import Scraper, OCRProcessor, ResumeProcessor, NERProcessor
from NERProcessor import NERProcessor
from ultra_logger import Logger  # Assuming you're using ultra_logger
from pprint import pprint
import spacy
from spacy.matcher import PhraseMatcher

# Initialize logger
logger = Logger(log_file="resume_processing.log", log_name="Resume processing")  # Example logger
# resume_processor = ResumeProcessor(logger)  # Initialize the ResumeProcessor
ner_processor = NERProcessor(logger, save_to_mongo= False)

data = """
 \n SUMMARY/OBJECTIVE   \n   \n Om Singh  Chandel   +91- 9685890401   \n  omchandel1703@gmail.com   \n   Pune,  Maharashtra   \n   LinkedIn   \n   \n   \n A passionate second -year B.Tech CSE student (AI & DS specialization) at MIT World Peace University, eager  \n to leverage strong coding skills and a growing interest in data science and machine learning in a challenging  \n internship. Possesses a strong work ethi c, a dedication to continuous learning, and a desire to contribute  \n meaningfully to a team's success.   \n   \n PROJECTS   \n MUSIC  RECOMMENDATION  ENGINE   \n ● Developed  the recommendation  engine  on Python.   \n ● Trained  a Word2Vec  model  on genres  names  to establish  relations  in music  features  data.  Used  K-means   \n clustering  and Co-occurrence  matrix  to create  a hierarchy of  these  relations   \n ● The K-means  clustering  algorithm was  able to create a  hierarchy of  these  relations  with 200 clusters.   \n ● Managed  the flow of user data with Json  format  to keep  track of  the user’s listening  history .  \n ● Git repo  \n   \n RECIPE EXPLORER & MANA GEMENT  YARD   \n ● Built a dynamic web application for recipe management and exploration using FastAPI, a modern Python web  \n framework.   \n ● Implemented a MongoDB database to efficiently store and retrieve recipe data, allowing users to search, view,  \n and save recipes.   \n ● Designed a user -friendly interface that facilitates recipe explo ration and management, enhancing user  \n experience.   \n ● Utilized modern web development practices to ensure the application's scalability and performance.   \n ● Git repo  \n   \n MOCK TEST WEBSITE  (CATPR EPHUB )  \n ● Developed a web platform using Django, a high -level Python framework, to assist students in their preparation  \n for the CAT exam (India).   \n ● Implemented features like simulated CAT exams with customizable sections (Quantitative Aptitude, Verbal  \n Ability, Logical Reasoning, Data Interpretation), engaging questions, and time limits.   \n ● Provided performance analysis tools to help students understand their strengths and weaknesses, enabling them  \n to focus their studying efforts effectively.   \n ● Git repo   \n   \n   \n SKILLS   \n ● Programming Languages : Python, H TML, Ja vaScript, TypeScript, CSS, PHP( Wordpress) .  \n ● Frameworks & Li braries: React -Native , React, Node, Bootstrap , Django, FastAP I.  \n ● Tools & Systems: G it (Version control), Vscod e, Xampp  \n ● Other Skills: REST  APIs, MySQL, SQLite, MongoD B, Wordpress.   \n   \n   \n   \n   \n   \n ACHIEVEMENTS    \n ● Won first prize at the DYP Nexus 2024  \n 5G Ideathon , pres ented  a V2X model for  \n Emergency reponses a nd Dynamic tra ffic  \n manage ment .  \n ● Successfully tackled over 150 DSA   \n questions  (Easy,  Medium,  and Hard)  on  \n prominent platforms, majorly on LeetCode   \n and Hackerrank  ● Achieved 3rd place in the Codex Coding Competition   \n Basic level (2023).   \n ● Currently an active member of the CSI MIT -WPU Chapter   \n since 2023.   \n ● Played an integral role in the organization of the   \n Texephyr’23  and lead the tech competitions of  \n Texephyr ’24 tech event s at MITWPU.   \n EDUCATION    \n Name  of College:  MIT World Peace  University   \n Course: Btech -CSE AI & DS  \n Years:  2022 -present   \n CERTIFICATIONS    \n ● Problem  Solving  (Basic)  Certificate  (Hackerrank)   \n ● Problem  Solving  (Intermediate)  Certificate  (Hackerrank)   \n ● Python  (Basic)  Certificate  (Hackerrank)   \n   \n LINKS   \n ● LeetCode:  roguetitan   \n ● Hackerrank:  roguetitan   \n ● Github:  roguetitan1703   \n ● Fiver r: roguetit an_17   \n
"""

def print_processed_entities(data=data):
    entities = ner_processor.process_resume(data)

    # Return the extracted entities as a JSON response
    pprint(entities, indent=4)


# Initialize SpaCy model
nlp = spacy.load("en_core_web_sm")

# Define sample NERArrays with skills in lowercase
NERArrays = {
    "programming_languages": [
        "python", "java", "javascript", "c#", "c++", "ruby", "go", "swift", "kotlin", 
        "php", "typescript", "scala", "rust", "perl", "clojure"
    ],
    "frameworks": [
        "django", "flask", "react", "angular", "vue.js", "spring", "asp.net", 
        "ruby on rails", "express.js", "node.js", "laravel", "symfony", "ember.js", 
        "backbone.js"
    ],
    "databases": [
        "mysql", "postgresql", "mongodb", "oracle", "sql server", "sqlite", "redis", 
        "cassandra", "mariadb", "elasticsearch"
    ],
    "tools": [
        "git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp", 
        "tensorflow", "pytorch", "postman", "visual studio code", "intellij idea", 
        "eclipse", "jira", "slack"
    ],
    "cloud_platforms": [
        "aws", "azure", "google cloud platform", "ibm cloud", "oracle cloud"
    ],
    "devops_tools": [
        "jenkins", "ansible", "terraform", "puppet", "chef", "nagios", 
        "prometheus", "grafana"
    ]
}

def testPhraseMatcher():
        
    # Initialize PhraseMatcher with case-insensitive matching
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    # Add patterns to the matcher for each skill category
    for category, skills in NERArrays.items():
        patterns = [nlp.make_doc(skill) for skill in skills]
        matcher.add(category, patterns)

    # Sample resume text
    sample_text = """
    John Doe
    Email: john.doe@example.com
    Phone: +1 (555) 123-4567

    Professional Summary:
    Experienced software developer with expertise in Python, JavaScript, and Java. Proficient in frameworks such as Django, React, and Angular. 
    Skilled in database management using MySQL and MongoDB. Familiar with tools like Git, Docker, and Jenkins. 
    Cloud experience with AWS and Azure.

    Work Experience:
    - Developed web applications using Python and Django.
    - Built responsive front-ends with React and Angular.
    - Managed databases with MySQL and MongoDB.
    - Utilized Docker and Kubernetes for containerization.
    - Implemented CI/CD pipelines using Jenkins.
    - Deployed applications on AWS and Azure.
    """

    # Process the sample text
    doc = nlp(sample_text.lower())  # Convert text to lowercase to match the patterns

    # Find matches in the text
    matches = matcher(doc)

    # Extract and print matched skills with their categories
    matched_skills = {}
    for match_id, start, end in matches:
        category = nlp.vocab.strings[match_id]  # Get the category name
        skill = doc[start:end].text.strip().lower()  # Get the matched skill
        if category not in matched_skills:
            matched_skills[category] = []
        if skill not in matched_skills[category]:
            matched_skills[category].append(skill)

    # Print the matched skills
    print("Matched Skills:")
    for category, skills in matched_skills.items():
        print(f"{category.capitalize()}: {', '.join(skills)}")


if __name__ == "__main__":
    testPhraseMatcher()