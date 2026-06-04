import streamlit as st
import requests
import os

# Set page config for a premium wide layout
st.set_page_config(
    page_title="AI PDF News Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium design
st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Gradient title */
    .gradient-text {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8C00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    /* Card design for outputs */
    .summary-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    /* Sentiment badge styles */
    .sentiment-positive {
        background: linear-gradient(135deg, #00c853, #69f0ae);
        color: #1b5e20;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    .sentiment-negative {
        background: linear-gradient(135deg, #ff1744, #ff8a80);
        color: #b71c1c;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    .sentiment-neutral {
        background: linear-gradient(135deg, #2196f3, #90caf9);
        color: #0d47a1;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    .sentiment-mixed {
        background: linear-gradient(135deg, #ff9800, #ffcc02);
        color: #e65100;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    /* Dark mode styling support */
    @media (prefers-color-scheme: dark) {
        .summary-card {
            background-color: #1e222b;
            border-left: 5px solid #FF8C00;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
    }
    </style>
""", unsafe_allow_html=True)

# Backend URL config
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/news.png", width=80)
    st.markdown("### AI News Summarizer")
    st.write("Extract and summarize critical insights from multiple news PDF documents using Cerebras AI models.")
    
    st.markdown("---")
    st.markdown("#### System Status")
    
    # Check backend health
    try:
        health_resp = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if health_resp.status_code == 200:
            st.success("🟢 Connected to Backend API")
        else:
            st.warning("⚠️ Backend responded with error")
    except Exception:
        st.error("🔴 Backend API is Offline\nPlease run the backend API first.")
        
    st.markdown("---")
    st.markdown("#### Instructions")
    st.info("""
    1. Upload one or more PDF news files.
    2. Click **Generate Summary**.
    3. Read the single-paragraph summary and sentiment analysis.
    4. Download the report!
    """)

# Title & Description
st.markdown('<h1 class="gradient-text">📰 AI PDF News Summarizer</h1>', unsafe_allow_html=True)
st.write("Upload PDF articles to generate a concise single-paragraph summary with sentiment analysis.")

# File Uploader
uploaded_files = st.file_uploader(
    "Upload News Article PDFs (Multiple Allowed)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload your news reports or articles in PDF format. Text will be extracted and analyzed."
)

col1, col2 = st.columns([1, 5])

with col1:
    generate_btn = st.button("🚀 Generate Summary", use_container_width=True)
with col2:
    if uploaded_files:
        st.info(f"📂 {len(uploaded_files)} PDF file(s) selected.")

# Action trigger
if generate_btn:
    if not uploaded_files:
        st.error("Please upload at least one PDF file first.")
        st.stop()
        
    # Read files
    files = []
    for file in uploaded_files:
        # Reset file pointer to read from beginning
        file.seek(0)
        files.append(
            ("files", (file.name, file.read(), "application/pdf"))
        )
        
    # Make API Call with Spinner
    with st.spinner("⏳ Extracting text from PDFs and generating summary via Cerebras AI..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/summarize-pdfs",
                files=files,
                timeout=120  # Give it ample time for large documents
            )
            
            if response.status_code == 200:
                result = response.json()
                summary_content = result.get("summary", "")
                sentiment = result.get("sentiment", "Neutral")
                sentiment_explanation = result.get("sentiment_explanation", "")
                
                if summary_content:
                    st.success("✨ Summary Generated Successfully!")
                    
                    # --- Sentiment Analysis Section ---
                    st.markdown("### 🎯 Sentiment Analysis")
                    sentiment_lower = sentiment.lower()
                    sentiment_class = f"sentiment-{sentiment_lower}"
                    
                    # Sentiment emoji mapping
                    sentiment_emoji = {
                        "positive": "😊",
                        "negative": "😟",
                        "neutral": "😐",
                        "mixed": "🤔"
                    }
                    emoji = sentiment_emoji.get(sentiment_lower, "😐")
                    
                    st.markdown(
                        f'<span class="{sentiment_class}">{emoji} {sentiment}</span>',
                        unsafe_allow_html=True
                    )
                    if sentiment_explanation:
                        st.caption(f"💡 {sentiment_explanation}")
                    
                    st.markdown("---")
                    
                    # --- Summary Section ---
                    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
                    st.markdown("### 📋 Summary")
                    st.markdown(summary_content)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Build downloadable report
                    report = (
                        f"# News Analysis Report\n\n"
                        f"## Sentiment: {sentiment}\n"
                        f"{sentiment_explanation}\n\n"
                        f"## Summary\n\n"
                        f"{summary_content}\n"
                    )
                    
                    # Add Download Button for the Markdown summary
                    st.download_button(
                        label="📥 Download Summary Report (MD)",
                        data=report,
                        file_name="news_analysis_report.md",
                        mime="text/markdown",
                        use_container_width=False
                    )
                else:
                    st.error("No summary content was returned by the API.")
            else:
                # Handle error returned by FastAPI
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                st.error(f"❌ Backend Error ({response.status_code}): {error_detail}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection Error: Could not connect to the backend server. Please verify the backend is running at http://localhost:8000")
        except requests.exceptions.Timeout:
            st.error("❌ Request Timeout: The summarization took too long. Please try with smaller/fewer PDF files.")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")