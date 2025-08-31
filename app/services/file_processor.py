# app/services/file_processor.py
import logging
import os
import numpy as np
import pdfplumber
from typing import cast
import torch
from doctr.io import Document as DocTRDocument
from doctr.models import ocr_predictor
from docx import Document
from pdf2image import convert_from_path
from spellchecker import SpellChecker
from PIL import Image
from PIL.Image import Image as ImageType 
import io
import asyncio
from app.core.config import settings
from app.core.utils import log_timing
from app.services.database import update_file_status
from app.services.vector_db import create_and_save_faiss_index

global_doctr_model = None

logging.basicConfig(level=logging.INFO)

# function to check quality of text
def is_text_quality_good(text):
    """
    Checks if the extracted text has a good linguistic quality.
    """
    if not text or len(text.strip()) < 100:
        return False

    spell = SpellChecker()
    words = text.split()
    misspelled = spell.unknown(words)

    if len(misspelled) / len(words) > 0.15:
        return False

    return True

# Extract text from PDF using pdfplumber
def extract_text_with_pdfplumber(pdf_path):
    extracted_text = ""
    try:
        logging.info(
            f"🔍 Extracting text from PDF with pdfplumber: {os.path.basename(pdf_path)}"
        )
        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_text += page_text.strip() + "\n"
                else:
                    logging.warning(f"⚠️ Blank or unreadable page: {page_idx + 1}")
    except Exception as e:
        logging.error(
            f"❌ Error with pdfplumber for '{os.path.basename(pdf_path)}': {e}"
        )
        extracted_text = ""
    return extracted_text

# Extract text from PDF using DocTR
def extract_text_from_pdf_with_doctr(pdf_path):
    global global_doctr_model
    if not global_doctr_model:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using {device} for DocTR.")
        global_doctr_model = ocr_predictor(
            det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True
        ).to(device)

    try:
        logging.info(
            f" OCR processing with DocTR for '{os.path.basename(pdf_path)}'..."
        )
        images_pil = convert_from_path(pdf_path, dpi=300)
        all_pages_np = [np.array(img) for img in images_pil]
        result = global_doctr_model(all_pages_np)

        extracted_text = ""
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join([word.value for word in line.words])
                    extracted_text += line_text + "\n"
        return extracted_text

    except Exception as e:
        logging.error(f"An error occurred during DocTR processing: {e}")
        return ""

# Main extraction function
async def extract_text_from_file(file_path: str):
    file_extension = os.path.splitext(file_path)[1].lower()
    text_content = ""
    if file_extension in [".jpg", ".jpeg", ".png"]:
        try:
            image_obj = Image.open(file_path)
            image = cast(ImageType, image_obj)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
                
            pdf_bytes = io.BytesIO()
            image.save(pdf_bytes, "PDF", resolution=100.0)
            pdf_bytes.seek(0)
            temp_pdf_path = os.path.join(os.path.dirname(file_path), f"{os.path.splitext(os.path.basename(file_path))[0]}.pdf")
            image.save(temp_pdf_path, "PDF", resolution=100.0)

            pdfplumber_text = extract_text_with_pdfplumber(temp_pdf_path)
            # Check the quality of the extracted text
            if pdfplumber_text and is_text_quality_good(pdfplumber_text):
                text_content = pdfplumber_text
                logging.info("Image to PDF conversion and PDF Plumber extraction succeeded.")
            else:
                logging.info("PDF Plumber text quality is poor, falling back to DocTR OCR.")
                text_content = extract_text_from_pdf_with_doctr(temp_pdf_path)
            os.remove(temp_pdf_path) 

        except Exception as e:
            logging.error(f"Error processing image file: {e}")
            return None
    
    elif file_extension == ".pdf":
        pdfplumber_text = extract_text_with_pdfplumber(file_path)

        if pdfplumber_text and is_text_quality_good(pdfplumber_text):
            text_content = pdfplumber_text
            logging.info("PDF Plumber extraction succeeded.")
        else:
            logging.info("PDF Plumber text quality is poor, falling back to DocTR OCR.")
            text_content = extract_text_from_pdf_with_doctr(file_path)

    elif file_extension == ".docx":
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
        except Exception as e:
            logging.error(f"Error extracting text from DOCX: {e}")
            return None

    elif file_extension == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
        except Exception as e:
            logging.error(f"Error reading TXT file: {e}")
            return None

    else:
        return None

    return text_content


@log_timing
async def process_file_pipeline(file_path: str, file_name: str, file_id: str):
    try:
        # Update status before starting extraction
        update_file_status(file_id, file_name, "Extracting")
        
        logging.info(f"Starting extraction for {file_id}")
        await asyncio.sleep(3)# Add a 3-second delay for demonstration

        text_content = await extract_text_from_file(file_path)
        if not text_content:
            update_file_status(file_id, file_name, "Failed")
            return
        file_name_without_ext = os.path.splitext(file_name)[0]
        extracted_text_dir = "extracted_text"
        os.makedirs(extracted_text_dir, exist_ok=True)
        text_file_path = os.path.join(extracted_text_dir, f"{file_name_without_ext}.txt")
        
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        logging.info(f"Extracted text saved to {text_file_path}")
        
        
        # Update status before chunking/embedding
        update_file_status(file_id, file_name, "Chunking/Embedding")
        logging.info(f"Starting chunking/embedding for {file_id}")
        await asyncio.sleep(3) # Add another 3-second delay

        create_and_save_faiss_index(text_content, file_name, file_id, settings.FAISS_INDEX_DIR)
        
        # Update status after indexing
        update_file_status(file_id, file_name, "Indexed")

    except Exception as e:
        update_file_status(file_id, file_name, "Failed")
        logging.error(f"Ingestion pipeline failed for {file_id}: {e}")