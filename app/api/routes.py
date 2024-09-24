from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bson import ObjectId
import os
import shutil
import uuid
from pathlib import Path
from services import Scraper, OCRProcessor, ResumeProcessor, NERProcessor

from ultra_logger import Logger  # Assuming you're using ultra_logger
# Initialize logger
logger = Logger(log_file="resume_processing.log", log_name="Resume processing")  # Example logger
ner_processor = NERProcessor(logger)

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

@router.get("/filtering_window", response_class=HTMLResponse)
async def get_filtering_window(request: Request):
    """
    Serve the filtering page (filter_window.html).
    """
    return templates.TemplateResponse("filter_window.html", {"request": request})

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
                
            entities = ner_processor.extract_all_entities(text)

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
            
@router.post("/analyze_resumes")
async def bulk_extract_data(file: UploadFile, request: Request):
    try:
        
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        extract_data = resume_processor.process_bulk_cvs(file_path, zip_file=True)
        
        all_entities, record = ner_processor.bulk_extract_all_entities(extract_data)

        def serialize_mongo_id(entity):
            if isinstance(entity, ObjectId):
                return str(entity)
            if isinstance(entity, dict):
                return {k: serialize_mongo_id(v) for k, v in entity.items()}
            elif isinstance(entity, list):
                return [serialize_mongo_id(i) for i in entity]
            return entity
        
        collection_name = ner_processor.bulk_save_to_mongo(serialize_mongo_id(all_entities))
        
        # Render the filter_window.html template and pass collection_name
        return templates.TemplateResponse("filter_window.html", {
            "request": request,  # Required by Jinja2Templates
            "collection_name": collection_name  # Pass collection_name to the template
        })

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/get_resume_data")
async def get_resume_data(collection: str):
    try:
        # Fetch data from MongoDB based on the collection name
        data = ner_processor.fetch_data_from_mongo(collection)
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
 
# @router.post("/extract_data_depreceated")
# async def extract_data_depreceated(file: UploadFile):
#     """
#     Handle file upload, process it, and return the processed Excel file.
#     """
#     try:
#         # Generate a unique filename and save the uploaded file
#         file_extension = os.path.splitext(file.filename)[1]
#         unique_filename = f"{uuid.uuid4()}{file_extension}"
#         file_path = os.path.join(UPLOAD_DIR, unique_filename)

#         # Save the uploaded file
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
        
#         # Process the file using the Scraper class
#         CVscraper = Scraper(log_file="main.log")
#         extract_data = CVscraper.read_and_extract_from_cvs(file_path, zip_file=True)

#         if extract_data['status'] == 'error':
#             raise HTTPException(status_code=400, detail=extract_data['message'])

#         # Get the path to the generated Excel file
#         excel_file = extract_data.get("excel_file")
#         if not excel_file or not os.path.exists(excel_file):
#             raise HTTPException(status_code=404, detail="Excel file not found after processing")

#         # Prepare headers for file download
#         headers = {
#             "Content-Disposition": f"attachment; filename=output.xlsx"
#         }

#         # Return the generated Excel file as a response
#         return FileResponse(excel_file, headers=headers, media_type="routerlication/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
#     finally:
#         # Clean up the uploaded file to avoid storage overload
#         if os.path.exists(file_path):
#             os.remove(file_path)
