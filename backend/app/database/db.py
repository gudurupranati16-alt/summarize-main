from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime  # pyrefly: ignore[missing-import]
from sqlalchemy.orm import declarative_base  # pyrefly: ignore[missing-import]
from sqlalchemy.orm import sessionmaker  # pyrefly: ignore[missing-import]
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./news.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PDFDocument(Base):
    __tablename__ = "pdf_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, unique=True, nullable=False)
    file_size = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    pdf_id = Column(Integer, nullable=False)
    summary_text = Column(Text, nullable=False)
    sentiment = Column(String, nullable=True)
    sentiment_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)