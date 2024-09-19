import spacy
import os
from PyPDF2 import PdfReader
from docx import Document
from spire.doc import Document as SpireDoc

class ResumeProcessor:
    def __init__(self, logger):
        self.log = logger

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

        # Remove the /n
        text = text.replace("\n", " ")
        
        return text

    def _extract_from_pdf(self, cv_path):
        """
        Extract text from PDF files using PyPDF2.
        """
        text = ""
        try:
            self.log.info(f"Reading PDF: {cv_path}")
            with open(cv_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            self.log.exception(f"Error reading PDF {cv_path}: {e}", exc_info=True)
        return text

    def _extract_from_docx(self, cv_path):
        """
        Extract text from DOCX files using python-docx.
        """
        text = ""
        try:
            self.log.info(f"Reading DOCX: {cv_path}")
            doc = Document(cv_path)
            text = "\n".join([paragraph.text.strip() for paragraph in doc.paragraphs])
        except Exception as e:
            self.log.exception(f"Error reading DOCX {cv_path}: {e}", exc_info=True)
        return text

    def _extract_from_doc(self, cv_path):
        """
        Extract text from DOC files using Spire.Doc.
        """
        text = ""
        try:
            self.log.info(f"Reading DOC using Spire.Doc: {cv_path}")
            doc = SpireDoc(cv_path)
            text = doc.GetText()
        except Exception as e:
            self.log.exception(f"Error reading DOC {cv_path}: {e}", exc_info=True)
        return text

