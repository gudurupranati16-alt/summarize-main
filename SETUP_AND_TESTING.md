# PDF Summarization Application - Setup & Testing Guide

## Implementation Complete! ✅

Your PDF summarization application has been successfully implemented with the following structure:

### Backend (Python/FastAPI)
- ✅ PDF file upload endpoint with validation
- ✅ PDF text extraction using pdfplumber
- ✅ Cerebras AI integration for summarization
- ✅ SQLite database for storing PDFs and summaries
- ✅ Summary history retrieval endpoint
- ✅ Error handling and file size limits (20MB max)

### Frontend (React/Vite)
- ✅ Drag-and-drop file upload interface
- ✅ File validation and progress indication
- ✅ Summary display with expand/collapse
- ✅ Copy and download summary buttons
- ✅ Summary history with quick access
- ✅ Backend connection status indicator
- ✅ Responsive design for all screen sizes

---

## ⚠️ IMPORTANT: Cerebras API Setup

Before running the application, you MUST set up your Cerebras API key:

### Step 1: Get Your Cerebras API Key
1. Go to https://console.cerebras.ai
2. Sign up or log in to your account
3. Navigate to API keys section
4. Create a new API key
5. Copy the key

### Step 2: Configure the Backend
1. Open `backend/.env` file
2. Replace `your_cerebras_api_key_here` with your actual API key:
   ```
   CEREBRAS_API_KEY=your_actual_key_here
   ```
3. Save the file

⚠️ **Never commit the `.env` file to version control!** It contains sensitive API keys.

---

## Quick Start Guide

### 1. Start the Backend Server

**Windows (PowerShell):**
```powershell
cd "c:\Users\GUDURU PRANATI\OneDrive\Desktop\TECHM work\summarize\backend"
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. Start the Frontend Development Server

**In a new terminal (PowerShell):**
```powershell
cd "c:\Users\GUDURU PRANATI\OneDrive\Desktop\TECHM work\summarize\frontend"
npm run dev
```

**Expected output:**
```
Local:   http://localhost:5173/
```

### 3. Open the Application
- Visit: http://localhost:5173
- You should see the PDF Summarizer interface

---

## Testing the Application

### Test 1: Verify Backend Connection
1. The app should automatically check backend connection
2. If "Cannot connect to backend server" message appears:
   - Ensure backend is running on http://localhost:8000
   - Check for CORS issues in browser console
   - Verify firewall settings

### Test 2: Upload and Summarize a PDF
1. Click on the drop zone or drag a PDF file
2. Select any PDF from your computer (max 20MB)
3. Wait for processing (takes 10-30 seconds depending on PDF size)
4. View the generated summary in paragraph format
5. Test copy/download buttons

### Test 3: File Validation
Try these to test error handling:
- Upload a non-PDF file → should show error
- Upload a PDF > 20MB → should show size limit error
- Upload a password-protected PDF → should show extraction error
- Upload an empty/corrupted PDF → should show content error

### Test 4: Summary History
1. After uploading 2-3 PDFs, click "📚 Summary History"
2. Click on any previous summary to view it
3. Summary details should load correctly

---

## File Structure

```
backend/
├── .env                          # API configuration (⚠️ not committed)
├── .env.example                  # Example configuration
├── requirements.txt              # Python dependencies
├── uploads/                      # Uploaded PDF files stored here
├── news.db                        # SQLite database
└── app/
    ├── main.py                   # FastAPI application
    ├── database/
    │   └── db.py                 # Database models and connection
    ├── routes/
    │   └── summarize.py          # PDF upload and summary endpoints
    ├── schemas/
    │   └── summary.py            # Pydantic data models
    └── utils/
        └── cerebras_client.py    # Cerebras API client

frontend/
├── src/
│   ├── App.jsx                   # Main application component
│   ├── App.css                   # Application styles
│   ├── main.jsx                  # Entry point
│   ├── components/
│   │   ├── FileUpload.jsx        # File upload component
│   │   ├── FileUpload.css        # Upload styles
│   │   ├── SummaryDisplay.jsx    # Summary display component
│   │   └── SummaryDisplay.css    # Summary styles
│   └── services/
│       └── api.js                # API service for backend calls
├── package.json                  # NPM dependencies
└── vite.config.js               # Vite configuration
```

---

## API Endpoints

### Backend Endpoints

#### 1. Health Check
```
GET http://localhost:8000/health

Response:
{ "status": "healthy" }
```

#### 2. Upload PDF and Summarize
```
POST http://localhost:8000/summarize
Content-Type: multipart/form-data

