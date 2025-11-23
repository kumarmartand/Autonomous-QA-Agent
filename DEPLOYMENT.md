# Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Push to GitHub

```bash
# Create a new repository on GitHub (https://github.com/new)
# Then run:

git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2. Deploy Backend (FastAPI)

**Option A: Railway (Recommended)**
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect Python
6. **Important**: Set build command to use backend requirements:
   - Build Command: `pip install -r requirements-backend.txt`
7. Add environment variables:
   ```
   LLM_PROVIDER=ollama
   LLM_MODEL=llama3.2
   LLM_BASE_URL=your_ollama_url
   ```
8. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
9. Deploy!

**Option B: Render**
1. Go to https://render.com
2. Create account and connect GitHub
3. New → Web Service
4. Connect repository
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (same as above)
7. Deploy!

### 3. Deploy Frontend (Streamlit Cloud)

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Configure:
   - **Main file path**: `ui/streamlit_app.py`
   - **Python version**: 3.8
6. Add environment variable:
   - **Key**: `API_BASE_URL`
   - **Value**: Your backend URL (e.g., `https://your-app.railway.app`)
7. Deploy!

## 📝 Important Notes

- **Backend must be deployed first** - Streamlit needs the API URL
- **CORS is enabled** - Backend allows all origins (configure for production)
- **LLM Provider** - Make sure your LLM service is accessible from the backend

## 🔧 Environment Variables

### Backend (Railway/Render)
```
LLM_PROVIDER=ollama|groq|openai
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434  # For Ollama
LLM_API_KEY=your_key  # For Groq/OpenAI
VECTOR_STORE_TYPE=chroma
```

### Frontend (Streamlit Cloud)
```
API_BASE_URL=https://your-backend-url.com
```

## ✅ Testing After Deployment

1. Test backend: `https://your-backend-url/health`
2. Test frontend: Your Streamlit Cloud URL
3. Try uploading documents and generating test cases

