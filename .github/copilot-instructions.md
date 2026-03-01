# Chatbot Performance Metrics Analyzer - Project Setup Guide

## Project Overview
A React-based web application for importing chatbot conversation data and analyzing performance metrics with export capabilities.

## Completed Steps

### ✅ Project Scaffolding
- Set up Vite React TypeScript project structure
- Created package.json with all dependencies
- Configured Vite with React plugin support
- Enabled TypeScript with strict type checking

### ✅ Core Application Files
- **Components**: ImportMenu (Menu 1) and MetricsMenu (Menu 2)
- **Utilities**: Data parsing, metrics calculation, export functions
- **Styling**: Custom CSS with gradient backgrounds and responsive design
- **Types**: Full TypeScript interface definitions

### ✅ Features Implemented
- CSV and Excel file import with data validation
- JSON direct paste functionality
- Automatic token usage extraction and analysis
- Token metrics calculation (prompt, candidates, total)
- Response length analysis
- Multi-format export (CSV, JSON, HTML)
- Responsive UI for desktop and mobile

### ✅ Documentation
- Comprehensive README.md with usage instructions
- Data format specifications and examples
- Project structure documentation
- Troubleshooting guide

## Next Steps: Installation & Running

### Install Dependencies
```bash
npm install
```

### Development Server
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

## Project Structure
```
src/
├── components/          # React components
│   ├── ImportMenu.tsx
│   ├── ImportMenu.css
│   ├── MetricsMenu.tsx
│   └── MetricsMenu.css
├── App.tsx              # Main component
├── App.css              # Styling
├── types.ts             # TypeScript definitions
├── utils.ts             # Utility functions
├── main.tsx             # Entry point
└── index.css            # Global styles
```

## Key Features

1. **Menu 1 - Import Data**: Upload CSV/Excel or paste JSON data
2. **Menu 2 - Metrics**: View calculated metrics and export reports
3. **Data Processing**: Automatic token usage extraction
4. **Export Options**: CSV, JSON, HTML formats

## Support for Your Use Case

### ✅ Import Options
- CSV files with raw_request/raw_reply columns
- Excel files (.xlsx, .xls)
- JSON format (array or single object)

### ✅ Metrics Calculated
- Total and average token usage
- Prompt/candidate token breakdown
- Response length statistics
- Min/max token values

### ✅ Export Formats
- CSV (spreadsheet compatible)
- JSON (structured data)
- HTML (formatted report)

## Technical Stack
- React 18 + TypeScript
- Vite (fast build tool)
- PapaParse (CSV parsing)
- XLSX (Excel support)
- Custom CSS (no external UI libraries)

