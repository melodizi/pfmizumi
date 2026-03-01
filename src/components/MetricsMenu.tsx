import React from 'react';
import { MetricsData, ChatMessage } from '../types';
import { exportToCSV, exportToJSON, downloadFile } from '../utils';
import './MetricsMenu.css';

interface MetricsMenuProps {
  metrics: MetricsData | null;
  messages: ChatMessage[];
  onBack: () => void;
}

export const MetricsMenu: React.FC<MetricsMenuProps> = ({ metrics, messages, onBack }) => {
  if (!metrics) {
    return (
      <div className="metrics-menu">
        <div className="empty-state">
          <p>No metrics data available. Please import data first.</p>
          <button onClick={onBack} className="back-button">← Back to Import</button>
        </div>
      </div>
    );
  }

  const handleExportCSV = () => {
    const csv = exportToCSV(metrics);
    downloadFile(csv, 'metrics-report.csv', 'text/csv');
  };

  const handleExportJSON = () => {
    const json = exportToJSON(metrics, messages);
    downloadFile(json, 'metrics-report.json', 'application/json');
  };

  const generateHTMLReport = () => {
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chatbot Performance Metrics Report</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
      min-height: 100vh;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      padding: 40px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    }
    h1 {
      color: #667eea;
      margin-bottom: 10px;
      text-align: center;
    }
    .report-date {
      text-align: center;
      color: #999;
      margin-bottom: 30px;
      font-size: 14px;
    }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }
    .metric-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      border-radius: 8px;
      text-align: center;
    }
    .metric-label {
      font-size: 12px;
      opacity: 0.9;
      margin-bottom: 8px;
    }
    .metric-value {
      font-size: 28px;
      font-weight: bold;
    }
    .metric-unit {
      font-size: 12px;
      opacity: 0.8;
    }
    .summary-section {
      background: #f5f7ff;
      border-left: 4px solid #667eea;
      padding: 20px;
      border-radius: 8px;
      margin-top: 30px;
    }
    .summary-section h2 {
      color: #667eea;
      font-size: 18px;
      margin-bottom: 15px;
    }
    .summary-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #e0e0e0;
    }
    .summary-row:last-child {
      border-bottom: none;
    }
    .summary-label {
      color: #666;
      font-weight: 500;
    }
    .summary-value {
      color: #333;
      font-weight: bold;
    }
    table {
      width: 100%;
      margin-top: 30px;
      border-collapse: collapse;
    }
    table th {
      background: #667eea;
      color: white;
      padding: 12px;
      text-align: left;
      font-weight: 600;
    }
    table td {
      border-bottom: 1px solid #eee;
      padding: 12px;
    }
    table tr:hover {
      background: #f5f7ff;
    }
    .footer {
      text-align: center;
      color: #999;
      font-size: 12px;
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #eee;
    }
    @media (max-width: 768px) {
      .container {
        padding: 20px;
      }
      .metrics-grid {
        grid-template-columns: 1fr;
      }
      h1 {
        font-size: 22px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 Chatbot Performance Metrics Report</h1>
    <p class="report-date">Generated: ${new Date(metrics.timestamp).toLocaleString()}</p>

    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-label">Total Messages Analyzed</div>
        <div class="metric-value">${metrics.total_messages}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Total Tokens Used</div>
        <div class="metric-value">${metrics.total_tokens.toLocaleString()}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Average Response Tokens</div>
        <div class="metric-value">${metrics.average_total_tokens}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Avg Response Length</div>
        <div class="metric-value">${metrics.average_response_length}</div>
        <div class="metric-unit">characters</div>
      </div>
    </div>

    <div class="summary-section">
      <h2>📋 Detailed Summary</h2>
      <div class="summary-row">
        <span class="summary-label">Total Prompt Tokens:</span>
        <span class="summary-value">${metrics.total_prompt_tokens.toLocaleString()}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Total Candidate Tokens:</span>
        <span class="summary-value">${metrics.total_candidate_tokens.toLocaleString()}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Average Prompt Tokens:</span>
        <span class="summary-value">${metrics.average_prompt_tokens}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Average Candidate Tokens:</span>
        <span class="summary-value">${metrics.average_candidate_tokens}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Minimum Response Tokens:</span>
        <span class="summary-value">${metrics.min_total_tokens}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Maximum Response Tokens:</span>
        <span class="summary-value">${metrics.max_total_tokens}</span>
      </div>
    </div>

    <div class="footer">
      <p>Performance Metrics Analysis Report</p>
      <p>Generated by Chatbot Performance Metrics Analyzer</p>
    </div>
  </div>
</body>
</html>
    `;
    downloadFile(html, 'metrics-report.html', 'text/html');
  };

  return (
    <div className="metrics-menu">
      <div className="metrics-container">
        <button onClick={onBack} className="back-button">← Back to Import</button>
        
        <h1>📊 Performance Metrics Analysis</h1>
        
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">Total Messages</div>
            <div className="metric-value">{metrics.total_messages}</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">Total Tokens</div>
            <div className="metric-value">{metrics.total_tokens.toLocaleString()}</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">Avg Response Tokens</div>
            <div className="metric-value">{metrics.average_total_tokens}</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">Avg Response Length</div>
            <div className="metric-value">{metrics.average_response_length}</div>
            <div className="metric-unit">chars</div>
          </div>
        </div>

        <div className="detailed-metrics">
          <h2>📋 Detailed Summary</h2>
          <div className="metrics-table">
            <div className="metrics-row">
              <span className="metrics-label">Total Prompt Tokens:</span>
              <span className="metrics-value">{metrics.total_prompt_tokens.toLocaleString()}</span>
            </div>
            <div className="metrics-row">
              <span className="metrics-label">Total Candidate Tokens:</span>
              <span className="metrics-value">{metrics.total_candidate_tokens.toLocaleString()}</span>
            </div>
            <div className="metrics-row">
              <span className="metrics-label">Average Prompt Tokens:</span>
              <span className="metrics-value">{metrics.average_prompt_tokens}</span>
            </div>
            <div className="metrics-row">
              <span className="metrics-label">Average Candidate Tokens:</span>
              <span className="metrics-value">{metrics.average_candidate_tokens}</span>
            </div>
            <div className="metrics-row">
              <span className="metrics-label">Min Total Tokens:</span>
              <span className="metrics-value">{metrics.min_total_tokens}</span>
            </div>
            <div className="metrics-row">
              <span className="metrics-label">Max Total Tokens:</span>
              <span className="metrics-value">{metrics.max_total_tokens}</span>
            </div>
            <div className="metrics-row">
              <span className="metrics-label">Report Generated:</span>
              <span className="metrics-value">{new Date(metrics.timestamp).toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div className="export-section">
          <h2>📥 Export Report</h2>
          <div className="export-buttons">
            <button onClick={handleExportCSV} className="export-btn csv-btn">
              📊 Export as CSV
            </button>
            <button onClick={handleExportJSON} className="export-btn json-btn">
              📄 Export as JSON
            </button>
            <button onClick={generateHTMLReport} className="export-btn html-btn">
              🌐 Export as HTML
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
