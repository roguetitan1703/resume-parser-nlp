import os
import zipfile
from PyPDF2 import PdfReader
from docx import Document
from spire.doc import Document as SpireDoc
import nltk

class ResumeProcessor:
    def __init__(self, logger, preprocess=False):
        self.log = logger
        self.preprocess = preprocess

    def preprocess_text(self, text):
        """
        Preprocesses the given text.
        """
        # Remove the /n and tokenize the text
        text = text.replace("\n", " ")
        tokens = nltk.word_tokenize(text)
        tokens = [token.strip() for token in tokens]

        # Lemmatize the tokens
        lemmatizer = nltk.stem.WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

        # Join the tokens back into a string
        return " ".join(tokens)

    def extract_text(self, cv_path):
        """
        Extract text from .pdf, .docx, and .doc files.
        """
        file_extension = os.path.splitext(cv_path)[1].lower()
        text = ""

        if file_extension == ".pdf":
            text = self._extract_from_pdf(cv_path)
        elif file_extension == ".docx":
            text = self._extract_from_docx(cv_path)
        elif file_extension == ".doc":
            text = self._extract_from_doc(cv_path)
        else:
            self.log.error(f"Unsupported file format: {cv_path}")
            raise ValueError(f"Unsupported file format: {file_extension}")

        return self.preprocess_text(text) if self.preprocess else text

    def _extract_from_pdf(self, cv_path):
        text = ""
        try:
            with open(cv_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            self.log.exception(f"Error reading PDF {cv_path}: {e}", exc_info=True)
        return text

    def _extract_from_docx(self, cv_path):
        text = ""
        try:
            doc = Document(cv_path)
            text = "\n".join([paragraph.text.strip() for paragraph in doc.paragraphs])
        except Exception as e:
            self.log.exception(f"Error reading DOCX {cv_path}: {e}", exc_info=True)
        return text

    def _extract_from_doc(self, cv_path):
        text = ""
        try:
            doc = SpireDoc(cv_path)
            text = doc.GetText()
            part_a, part_b = text.split("Evaluation Warning: The document was created with Spire.Doc for Python.")
            return part_a + " " + part_b
        except Exception as e:
            self.log.exception(f"Error reading DOC {cv_path}: {e}", exc_info=True)
        return text

    def find_cvs(self, directory):
        """
        Finds all CV files (PDF, DOC, DOCX) in the directory.
        """
        cv_files = []
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isdir(file_path):
                    cv_files.extend(self.find_cvs(file_path))
                elif filename.lower().endswith((".pdf", ".docx", ".doc")):
                    cv_files.append(file_path)
        except Exception as e:
            self.log.exception(f"Error finding CVs in directory {directory}: {e}", exc_info=True)
        return cv_files

    def process_bulk_cvs(self, directory, zip_file=False):
        """
        Reads and extracts text from multiple CV files in a given directory or ZIP file.

        Returns an array of texts for all CVs.
        """
        # Handle ZIP file extraction
        if zip_file:
            try:
                with zipfile.ZipFile(directory, 'r') as zip_ref:
                    temp_dir = os.path.join(os.getcwd(), '.temp_extract')
                    os.makedirs(temp_dir, exist_ok=True)
                    zip_ref.extractall(temp_dir)
                    directory = temp_dir
            except Exception as e:
                self.log.exception(f"Error extracting ZIP file: {e}", exc_info=True)
                return []

        # Find all CVs in the directory
        cv_files = self.find_cvs(directory)
        all_texts = []

        # Extract text from each CV
        for cv_file in cv_files:
            text = self.extract_text(cv_file)
            all_texts.append(text)

        return all_texts
