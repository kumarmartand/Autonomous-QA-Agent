# Streamlit Cloud Deployment Fix

## Problem
Streamlit Cloud was failing with "installer returned a non-zero exit code" because it was trying to install backend dependencies (ChromaDB, sentence-transformers, etc.) that aren't needed for the frontend and cause build issues.

## Solution
- **requirements.txt** - Now contains only minimal dependencies for Streamlit frontend (streamlit + requests)
- **requirements-backend.txt** - Contains all backend dependencies for FastAPI deployment

## What Changed

### For Streamlit Cloud:
- Uses `requirements.txt` which only has:
  - streamlit>=1.28.0
  - requests>=2.31.0

### For Backend Deployment:
- Use `requirements-backend.txt` when deploying FastAPI backend
- Update build commands in Railway/Render to use `requirements-backend.txt`

## Updated Deployment Instructions

### Backend (Railway/Render):
- Build Command: `pip install -r requirements-backend.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Streamlit Cloud):
- Automatically uses `requirements.txt` (minimal dependencies)
- No changes needed - just redeploy!

## Why This Works

The Streamlit frontend only makes HTTP requests to the backend API. It doesn't need:
- FastAPI (backend framework)
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- pymupdf (PDF parsing)
- etc.

All heavy processing happens on the backend, so the frontend can be lightweight.

