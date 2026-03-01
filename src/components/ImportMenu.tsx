import React, { useState } from 'react';
import { ChatMessage } from '../types';
import { parseCSVFile, parseExcelFile, parseJsonText, calculateMetrics } from '../utils';
import './ImportMenu.css';

interface ImportMenuProps {
  onDataImported: (messages: ChatMessage[]) => void;
}

export const ImportMenu: React.FC<ImportMenuProps> = ({ onDataImported }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [jsonText, setJsonText] = useState('');
  const [importMode, setImportMode] = useState<'file' | 'json'>('file');

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      let messages: ChatMessage[] = [];

      if (file.name.endsWith('.csv')) {
        messages = await parseCSVFile(file);
      } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        messages = await parseExcelFile(file);
      } else {
        throw new Error('Unsupported file format. Please use CSV or Excel files.');
      }

      if (messages.length === 0) {
        throw new Error('No valid data found in the file. Please ensure it has raw_request and raw_reply columns.');
      }

      onDataImported(messages);
      setSuccess(`Successfully imported ${messages.length} messages from ${file.name}`);
      setJsonText('');
    } catch (err: any) {
      setError(err.message || 'Failed to parse file');
    } finally {
      setLoading(false);
    }
  };

  const handleJsonPaste = () => {
    if (!jsonText.trim()) {
      setError('Please paste JSON data');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const messages = parseJsonText(jsonText);

      if (messages.length === 0) {
        throw new Error('No valid data found in JSON. Please ensure it has raw_request and raw_reply fields.');
      }

      onDataImported(messages);
      setSuccess(`Successfully imported ${messages.length} messages from JSON`);
      setJsonText('');
    } catch (err: any) {
      setError(err.message || 'Failed to parse JSON');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="import-menu">
      <div className="import-container">
        <h1>📊 Import Chatbot Data</h1>
        
        <div className="mode-selector">
          <button
            className={`mode-btn ${importMode === 'file' ? 'active' : ''}`}
            onClick={() => { setImportMode('file'); setError(null); setSuccess(null); }}
          >
            📁 Upload File
          </button>
          <button
            className={`mode-btn ${importMode === 'json' ? 'active' : ''}`}
            onClick={() => { setImportMode('json'); setError(null); setSuccess(null); }}
          >
            📝 Paste JSON
          </button>
        </div>

        {importMode === 'file' && (
          <div className="file-upload-section">
            <div className="upload-box">
              <input
                type="file"
                id="file-input"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileUpload}
                disabled={loading}
                className="file-input"
              />
              <label htmlFor="file-input" className="upload-label">
                <span className="icon">📤</span>
                <span className="text">
                  {loading ? 'Processing...' : 'Click to upload or drag and drop'}
                </span>
                <span className="subtext">CSV or Excel files (raw_request, raw_reply columns)</span>
              </label>
            </div>
          </div>
        )}

        {importMode === 'json' && (
          <div className="json-section">
            <textarea
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
              placeholder={`Paste your JSON data here. Format:
[
  {
    "raw_request": "user message JSON string",
    "raw_reply": "bot response JSON string"
  }
]

Or single object:
{
  "raw_request": "message",
  "raw_reply": "response"
}`}
              className="json-textarea"
              disabled={loading}
            />
            <button
              onClick={handleJsonPaste}
              disabled={loading || !jsonText.trim()}
              className="json-submit-btn"
            >
              {loading ? '⏳ Processing...' : '💾 Save & Analyze'}
            </button>
          </div>
        )}

        {error && (
          <div className="message error-message">
            ❌ Error: {error}
          </div>
        )}

        {success && (
          <div className="message success-message">
            ✅ {success}
          </div>
        )}

        <div className="info-box">
          <h3>📋 Data Format Requirements</h3>
          <ul>
            <li><strong>raw_request:</strong> JSON string containing user message with metadata</li>
            <li><strong>raw_reply:</strong> JSON string containing bot response with token_usage information</li>
            <li>Token usage metrics are automatically extracted from token_usage field</li>
            <li>Supported formats: CSV, Excel (.xlsx, .xls), or JSON</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
