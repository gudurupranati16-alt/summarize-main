import React, { useState } from 'react';
import './FileUpload.css';

export default function FileUpload({ onUpload }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileName, setFileName] = useState(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const processFiles = async (filesList) => {
    const files = Array.from(filesList);
    if (files.length === 0) return;

    // Validate each file
    for (const file of files) {
      if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        setError(`"${file.name}" is not a PDF file. Please upload only PDFs.`);
        return;
      }

      const maxSize = 20 * 1024 * 1024;
      if (file.size > maxSize) {
        setError(`"${file.name}" exceeds the 20MB limit. File is ${(file.size / 1024 / 1024).toFixed(2)}MB`);
        return;
      }
    }

    setError(null);
    const displayNames = files.map(f => f.name);
    let displayName = "";
    if (displayNames.length === 1) {
      displayName = displayNames[0];
    } else if (displayNames.length <= 3) {
      displayName = displayNames.join(', ');
    } else {
      displayName = `${displayNames.length} PDF files (${displayNames.slice(0, 2).join(', ')}...)`;
    }
    
    setFileName(displayName);
    setIsLoading(true);

    try {
      await onUpload(files);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFiles(files);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      processFiles(files);
    }
  };

  const handleClick = () => {
    document.getElementById('file-input').click();
  };

  return (
    <div className="file-upload-container">
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${isLoading ? 'loading' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          id="file-input"
          type="file"
          accept="application/pdf"
          onChange={handleFileInput}
          style={{ display: 'none' }}
          disabled={isLoading}
          multiple
        />

        {isLoading ? (
          <div className="upload-loading">
            <div className="spinner"></div>
            <p>Processing {fileName}...</p>
          </div>
        ) : (
          <div className="upload-content">
            <svg
              className="upload-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <h3>Drag and drop your PDF files</h3>
            <p>or click to select files</p>
            <p className="file-info">PDF files up to 20MB each</p>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          <svg fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </div>
      )}

      {fileName && !isLoading && !error && (
        <div className="success-message">
          <svg fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          {fileName} uploaded successfully!
        </div>
      )}
    </div>
  );
}
