import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://127.0.0.1:8000';

export default function App() {
  const [sourceType, setSourceType] = useState('url');
  const [urlInput, setUrlInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [targetText, setTargetText] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const logsEndRef = useRef(null);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!targetText.trim()) {
      setError('Please enter a target text to search.');
      return;
    }

    if (sourceType === 'url' && !urlInput.trim()) {
      setError('Please enter a video URL.');
      return;
    }

    if (sourceType === 'file' && !selectedFile) {
      setError('Please select a local video file.');
      return;
    }

    setIsSearching(true);
    setLogs([]);
    setResult(null);
    setError(null);

    const formData = new FormData();
    formData.append('target', targetText.trim());

    if (sourceType === 'url') {
      formData.append('url', urlInput.trim());
    } else {
      formData.append('video', selectedFile);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/search/stream`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || `Server error ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          const line = part.trim();
          if (line.startsWith('data: ')) {
            const jsonStr = line.replace('data: ', '').trim();
            if (jsonStr) {
              try {
                const event = JSON.parse(jsonStr);
                handleStreamEvent(event);
              } catch (parseErr) {
                console.error('Failed to parse SSE JSON:', parseErr, jsonStr);
              }
            }
          }
        }
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message || 'An error occurred during video search.');
      setIsSearching(false);
    }
  };

  const handleStreamEvent = (event) => {
    if (event.type === 'complete') {
      setLogs((prevLogs) =>
        prevLogs.map((log) => ({ ...log, status: 'completed' }))
      );
      setResult(event.result);
      setIsSearching(false);
      return;
    }

    if (event.type === 'error') {
      setError(event.error || 'Pipeline execution failed.');
      setIsSearching(false);
      return;
    }

    // Progress status events
    const newLogItem = {
      id: Date.now() + Math.random(),
      message: event.message,
      stage: event.stage || 'status',
      status: 'running',
    };

    setLogs((prevLogs) => {
      const updated = prevLogs.map((log) => ({
        ...log,
        status: 'completed',
      }));
      return [...updated, newLogItem];
    });
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1 className="brand-title">Quest1</h1>
        <h2 className="brand-subtitle">Video Text Search</h2>
        <p className="brand-description">
          Search a dialogue or text inside subtitles, audio, and video frames.
        </p>
      </header>

      {/* Main Search Card */}
      <div className="card search-card">
        <form onSubmit={handleSearch}>
          {/* Source Type Selector */}
          <div className="form-group">
            <label className="form-label">Source Type</label>
            <div className="source-toggle-group">
              <button
                type="button"
                className={`toggle-btn ${sourceType === 'url' ? 'active' : ''}`}
                onClick={() => setSourceType('url')}
                disabled={isSearching}
              >
                Video URL
              </button>
              <button
                type="button"
                className={`toggle-btn ${sourceType === 'file' ? 'active' : ''}`}
                onClick={() => setSourceType('file')}
                disabled={isSearching}
              >
                Local File
              </button>
            </div>
          </div>

          {/* Source Input */}
          <div className="form-group">
            <label className="form-label">
              {sourceType === 'url' ? 'Video URL' : 'Local Video File'}
            </label>
            {sourceType === 'url' ? (
              <input
                type="url"
                className="form-input"
                placeholder="https://youtu.be/..."
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                disabled={isSearching}
              />
            ) : (
              <input
                type="file"
                className="form-input file-input"
                accept="video/*"
                onChange={(e) => setSelectedFile(e.target.files[0] || null)}
                disabled={isSearching}
              />
            )}
          </div>

          {/* Target Text Input */}
          <div className="form-group">
            <label className="form-label">Target Text</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. In my younger age"
              value={targetText}
              onChange={(e) => setTargetText(e.target.value)}
              disabled={isSearching}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="submit-btn"
            disabled={isSearching}
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="card error-card">
          <div className="error-header font-semibold">Something went wrong</div>
          <div className="error-message">{error}</div>
        </div>
      )}

      {/* Processing Log Panel */}
      {logs.length > 0 && (
        <div className="card log-card">
          <div className="card-title">Processing</div>
          <div className="log-list">
            {logs.map((log) => (
              <div key={log.id} className={`log-item log-${log.status}`}>
                <span className="log-indicator">
                  {log.status === 'completed' && '✓'}
                  {log.status === 'running' && '●'}
                  {log.status === 'pending' && '○'}
                  {log.status === 'error' && '✕'}
                </span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>
      )}

      {/* Result Display */}
      {result && (
        <div className="card result-card">
          <div className="card-title">Search Result</div>

          {result.found ? (
            <div className="result-content">
              <div className="status-badge match-badge font-semibold">
                ✓ Match Found
              </div>

              <div className="result-grid">
                <div className="grid-item">
                  <span className="grid-label">Source</span>
                  <span className="grid-value source-tag">{result.source}</span>
                </div>

                <div className="grid-item">
                  <span className="grid-label">Confidence</span>
                  <span className="grid-value">{result.score?.toFixed(2)}%</span>
                </div>

                <div className="grid-item">
                  <span className="grid-label">Start</span>
                  <span className="grid-value timestamp-val">{result.timestamp}</span>
                </div>

                <div className="grid-item">
                  <span className="grid-label">End</span>
                  <span className="grid-value timestamp-val">{result.end_timestamp || 'N/A'}</span>
                </div>

                <div className="grid-item">
                  <span className="grid-label">Frame #</span>
                  <span className="grid-value">{result.frame_number ?? 'N/A'}</span>
                </div>
              </div>

              <div className="text-block">
                <span className="block-label">Target Text</span>
                <div className="block-content">"{result.target}"</div>
              </div>

              <div className="text-block">
                <span className="block-label">Matched Text</span>
                <div className="block-content highlight-text">
                  "{result.matched_text}"
                </div>
              </div>

              {result.frame_url && (
                <div className="frame-container">
                  <span className="block-label">Extracted Frame</span>
                  <div className="frame-wrapper">
                    <img
                      src={`${API_BASE_URL}${result.frame_url}`}
                      alt="Extracted Result Frame"
                      className="result-frame-img"
                    />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="result-content no-match-content">
              <div className="status-badge no-match-badge font-semibold">
                No Match Found
              </div>
              <p className="no-match-text">
                The target text was not found in:
              </p>
              <ul className="no-match-list">
                <li>Subtitles</li>
                <li>Audio (Whisper)</li>
                <li>Visual OCR</li>
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
