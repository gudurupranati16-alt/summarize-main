from pydantic import BaseModel  # pyrefly: ignore[missing-import]
from datetime import datetime
from typing import Optional


class PDFUploadResponse(BaseModel):
    pdf_id: int
    filename: str
    file_size: int
    upload_date: datetime
    summary: str
    sentiment: Optional[str] = "Neutral"
    sentiment_explanation: Optional[str] = ""


class SummaryHistoryItem(BaseModel):
    id: int
    pdf_id: int
    filename: str
    summary_text: str
    sentiment: Optional[str] = None
    sentiment_explanation: Optional[str] = None
    created_at: datetime