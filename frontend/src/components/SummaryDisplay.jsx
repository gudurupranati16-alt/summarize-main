import React from 'react';
import './SummaryDisplay.css';

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    alert('Summary copied to clipboard!');
  } catch {
    alert('Failed to copy to clipboard');
  }
};

const downloadSummary = (filename, summary) => {
  const element = document.createElement('a');
  const file = new Blob([summary], { type: 'text/plain' });
  element.href = URL.createObjectURL(file);
  element.download = `${filename.replace('.pdf', '')}_summary.txt`;
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
};

export default function SummaryDisplay({ summary, onClear }) {
  const [isExpanded, setIsExpanded] = React.useState(true);

  if (!summary) return null;

  return (
    <div className="summary-display">
      <div className="summary-header">
        <div className="summary-info">
          <h3>{summary.filename}</h3>
          <p className="summary-meta">
            {(summary.file_size / 1024).toFixed(1)} KB • {formatDate(summary.upload_date)}
          </p>
        </div>
        <button className="clear-btn" onClick={onClear} title="Clear summary">
          ✕
        </button>
      </div>

      <div className={`summary-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
        <div className="summary-text">{summary.summary}</div>
      </div>

      <button
        className="expand-btn"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? 'Collapse' : 'Expand'}
      </button>

      <div className="summary-actions">
        <button 
          className="action-btn copy-btn" 
          onClick={() => copyToClipboard(summary.summary)}
        >
          📋 Copy
        </button>
        <button 
          className="action-btn download-btn" 
          onClick={() => downloadSummary(summary.filename, summary.summary)}
        >
          ⬇️ Download
        </button>
      </div>
    </div>
  );
}
