import spacy

class ResumeParser:
    def __init__(self, model="en_core_web_sm"):
        self.nlp = spacy.load(model)

    def parse(self, text):
        doc = self.nlp(text)
        resume_data = {
            "name": self.extract_name(doc),
            "skills": self.extract_skills(doc),
            "experience": self.extract_experience(doc),
            "education": self.extract_education(doc),
        }
        return resume_data

    def extract_name(self, doc):
        # Use named entity recognition to extract the name
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return "Name not found"

    def extract_skills(self, doc):
        # A placeholder for skills extraction logic
        return ["Python", "Machine Learning"]  # Example

    def extract_experience(self, doc):
        # Placeholder for extracting experience
        return "Experience info"

    def extract_education(self, doc):
        # Placeholder for extracting education info
        return "Education info"
