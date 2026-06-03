import { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import SummaryDisplay from "./components/SummaryDisplay";
import "./App.css";

function App() {
  const [currentSummary, setCurrentSummary] = useState(null);
  const [summaryHistory, setSummaryHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [connectionError, setConnectionError] = useState(null);

  // Check backend connection on mount
  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const response = await fetch("http://localhost:8000/health");
        if (response.ok) {
          setConnectionError(null);
        } else {
          setConnectionError("Backend server is not responding properly");
        }
      } catch (error) {
        setConnectionError(
          "Cannot connect to backend server. Make sure it's running on http://localhost:8000"
        );
      }
    };

    checkBackendConnection();
  }, []);

  const handleUpload = async (file) => {
    const { uploadPDF } = await import("./services/api.js");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/summarize", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to process PDF");
      }

      const data = await response.json();
      setCurrentSummary(data);
      setConnectionError(null);

      // Refresh history
      fetchSummaryHistory();
    } catch (error) {
      throw error;
    }
  };

  const fetchSummaryHistory = async () => {
    try {
      const response = await fetch("http://localhost:8000/summaries");
      if (response.ok) {
        const data = await response.json();
        setSummaryHistory(data);
      }
    } catch (error) {
      console.error("Failed to fetch history:", error);
    }
  };

  useEffect(() => {
    fetchSummaryHistory();
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">📄 PDF Summarizer</h1>
          <p className="app-subtitle">
            Upload your PDF and let AI generate a comprehensive summary
          </p>
        </div>
      </header>

      <main className="app-main">
        {connectionError && (
          <div className="connection-error">
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            {connectionError}
          </div>
        )}

        <FileUpload onUpload={handleUpload} />

        {currentSummary && (
          <SummaryDisplay
            summary={currentSummary}
            onClear={() => setCurrentSummary(null)}
          />
        )}

        {summaryHistory.length > 0 && (
          <div className="history-section">
            <button
              className="history-toggle"
              onClick={() => setShowHistory(!showHistory)}
            >
              <span>📚 Summary History ({summaryHistory.length})</span>
              <span className="toggle-icon">{showHistory ? "▼" : "▶"}</span>
            </button>

            {showHistory && (
              <div className="history-list">
                {summaryHistory.map((item, index) => (
                  <div
                    key={item.id}
                    className="history-item"
                    onClick={() => {
                      setCurrentSummary({
                        pdf_id: item.pdf_id,
                        filename: item.filename,
                        file_size: 0,
                        upload_date: item.created_at,
                        summary: item.summary_text,
                      });
                      setShowHistory(false);
                    }}
                  >
                    <div className="history-item-content">
                      <h4>{item.filename}</h4>
                      <p className="history-item-date">
                        {new Date(item.created_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                    <span className="history-item-arrow">→</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Powered by Cerebras AI • Max file size: 20MB • Supports PDF format
        </p>
      </footer>
    </div>
  );
}

export default App;