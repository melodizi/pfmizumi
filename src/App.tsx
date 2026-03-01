import React, { useState } from 'react';
import { ChatMessage } from './types';
import { calculateMetrics } from './utils';
import { ImportMenu } from './components/ImportMenu';
import { MetricsMenu } from './components/MetricsMenu';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState<'menu' | 'import' | 'metrics'>('menu');
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const metrics = messages.length > 0 ? calculateMetrics(messages) : null;

  const handleDataImported = (importedMessages: ChatMessage[]) => {
    setMessages(importedMessages);
    setCurrentPage('metrics');
  };

  const handleBackToMenu = () => {
    setCurrentPage('menu');
  };

  const handleStartImport = () => {
    setCurrentPage('import');
  };

  if (currentPage === 'import') {
    return <ImportMenu onDataImported={handleDataImported} />;
  }

  if (currentPage === 'metrics') {
    return (
      <MetricsMenu
        metrics={metrics}
        messages={messages}
        onBack={handleBackToMenu}
      />
    );
  }

  return (
    <div className="app">
      <div className="main-menu">
        <div className="menu-container">
          <h1 className="app-title">🤖 Chatbot Performance Analyzer</h1>
          <p className="app-subtitle">Analyze and Export Chatbot Performance Metrics</p>

          <div className="menu-cards">
            <div
              className="menu-card"
              onClick={handleStartImport}
            >
              <div className="card-icon">📤</div>
              <h2>Import Data</h2>
              <p>Upload CSV/Excel or paste JSON data containing chatbot conversations</p>
              <div className="card-footer">Click to start →</div>
            </div>

            <div
              className="menu-card"
              onClick={() => messages.length > 0 ? setCurrentPage('metrics') : alert('Please import data first')}
              style={{
                opacity: messages.length > 0 ? 1 : 0.5,
                cursor: messages.length > 0 ? 'pointer' : 'not-allowed'
              }}
            >
              <div className="card-icon">📊</div>
              <h2>View Metrics</h2>
              <p>Analyze performance metrics and export detailed reports</p>
              <div className="card-footer">{messages.length > 0 ? `${messages.length} messages loaded` : 'No data yet'}</div>
            </div>
          </div>

          <div className="info-section">
            <h3>ℹ️ Features</h3>
            <ul>
              <li>✅ Import data from CSV, Excel, or JSON formats</li>
              <li>✅ Automatic token usage analysis</li>
              <li>✅ Performance metrics calculation</li>
              <li>✅ Export reports as CSV, JSON, or HTML</li>
              <li>✅ Support for Thai language and special characters</li>
            </ul>
          </div>

          {messages.length > 0 && (
            <div className="data-status">
              <p>📌 Current Status: <strong>{messages.length} messages loaded</strong></p>
              <button onClick={() => { setMessages([]); }} className="reset-btn">
                🔄 Clear Data
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
