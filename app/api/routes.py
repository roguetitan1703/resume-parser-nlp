from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import uuid
from pathlib import Path
from services import Scraper, OCRProcessor, ResumeProcessor, NERProcessor

from ultra_logger import Logger  # Assuming you're using ultra_logger
# Initialize logger
logger = Logger(log_file="resume_processing.log", log_name="Resume processing")  # Example logger
ner_processor = NERProcessor(logger, save_to_mongo= False)

ner = True
ocr = False

resume_processor = ResumeProcessor(logger) if not ocr else OCRProcessor(logger)  # Initialize the ResumeProcessor
# Setting up the router
router = APIRouter()

# Mount the static directory correctly
router.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Root directory for uploads and processed files
UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)


@router.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    """
    Serve the homepage (index.html).
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/extract_data")
async def extract_data(file: UploadFile):
    """
    Handle file upload, process it, and return extracted resume data or download file.
    """
    try:
        # Generate a unique filename and save the uploaded file
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Extract text from the resume using the ResumeProcessor class
        if file_extension.lower() in ['.pdf', '.doc', '.docx']:
            text = resume_processor.extract_text(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF, DOC, and DOCX are supported.")
        
        # return {
        #         "status": "success",
        #         "data": text
        #     }
        
        # Step 2: Process the resume using NERProcessor
        if ner:
                
            entities = ner_processor.process_resume(text)

            # Return the extracted entities as a JSON response
            return {
                "status": "success",
                "data": entities,
                "text": text
            }
    
        else:
            return text
        # Optional steps for further processing (commented out for now)
        # Step 2: Preprocess the extracted text
        # preprocessed_text = preprocess_text(text)


        # Step 3: Extract key entities using NER
        # entities = extract_entities(preprocessed_text)

        # Step 4: Structure the extracted data (name, education, skills, etc.)
        # structured_data = ResumeParser.structure_resume_data(entities)

        # Optional: Save the structured data to a database, or return directly
        # save_to_database(structured_data)

        # Return the extracted resume text as a JSON response

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)