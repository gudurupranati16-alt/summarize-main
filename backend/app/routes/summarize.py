import os
import hashlib
import pdfplumber
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import SessionLocal, PDFDocument, Summary
from app.schemas.summary import PDFUploadResponse, SummaryHistoryItem
from app.utils.cerebras_client import get_cerebras_client

router = APIRouter()

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# Create uploads directory if it doesn't exist
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


@router.post("/summarize", response_model=PDFUploadResponse)
async def summarize_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF file and generate a summary using Cerebras API.
    
    Returns:
        PDFUploadResponse with pdf_id, filename, file_size, upload_date, and summary
    """
    try:
        # Validate file type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # Calculate file hash
        file_hash = calculate_file_hash(content)

        # Check if same PDF already exists
        existing_pdf = db.query(PDFDocument).filter(
            PDFDocument.file_hash == file_hash
        ).first()

        if existing_pdf:
            # Return cached summary if available
            existing_summary = db.query(Summary).filter(
                Summary.pdf_id == existing_pdf.id
            ).first()
            
            if existing_summary:
                return PDFUploadResponse(
                    pdf_id=existing_pdf.id,
                    filename=existing_pdf.filename,
                    file_size=existing_pdf.file_size,
                    upload_date=existing_pdf.upload_date,
                    summary=existing_summary.summary_text
                )

        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, f"{file_hash}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)

        # Extract text from PDF
        text_content = extract_text_from_pdf(file_path)

        if not text_content.strip():
            raise HTTPException(status_code=400, detail="PDF appears to be empty or unreadable")

        # Create PDF document record
        pdf_doc = PDFDocument(
            filename=file.filename,
            file_path=file_path,
            file_hash=file_hash,
            file_size=len(content),
            text_content=text_content
        )
        db.add(pdf_doc)
        db.commit()
        db.refresh(pdf_doc)

        # Generate summary using Cerebras
        cerebras_client = get_cerebras_client()
        summary_text = cerebras_client.summarize(text_content)

        if not summary_text:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate summary from Cerebras API"
            )

        # Save summary to database
        summary = Summary(
            pdf_id=pdf_doc.id,
            summary_text=summary_text
        )
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
    """
    Retrieve all stored summaries with their associated PDF information.
    """
    try:
        summaries = db.query(
            Summary.id,
            Summary.pdf_id,
            PDFDocument.filename,
            Summary.summary_text,
            Summary.created_at
        ).join(
            PDFDocument,
            Summary.pdf_id == PDFDocument.id
        ).all()

        result = [
            SummaryHistoryItem(
                id=s[0],
                pdf_id=s[1],
                filename=s[2],
                summary_text=s[3],
                created_at=s[4]
            )
            for s in summaries
        ]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summaries: {str(e)}")