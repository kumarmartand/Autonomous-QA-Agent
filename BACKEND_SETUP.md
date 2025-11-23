# Backend Setup Guide - Fix "API server is not running"

## Current Status
✅ Streamlit frontend is deployed on Streamlit Cloud  
❌ FastAPI backend needs to be deployed separately

## Quick Fix: Deploy Backend

The Streamlit app needs the FastAPI backend to be running. Follow these steps:

### Option 1: Railway (Recommended - Easiest)

1. **Go to Railway**: https://railway.app
2. **Sign in** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select**: `kumarmartand/Autonomous-QA-Agent`
5. **Settings**:
   - **Root Directory**: Leave default (project root)
   - **Build Command**: `pip install -r requirements-backend.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables** (Add these):
   ```
   LLM_PROVIDER=ollama
   LLM_MODEL=llama3.2
   LLM_BASE_URL=http://localhost:11434
   ```
   (Or use Groq/OpenAI if you prefer)
7. **Deploy** - Railway will give you a URL like: `https://your-app.railway.app`
8. **Copy the backend URL**

### Option 2: Render

1. **Go to Render**: https://render.com
2. **Sign in** with GitHub
3. **New** → **Web Service**
4. **Connect** your repository: `kumarmartand/Autonomous-QA-Agent`
5. **Settings**:
   - **Build Command**: `pip install -r requirements-backend.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables** (same as Railway)
7. **Deploy** and copy the URL

### Step 2: Connect Streamlit to Backend

1. **Go to Streamlit Cloud**: https://share.streamlit.io
2. **Open your app** settings
3. **Go to "Settings"** → **"Secrets"** or **"Environment variables"**
4. **Add environment variable**:
   - **Key**: `API_BASE_URL`
   - **Value**: Your backend URL (e.g., `https://your-app.railway.app`)
5. **Save** - Streamlit will automatically redeploy

### Step 3: Test

1. **Check backend health**: Visit `https://your-backend-url/health`
   - Should return: `{"status": "healthy", "vector_store_ready": false}`
2. **Refresh your Streamlit app**
3. **The error should be gone!**

## Troubleshooting

### Backend not responding?
- Check Railway/Render logs for errors
- Verify environment variables are set
- Make sure the build completed successfully

### Still seeing "API server is not running"?
- Verify `API_BASE_URL` is set correctly in Streamlit Cloud
- Check that backend URL is accessible (try in browser)
- Make sure backend allows CORS (already configured in code)

### LLM errors?
- If using Ollama, make sure it's accessible from your backend
- For Groq/OpenAI, verify API keys are correct
- Check backend logs for LLM connection errors

## Quick Test Commands

Test backend locally first:
```bash
# Install dependencies
pip install -r requirements-backend.txt

# Run backend
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/health
```

## Architecture

```
┌─────────────────────┐
│  Streamlit Cloud    │  (Frontend - Already deployed ✅)
│  streamlit.app      │
└──────────┬──────────┘
           │ HTTP Requests
           │ (API_BASE_URL)
           ▼
┌─────────────────────┐
│  Railway/Render     │  (Backend - Needs deployment ❌)
│  FastAPI Backend    │
└─────────────────────┘
```

The frontend makes HTTP requests to the backend API. Both need to be deployed separately.

