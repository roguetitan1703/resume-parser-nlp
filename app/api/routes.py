from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import uuid
from pathlib import Path
from services import Scraper
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
    Handle file upload, process it, and return the processed Excel file.
    """
    try:
        # Generate a unique filename and save the uploaded file
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file using the Scraper class
        CVscraper = Scraper(log_file="main.log")
        extract_data = CVscraper.read_and_extract_from_cvs(file_path, zip_file=True)

        if extract_data['status'] == 'error':
            raise HTTPException(status_code=400, detail=extract_data['message'])

        # Get the path to the generated Excel file
        excel_file = extract_data.get("excel_file")
        if not excel_file or not os.path.exists(excel_file):
            raise HTTPException(status_code=404, detail="Excel file not found after processing")

        # Prepare headers for file download
        headers = {
            "Content-Disposition": f"attachment; filename=output.xlsx"
        }

        # Return the generated Excel file as a response
        return FileResponse(excel_file, headers=headers, media_type="routerlication/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Clean up the uploaded file to avoid storage overload
        if os.path.exists(file_path):
            os.remove(file_path)
