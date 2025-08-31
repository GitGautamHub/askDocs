# app/api/endpoints/status.py
from fastapi import APIRouter, HTTPException

from app.services.database import get_file_status, get_all_documents

router = APIRouter()

# Get the processing status of a file
@router.get("/api/status/{file_id}", summary="Get the processing status of a file")
async def get_status(file_id: str):
    status = get_file_status(file_id)
    if status is None:
        raise HTTPException(status_code=404, detail="File ID not found.")
    return {"status": status}

# Get a list of all uploaded documents
@router.get("/api/documents", summary="Get a list of all uploaded documents")
async def get_documents_list():
    documents = get_all_documents()
    return {"documents": documents}