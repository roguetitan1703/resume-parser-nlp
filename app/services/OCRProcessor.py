import os
import pytesseract
from pdf2image import convert_from_path
from docx2pdf import convert as docx2pdf_convert
import re
from PIL import Image
import logging

class OCRProcessor:
    def __init__(self, logger, temp_dir="temp"):
        """
        Initializes the OCRProcessor with a logger and a temporary directory for storing intermediate files.
        
        :param logger: Logger instance to log information.
        :param temp_dir: Directory to store temporary images and converted PDFs.
        """
        self.log = logger
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def pdf_to_text(self, pdf_path):
        """
        Extracts text from a PDF file using OCR.
        
        :param pdf_path: Path to the PDF file.
        :return: Extracted text as a string.
        """
        self.log.info(f"Extracting text from PDF: {pdf_path}")
        try:
            # Convert PDF pages to images
            pages = convert_from_path(pdf_path, dpi=300, fmt='png', output_folder=self.temp_dir, thread_count=4)
            text = ""
            for i, page in enumerate(pages):
                image_path = os.path.join(self.temp_dir, f"page_{i}.png")
                page.save(image_path, "PNG")
                self.log.debug(f"Saved page {i} as image: {image_path}")
                # Perform OCR on the image
                extracted_text = pytesseract.image_to_string(Image.open(image_path))
                self.log.debug(f"Extracted text from page {i}: {extracted_text[:100]}...")  # Log first 100 chars
                text += extracted_text + "\n"
                # Remove the temporary image
                os.remove(image_path)
                self.log.debug(f"Removed temporary image: {image_path}")
            return text
        except Exception as e:
            self.log.error(f"Error extracting text from PDF: {e}")
            raise e

    def docx_to_text(self, docx_path):
        """
        Extracts text from a DOCX file by converting it to PDF first and then using OCR.
        
        :param docx_path: Path to the DOCX file.
        :return: Extracted text as a string.
        """
        self.log.info(f"Extracting text from DOCX: {docx_path}")
        try:
            # Convert DOCX to PDF
            pdf_path = os.path.join(self.temp_dir, f"{os.path.splitext(os.path.basename(docx_path))[0]}.pdf")
            docx2pdf_convert(docx_path, pdf_path)
            self.log.debug(f"Converted DOCX to PDF: {pdf_path}")
            # Use PDF to text extraction
            text = self.pdf_to_text(pdf_path)
            # Remove the temporary PDF
            os.remove(pdf_path)
            self.log.debug(f"Removed temporary PDF: {pdf_path}")
            return text
        except Exception as e:
            self.log.error(f"Error extracting text from DOCX: {e}")
            raise e

    def doc_to_text(self, doc_path):
        """
        Extracts text from a DOC file by converting it to PDF first and then using OCR.
        
        :param doc_path: Path to the DOC file.
        :return: Extracted text as a string.
        """
        self.log.info(f"Extracting text from DOC: {doc_path}")
        try:
            # Convert DOC to PDF using docx2pdf (requires LibreOffice on macOS/Linux)
            pdf_path = os.path.join(self.temp_dir, f"{os.path.splitext(os.path.basename(doc_path))[0]}.pdf")
            docx2pdf_convert(doc_path, pdf_path)
            self.log.debug(f"Converted DOC to PDF: {pdf_path}")
            # Use PDF to text extraction
            text = self.pdf_to_text(pdf_path)
            # Remove the temporary PDF
            os.remove(pdf_path)
            self.log.debug(f"Removed temporary PDF: {pdf_path}")
            return text
        except Exception as e:
            self.log.error(f"Error extracting text from DOC: {e}")
            raise e

    def extract_text(self, file_path):
        """
        Extracts text from .pdf, .docx, and .doc files using OCR.
        
        :param file_path: Path to the file.
        :return: Extracted text as a string.
        """
        self.log.info(f"Starting text extraction for file: {file_path}")
        file_extension = os.path.splitext(file_path)[1].lower()
        text = ""

        if file_extension == ".pdf":
            text = self.pdf_to_text(file_path)
        elif file_extension == ".docx":
            text = self.docx_to_text(file_path)
        elif file_extension == ".doc":
            text = self.doc_to_text(file_path)
        else:
            self.log.error(f"Unsupported file format: {file_path}")
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Clean up the text if needed
        text = self.postprocess_text(text)
        self.log.info(f"Completed text extraction for file: {file_path}")
        return text

    def postprocess_text(self, text):
        """
        Post-processes the extracted text to clean it up.
        
        :param text: Raw extracted text.
        :return: Cleaned text.
        """
        self.log.debug("Starting post-processing of extracted text.")
        # Replace multiple newlines with double newlines to preserve paragraph breaks
        text = re.sub(r'\n{2,}', '\n\n', text)
        # Replace single newlines with a space to avoid merging paragraphs
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        # Optionally, remove unwanted characters or perform other cleaning steps
        text = text.strip()
        self.log.debug(f"Post-processed text: {text[:100]}...")  # Log first 100 chars
        return text

# Example Usage
if __name__ == "__main__":
    import logging

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("OCRProcessor")

    # Initialize OCRProcessor with the logger
    ocr_processor = OCRProcessor(logger, temp_dir="temp")

    # Paths to your files
    pdf_path = "sample.pdf"
    docx_path = "sample.docx"
    doc_path = "sample.doc"

    # Extract text
    try:
        pdf_text = ocr_processor.extract_text(pdf_path)
        print(f"Extracted PDF Text:\n{pdf_text[:500]}...\n")  # Print first 500 chars

        docx_text = ocr_processor.extract_text(docx_path)
        print(f"Extracted DOCX Text:\n{docx_text[:500]}...\n")  # Print first 500 chars

        doc_text = ocr_processor.extract_text(doc_path)
        print(f"Extracted DOC Text:\n{doc_text[:500]}...\n")  # Print first 500 chars
    except Exception as e:
        logger.error(f"An error occurred during text extraction: {e}")
