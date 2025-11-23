"""Configuration settings for the QA Agent application."""
import os
from pathlib import Path
from typing import Optional

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Assets directory
ASSETS_DIR = BASE_DIR / "assets"
SUPPORT_DOCS_DIR = ASSETS_DIR / "support_docs"
CHECKOUT_HTML_PATH = ASSETS_DIR / "checkout.html"

# Vector store settings
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chroma")  # "chroma" or "faiss"

# Embedding model settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # For all-MiniLM-L6-v2

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval settings
TOP_K_RETRIEVAL = 5

# LLM settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama", "groq", "openai", etc.
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# FastAPI settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Streamlit settings
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# Supported file types
SUPPORTED_DOC_TYPES = {".md", ".txt", ".json", ".pdf", ".html"}