Request:
- file: <PDF file>

Response:
{
  "pdf_id": 1,
  "filename": "document.pdf",
  "file_size": 102400,
  "upload_date": "2024-01-15T10:30:00",
  "summary": "Generated summary text..."
}
```

#### 3. Get Summary History
```
GET http://localhost:8000/summaries

Response:
[
  {
    "id": 1,
    "pdf_id": 1,
    "filename": "document.pdf",
    "summary_text": "Generated summary text...",
    "created_at": "2024-01-15T10:30:00"
  },
  ...
]
```

---

## Troubleshooting

### Issue: "CEREBRAS_API_KEY environment variable is not set"
**Solution:**
1. Check that `.env` file exists in backend directory
2. Verify API key is set: `echo %CEREBRAS_API_KEY%`
3. Restart the backend server after setting .env

### Issue: Backend returns 413 error (File too large)
**Solution:**
- Maximum file size is 20MB
- Split large PDFs into smaller chunks
- Use compression tools to reduce PDF size

### Issue: Backend returns 400 error (Failed to extract text)
**Causes:**
- PDF is scanned image (OCR required)
- PDF is password protected
- PDF is corrupted
**Solution:**
- Use a different PDF
- Remove password protection if possible
- For scanned PDFs, enable OCR (future enhancement)

### Issue: Summarization takes too long or times out
**Causes:**
- Large PDF (>10MB)
- Slow internet connection
- Cerebras API is slow
**Solution:**
- Try with smaller PDF first
- Check internet connection
- Check Cerebras API status: https://status.cerebras.ai

### Issue: CORS error in browser console
**Solution:**
1. Ensure backend CORS is enabled (should be in main.py)
2. Verify backend is running on http://localhost:8000
3. Clear browser cache and restart

### Issue: Frontend cannot connect to backend
**Checks:**
1. Is backend running? `netstat -ano | findstr :8000`
2. Check backend logs for errors
3. Try accessing http://localhost:8000/health directly
4. Check firewall settings

---

## Database

The application uses SQLite database (`news.db`) with two tables:

### PDFDocument Table
- `id`: Primary key
- `filename`: Original PDF filename
- `file_path`: Path to stored PDF file
- `file_hash`: SHA256 hash for duplicate detection
- `file_size`: Size in bytes
- `upload_date`: Timestamp
- `text_content`: Extracted PDF text

### Summary Table
- `id`: Primary key
- `pdf_id`: Foreign key to PDFDocument
- `summary_text`: Generated summary
- `created_at`: Timestamp

---

## Performance Notes

### Token Limits
- Cerebras gpt-oss-120b: ~200K context window
- Application limit: ~150K tokens for safety
- Rough estimate: 1 token ≈ 4 characters
- 20MB PDF ≈ 5M tokens → truncated to 150K tokens

### Processing Time
- Small PDF (< 1MB): 5-10 seconds
- Medium PDF (1-5MB): 15-30 seconds
- Large PDF (5-20MB): 30-60+ seconds

### Database
- SQLite suitable for local/small deployments
- Each summary stored with full PDF metadata
- Supports duplicate detection via file hash

---

## Future Enhancements

1. **OCR Support**: Handle scanned PDFs with text extraction
2. **Exact Token Counting**: Use tokenizer for accurate token limits
3. **Chunked Summarization**: For very large PDFs, summarize chunks separately
4. **Multiple Summaries**: Generate summaries in different lengths/styles
5. **Export Formats**: Support PDF, DOCX, Markdown export for summaries
6. **Authentication**: Add user accounts and summary management
7. **Batch Processing**: Process multiple PDFs in queue
8. **PostgreSQL**: Replace SQLite for production deployment

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs for detailed error messages
3. Verify Cerebras API key and status
4. Test endpoints using curl or Postman:

```bash
# Test backend connection
curl http://localhost:8000/health

# Test with a local PDF
curl -F "file=@path\to\your\file.pdf" http://localhost:8000/summarize

# Get summary history
curl http://localhost:8000/summaries
```

---

## Version Info

- **Backend**: Python 3.11+, FastAPI 0.136.3, SQLAlchemy 2.0.50
- **Frontend**: React 18, Vite 5.x, Tailwind CSS 3.x
- **PDF Processing**: pdfplumber 0.11.9
- **LLM**: Cerebras gpt-oss-120b
- **Database**: SQLite 3

---

**🎉 Your PDF Summarization Application is Ready!**

Start the backend and frontend servers, then upload a PDF to see the magic happen!
