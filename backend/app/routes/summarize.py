import os
import hashlib
import pdfplumber
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database.db import SessionLocal, PDFDocument, Summary
from app.schemas.summary import PDFUploadResponse, SummaryHistoryItem
from app.utils.cerebras_client import get_cerebras_client

router = APIRouter()

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_CONTENT_TYPE = "application/pdf"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")


def validate_file(file: UploadFile, content: bytes) -> None:
    """Validate file type and size."""
    if file.content_type != ALLOWED_CONTENT_TYPE:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / 1024 / 1024}MB"
        )


def get_or_create_pdf_document(db: Session, file_hash: str, file_path: str, 
                               filename: str, content: bytes, text_content: str) -> PDFDocument:
    """Get existing PDF or create new one."""
    existing_pdf = db.query(PDFDocument).filter(
        PDFDocument.file_hash == file_hash
    ).first()
    
    if existing_pdf:
        return existing_pdf
    
    pdf_doc = PDFDocument(
        filename=filename,
        file_path=file_path,
        file_hash=file_hash,
        file_size=len(content),
        text_content=text_content
    )
    db.add(pdf_doc)
    db.commit()
    db.refresh(pdf_doc)
    return pdf_doc


@router.post("/summarize", response_model=PDFUploadResponse)
async def summarize_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF file and generate a summary using Cerebras API."""
    try:
        content = await file.read()
        validate_file(file, content)

        file_hash = calculate_file_hash(content)

        existing_summary = db.query(Summary).join(
            PDFDocument, 
            Summary.pdf_id == PDFDocument.id
        ).filter(PDFDocument.file_hash == file_hash).first()
        
        if existing_summary:
            pdf = db.query(PDFDocument).filter(
                PDFDocument.id == existing_summary.pdf_id
            ).first()
            return PDFUploadResponse(
                pdf_id=pdf.id,
                filename=pdf.filename,
                file_size=pdf.file_size,
                upload_date=pdf.upload_date,
                summary=existing_summary.summary_text
            )

        file_path = os.path.join(UPLOAD_DIR, f"{file_hash}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)

        text_content = extract_text_from_pdf(file_path)

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="PDF appears to be empty or unreadable")

        pdf_doc = get_or_create_pdf_document(
            db, file_hash, file_path, file.filename, content, text_content
        )

        cerebras_client = get_cerebras_client()
        summary_text = cerebras_client.summarize(text_content)

        if not summary_text:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate summary from Cerebras API"
            )

        summary = Summary(pdf_id=pdf_doc.id, summary_text=summary_text)
        db.add(summary)
        db.commit()

        return PDFUploadResponse(
            pdf_id=pdf_doc.id,
            filename=file.filename,
            file_size=len(content),
            upload_date=pdf_doc.upload_date,
            summary=summary_text
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/summaries", response_model=list[SummaryHistoryItem])
def get_summaries(db: Session = Depends(get_db)):
    """Retrieve all stored summaries with their associated PDF information."""
    try:
        summaries = db.query(Summary).join(
            PDFDocument, Summary.pdf_id == PDFDocument.id
        ).all()

        return [
            SummaryHistoryItem(
                id=s.id,
                pdf_id=s.pdf_id,
                filename=db.query(PDFDocument).filter(PDFDocument.id == s.pdf_id).first().filename,
                summary_text=s.summary_text,
                created_at=s.created_at
            )
            for s in summaries
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summaries: {str(e)}")