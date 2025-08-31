# app/api/endpoints/upload.py
import os
import shutil
import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.core.config import settings
from app.services.file_processor import process_file_pipeline

router = APIRouter()


# Upload a file for ingestion
@router.post("/api/upload", summary="Upload a file for ingestion")
async def upload_file(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    
    file_id = str(uuid.uuid4())
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename not provided.")
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_extension}")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Trigger the background task for processing
        background_tasks.add_task(
            process_file_pipeline, file_path, file.filename, file_id
        )

        return {"status": "Uploaded", "file_id": file_id, "file_name": file.filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
