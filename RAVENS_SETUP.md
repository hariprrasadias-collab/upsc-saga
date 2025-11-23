# UPSC Current Affairs System - Setup Guide

## Quick Start

### 1. Add Your Gemini API Key

1. Get your API key from: https://makersuite.google.com/app/apikey
2. Create a `.env` file in the `backend` folder:
   ```bash
   cd backend
   copy .env.example .env
   ```
3. Open `.env` and add your key:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key
   ```

### 2. The database has been initialized ✅

### 3. Restart the backend server

Stop the current backend (Ctrl+C) and restart:
```bash
python app.py
```

### 4. Start Using!

1. Navigate to the **Ravens** tab
2. Click **"📡 Live Feed"**
3. Choose MUNIN or HUGIN
4. Click **"🤖 Process with AI"** on any article
5. Article will be analyzed, tagged, and saved!

## Features Overview

- **AI Summarization**: Gemini Pro creates UPSC-focused summaries
- **Smart Tagging**: Auto-tags with GS Papers + Subjects
- **Image Extraction**: Pulls images from articles
- **PYQ Linking**: Shows related Previous Year Questions
- **Anki Integration**: One-click flashcard creation
- **Filters**: Search by paper, subject, importance
- **Notes**: Add personal notes to articles
- **Bookmarks**: Save important articles

## File Structure

```
backend/
├── app/
│   ├── db_models/
│   │   └── current_affairs.py (✅ NEW - Database operations)
│   ├── services/
│   │   └── upsc_summarizer.py (✅ NEW - Gemini AI integration)
│   └── routes/
│       └── ravens.py (✅ UPDATED - Enhanced routes)
├── .env.example (✅ NEW - Environment template)
└── init_db.py (✅ NEW - Database initialization)

frontend/
└── src/
    └── components/
        └── Ravens/
            ├── NewsCardEnhanced.tsx (✅ NEW)
            ├── FilterPanel.tsx (✅ NEW)
            ├── Ravens.tsx (✅ UPDATED)
            └── Ravens.css (✅ UPDATED)
```

All files are ready to go!
