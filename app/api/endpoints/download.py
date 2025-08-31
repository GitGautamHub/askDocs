# app/api/endpoints/download.py
import os
import shutil
import tempfile
from docx import Document
from PIL import Image
from PIL.Image import Image as ImageType
from typing import cast

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.services.database import delete_file_entry

router = APIRouter()


def convert_to_pdf(file_path: str, file_extension: str):
    """
    Converts various file types (DOCX, JPG, PNG, TXT) to a temporary PDF file.
    This is necessary for the frontend PDF viewer.
    """
    temp_dir = tempfile.gettempdir()
    temp_pdf_path = os.path.join(temp_dir, f"temp_{os.path.basename(file_path)}.pdf")

    if file_extension == ".docx":
        try:
            doc = Document(file_path)
            with open(temp_pdf_path, 'w', encoding='utf-8') as f:
                for para in doc.paragraphs:
                    f.write(para.text + '\n')
            return temp_pdf_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting DOCX to PDF: {e}")

    elif file_extension in [".jpg", ".jpeg", ".png"]:
        try:
            image_obj = Image.open(file_path)
            image = cast(ImageType, image_obj)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(temp_pdf_path, "PDF")
            return temp_pdf_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting image to PDF: {e}")

    elif file_extension == ".txt":
        try:
            with open(file_path, 'r', encoding='utf-8') as f_in, open(temp_pdf_path, 'w', encoding='utf-8') as f_out:
                shutil.copyfileobj(f_in, f_out)
            return temp_pdf_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting TXT to PDF: {e}")

    return None


@router.get("/api/download/{file_id}", summary="Download a document for viewing")
async def download_file(file_id: str):
    """
    Serves a document file. If the file is not a PDF, it converts it to a temporary PDF on the fly.
    """
    found_file = None
    for filename in os.listdir(settings.UPLOAD_DIR):
        if filename.startswith(file_id):
            found_file = filename
            break

    if not found_file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(settings.UPLOAD_DIR, found_file)
    file_extension = os.path.splitext(found_file)[1].lower()

    if file_extension == ".pdf":
        return FileResponse(path=file_path, filename=found_file)
    else:
        temp_pdf_path = convert_to_pdf(file_path, file_extension)
        if temp_pdf_path:
            return FileResponse(path=temp_pdf_path, filename=f"{os.path.splitext(found_file)[0]}.pdf", media_type="application/pdf")
        else:
            raise HTTPException(status_code=500, detail="Could not convert file to PDF.")


@router.delete("/api/documents/{file_id}", summary="Delete a document and its index")
async def delete_document(file_id: str):
    """
    Deletes an uploaded document, its associated FAISS index, and the database entry.
    """
    try:
        # Delete the file from the uploads directory
        found_file = None
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.startswith(file_id):
                found_file = filename
                os.remove(os.path.join(settings.UPLOAD_DIR, found_file))
                break

        # Delete the FAISS index file
        index_file_path = os.path.join(settings.FAISS_INDEX_DIR, f"{file_id}.faiss")
        if os.path.exists(index_file_path):
            os.remove(index_file_path)

        # Delete the database entry
        delete_file_entry(file_id)

        return {"message": f"Document {file_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")