# Resume Parsing System

## Description

This project is a Resume Parsing System built using FastAPI. It processes resumes in PDF, DOC, and DOCX formats, extracts text, and optionally performs further natural language processing (NLP) tasks such as named entity recognition (NER). The project leverages various libraries such as Spacy, PyPDF2, and python-docx for text extraction, along with a logging mechanism using UltraLogger.

## Project Structure

```bash
.
├── app
│   ├── api
│   │   ├── __init__.py
│   │   └── routes.py         # API routes defined here
│   ├── core
│   └── models
├── services
│   ├── __init__.py
│   ├── OCRProcessor.py       # (Optional, not used currently)
│   ├── ResumeParser.py       # Resume text extraction logic
│   └── scraper.py            # Scraper module (not in active use currently)
├── static                    # Static files such as CSS, JS
├── templates                 # Jinja2 HTML templates
│   └── index.html
├── tests                     # Unit tests (To be implemented)
├── main.py                   # FastAPI entry point
├── .gitignore
├── package.json              # Node.js packages (if any)
├── postcss.config.js
├── README.md                 # Documentation file
├── requirements.txt          # Python dependencies
├── resume_processing.log      # Log file for processing
├── tailwind.config.js
└── To-Do                     # To-Do list for the project

```

## Features

- **Resume Upload and Processing**: Upload resume files in PDF, DOC, or DOCX formats and extract their content as raw text.
- **File Handling**: Resumes are saved temporarily during the processing phase and deleted afterward to prevent storage overload.
- **Logging**: Errors and important events are logged using UltraLogger, with logs saved in `resume_processing.log`.
- **Text Extraction**: Utilizes PyPDF2, python-docx, and Spire.Doc libraries for extracting text from resumes in different formats.
- **Preprocessing (Optional)**: Functionality for preprocessing text and entity extraction using Spacy is available but not yet implemented in the routes.

## Dependencies

The project uses the following Python libraries and packages:

```txt
fastapi==0.110.1
uvicorn==0.29.0
PyPDF2==3.0.1
python-docx==1.1.0
Spire.Doc==12.3.2
spacy==3.7.6
pydantic==2.7.0
openpyxl==3.1.2
pdf2image==1.17.0
ultra_logger==0.1.2
```

You can install the dependencies using:

```bash
pip install -r requirements.txt
```

## How to Run

1. **Clone the Repository**:

```bash
git clone <repository-url>
cd <repository-directory>
```

2. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

3. **Run the FastAPI Application**:

```bash
uvicorn main:app --reload
```

4. **Access the API**:

Visit `http://127.0.0.1:8000` to upload resumes and extract text. The API allows file uploads and serves a simple HTML page (`index.html`).

## API Endpoints

- `GET /`: Serves the homepage (HTML form for uploading resumes).
- `POST /extract_data`: Handles the resume upload, processes the file, and returns the extracted text in JSON format.

## Example Request

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/extract_data' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@resume.pdf'
```

## Logging

Logs are written to `resume_processing.log`, capturing events such as file uploads, text extraction errors, and more.

## To-Do

- [ ] Add OCR processing for image-based resumes.
- [ ] Implement text preprocessing and entity extraction using Spacy.
- [ ] Add database support for saving structured resume data.
- [ ] Write unit tests for routes and services.
