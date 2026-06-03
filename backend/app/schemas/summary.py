from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SummaryRequest(BaseModel):
    company: Optional[str] = None


class Article(BaseModel):
    title: str
    description: str


class SummaryResponse(BaseModel):
    company: Optional[str] = None
    summary: list[str]
    articles: list[Article]


class PDFUploadResponse(BaseModel):
    pdf_id: int
    filename: str
    file_size: int
    upload_date: datetime
    summary: str


class SummaryHistoryItem(BaseModel):
    id: int
    pdf_id: int
    filename: str
    summary_text: str
    created_at: datetime

    class Config:
        from_attributes = True