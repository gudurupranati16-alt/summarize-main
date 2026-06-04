import os
import hashlib
import fitz  # pyrefly: ignore[missing-import]
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException  # pyrefly: ignore[missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore[missing-import]
from app.database.db import SessionLocal, PDFDocument, Summary  # pyrefly: ignore[missing-import]
from app.schemas.summary import PDFUploadResponse, SummaryHistoryItem  # pyrefly: ignore[missing-import]
from cerebras_service import generate_summary  # pyrefly: ignore[missing-import]

router = APIRouter()

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 20 * 1024 * 1024

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            extracted = page.get_text()
            if extracted:
                text += extracted
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")


def validate_file(content: bytes) -> None:
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit"
        )


def get_or_create_pdf_document(db: Session, file_hash: str, file_path: str,
                                filename: str, content: bytes, text_content: str) -> PDFDocument:
    existing = db.query(PDFDocument).filter(PDFDocument.file_hash == file_hash).first()
    if existing:
        return existing

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


async def process_pdfs(files: list[UploadFile], db: Session) -> PDFUploadResponse:
    """Core logic shared by both /summarize and /summarize-pdfs."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    contents, filenames, individual_hashes = [], [], []
    total_size = 0

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"'{file.filename}' is not a PDF.")
        content = await file.read()
        validate_file(content)
        individual_hashes.append(calculate_file_hash(content))
        contents.append(content)
        filenames.append(file.filename)
        total_size += len(content)

    # Sort for deterministic hashing
    sorted_indices = sorted(range(len(files)), key=lambda k: filenames[k])
    sorted_contents = [contents[i] for i in sorted_indices]
    sorted_filenames = [filenames[i] for i in sorted_indices]
    sorted_hashes = [individual_hashes[i] for i in sorted_indices]

    combined_hash = calculate_file_hash("".join(sorted_hashes).encode("utf-8"))

    # Return cached summary if exists
    existing_summary = db.query(Summary).join(
        PDFDocument, Summary.pdf_id == PDFDocument.id
    ).filter(PDFDocument.file_hash == combined_hash).first()

    if existing_summary:
        pdf = db.query(PDFDocument).filter(PDFDocument.id == existing_summary.pdf_id).first()
        return PDFUploadResponse(
            pdf_id=pdf.id,
            filename=pdf.filename,
            file_size=pdf.file_size,
            upload_date=pdf.upload_date,
            summary=existing_summary.summary_text,
            sentiment=existing_summary.sentiment or "Neutral",
            sentiment_explanation=existing_summary.sentiment_explanation or ""
        )

    # Extract text and save files
    extracted_texts, saved_paths = [], []

    for content, filename, indiv_hash in zip(sorted_contents, sorted_filenames, sorted_hashes):
        file_path = os.path.join(UPLOAD_DIR, f"{indiv_hash}_{filename}")
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(content)
        saved_paths.append(file_path)

        text = extract_text_from_pdf_bytes(content)
        if text.strip():
            extracted_texts.append(f"--- Document: {filename} ---\n{text.strip()}")

    if not extracted_texts:
        raise HTTPException(status_code=400, detail="No readable text found in the uploaded PDF(s).")

    combined_text = "\n\n".join(extracted_texts)
    combined_filename = ", ".join(sorted_filenames)
    combined_filepath = ", ".join(saved_paths)

    pdf_doc = get_or_create_pdf_document(
        db, combined_hash, combined_filepath, combined_filename,
        b"".join(sorted_contents), combined_text
    )

    # Generate summary + sentiment
    result = generate_summary(combined_text)
    summary_text = result.get("summary", "")
    sentiment = result.get("sentiment", "Neutral")
    sentiment_explanation = result.get("sentiment_explanation", "")

    if not summary_text:
        raise HTTPException(status_code=500, detail="Failed to generate summary.")

    summary = Summary(
        pdf_id=pdf_doc.id,
        summary_text=summary_text,
        sentiment=sentiment,
        sentiment_explanation=sentiment_explanation
    )
    db.add(summary)
    db.commit()

    return PDFUploadResponse(
        pdf_id=pdf_doc.id,
        filename=combined_filename,
        file_size=total_size,
        upload_date=pdf_doc.upload_date,
        summary=summary_text,
        sentiment=sentiment,
        sentiment_explanation=sentiment_explanation
    )


@router.post("/summarize", response_model=PDFUploadResponse)
async def summarize_pdf(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    try:
        return await process_pdfs(files, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/summarize-pdfs", response_model=PDFUploadResponse)
async def summarize_pdfs(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    try:
        return await process_pdfs(files, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/summaries", response_model=list[SummaryHistoryItem])
def get_summaries(db: Session = Depends(get_db)):
    try:
        summaries = db.query(Summary).join(
            PDFDocument, Summary.pdf_id == PDFDocument.id
        ).all()

        result = []
        for s in summaries:
            pdf = db.query(PDFDocument).filter(PDFDocument.id == s.pdf_id).first()
            result.append(SummaryHistoryItem(
                id=s.id,
                pdf_id=s.pdf_id,
                filename=pdf.filename if pdf else "Unknown",
                summary_text=s.summary_text,
                sentiment=s.sentiment,
                sentiment_explanation=s.sentiment_explanation,
                created_at=s.created_at
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summaries: {str(e)}")