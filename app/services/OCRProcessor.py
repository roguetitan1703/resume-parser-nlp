import pytesseract
from pdf2image import convert_from_path
import os

class OCRProcessor:
    def __init__(self, temp_dir="temp"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def pdf_to_text(self, pdf_path):
        # Convert PDF to images
        pages = convert_from_path(pdf_path)
        text = ""
        for i, page in enumerate(pages):
            image_path = f"{self.temp_dir}/page_{i}.png"
            page.save(image_path, "PNG")
            # Extract text using pytesseract
            text += pytesseract.image_to_string(image_path)
            os.remove(image_path)
        return text
