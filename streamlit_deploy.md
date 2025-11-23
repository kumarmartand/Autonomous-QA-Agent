# Streamlit Cloud Deployment Guide

## Important Notes

⚠️ **Streamlit Cloud can only host the Streamlit frontend.** The FastAPI backend needs to be deployed separately on a platform like:
- Railway (https://railway.app)
- Render (https://render.com)
- Heroku
- Fly.io
- Or any other cloud platform

## Deployment Steps

### 1. Deploy FastAPI Backend

Deploy the FastAPI backend to a cloud service:

**Option A: Railway**
1. Create account at railway.app
2. Create new project
3. Connect GitHub repository
4. Set root directory to project root
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `LLM_PROVIDER=ollama` (or groq/openai)
   - `LLM_MODEL=llama3.2`
   - `LLM_BASE_URL=your_ollama_url` (if using Ollama)
   - `LLM_API_KEY=your_key` (if using Groq/OpenAI)

**Option B: Render**
1. Create account at render.com
2. Create new Web Service
3. Connect GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (same as above)

### 2. Deploy Streamlit Frontend

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set:
   - **Main file path**: `ui/streamlit_app.py`
   - **Python version**: 3.8 or higher
6. Add environment variable:
   - `API_BASE_URL`: Your FastAPI backend URL (e.g., `https://your-backend.railway.app`)

### 3. Update API URL

After deploying the backend, update the `API_BASE_URL` environment variable in Streamlit Cloud to point to your deployed backend URL.

## Environment Variables for Streamlit Cloud

- `API_BASE_URL`: URL of your deployed FastAPI backend (required)

## Environment Variables for Backend

- `LLM_PROVIDER`: ollama, groq, or openai
- `LLM_MODEL`: Model name
- `LLM_BASE_URL`: Base URL (for Ollama)
- `LLM_API_KEY`: API key (for Groq/OpenAI)
- `VECTOR_STORE_TYPE`: chroma (default) or faiss
- `EMBEDDING_MODEL`: sentence-transformers model name

## Testing

After deployment:
1. Test backend: Visit `https://your-backend-url/health`
2. Test frontend: Visit your Streamlit Cloud URL
3. Ensure frontend can connect to backend

