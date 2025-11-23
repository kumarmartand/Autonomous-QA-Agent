"""FastAPI backend for QA Agent."""
import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import (
    VECTOR_STORE_TYPE, EMBEDDING_MODEL, VECTOR_STORE_DIR,
    CHECKOUT_HTML_PATH, CHUNK_SIZE, CHUNK_OVERLAP
)
from app.models.schemas import (
    BuildKnowledgeBaseRequest, BuildKnowledgeBaseResponse,
    GenerateTestCasesRequest, GenerateTestCasesResponse, TestCase,
    GenerateScriptRequest, GenerateScriptResponse,
    HealthResponse
)
from app.services.ingestion import DocumentIngester
from app.services.vector_store import VectorStore
from app.services.llm_client import get_llm_client
from app.services.test_case_agent import TestCaseAgent
from app.services.script_agent import ScriptAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    initialize_services()
    yield
    # Shutdown (if needed)
    pass

# Initialize FastAPI app
app = FastAPI(
    title="QA Agent API",
    description="Autonomous QA Agent for Test Case and Script Generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
vector_store: Optional[VectorStore] = None
llm_client = None
test_case_agent: Optional[TestCaseAgent] = None
script_agent: Optional[ScriptAgent] = None
uploaded_documents: dict = {}  # Store uploaded documents in memory
html_content: Optional[str] = None


def initialize_services():
    """Initialize vector store and LLM client."""
    global vector_store, llm_client, test_case_agent, script_agent
    
    try:
        # Initialize vector store
        if vector_store is None:
            VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
            vector_store = VectorStore(
                store_type=VECTOR_STORE_TYPE,
                embedding_model=EMBEDDING_MODEL,
                store_dir=VECTOR_STORE_DIR
            )
        
        # Initialize LLM client
        if llm_client is None:
            llm_client = get_llm_client(
                provider=os.getenv("LLM_PROVIDER", "ollama"),
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
                model=os.getenv("LLM_MODEL", "llama3.2"),
                api_key=os.getenv("LLM_API_KEY", "")
            )
        
        # Initialize agents
        if test_case_agent is None:
            test_case_agent = TestCaseAgent(vector_store, llm_client)
        
        if script_agent is None:
            script_agent = ScriptAgent(vector_store, llm_client)
        
        return True
    except Exception as e:
        print(f"Error initializing services: {str(e)}")
        return False




@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global vector_store
    try:
        if vector_store is None:
            initialize_services()
        
        stats = vector_store.get_stats() if vector_store else {}
        return HealthResponse(
            status="healthy",
            vector_store_ready=vector_store is not None and stats.get("document_count", 0) > 0
        )
    except Exception as e:
        return HealthResponse(
            status=f"error: {str(e)}",
            vector_store_ready=False
        )


@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Upload a support document."""
    global uploaded_documents
    
    try:
        # Read file content
        content = await file.read()
        
        # Determine file type
        filename = file.filename
        ext = Path(filename).suffix.lower()
        
        # Decode content if text file
        if ext in [".md", ".txt", ".json", ".html"]:
            try:
                content_str = content.decode('utf-8')
            except:
                content_str = content.decode('latin-1')
        else:
            # For PDF, keep as bytes
            content_str = content
        
        # Store document
        doc_id = f"doc_{len(uploaded_documents)}"
        uploaded_documents[doc_id] = {
            "filename": filename,
            "content": content_str,
            "doc_type": ext,
            "is_binary": ext == ".pdf"
        }
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": filename,
            "message": f"Document '{filename}' uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@app.post("/upload-html")
async def upload_html(file: UploadFile = File(...)):
    """Upload or update checkout.html."""
    global html_content
    
    try:
        content = await file.read()
        html_content = content.decode('utf-8')
        
        # Also save to assets directory
        CHECKOUT_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
        CHECKOUT_HTML_PATH.write_text(html_content, encoding='utf-8')
        
        return {
            "success": True,
            "message": "HTML file uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading HTML: {str(e)}")


@app.post("/build-knowledge-base", response_model=BuildKnowledgeBaseResponse)
async def build_knowledge_base(request: Optional[BuildKnowledgeBaseRequest] = None):
    """Build knowledge base from uploaded documents and HTML."""
    global vector_store, uploaded_documents, html_content
    
    try:
        # Initialize services if needed
        if not initialize_services():
            raise HTTPException(status_code=500, detail="Failed to initialize services")
        
        # Clear existing knowledge base
        vector_store.clear()
        
        ingester = DocumentIngester()
        total_chunks = 0
        
        # Process uploaded documents
        if request and request.document_ids:
            doc_ids_to_process = request.document_ids
        else:
            doc_ids_to_process = list(uploaded_documents.keys())
        
        for doc_id in doc_ids_to_process:
            if doc_id not in uploaded_documents:
                continue
            
            doc = uploaded_documents[doc_id]
            
            try:
                # Parse document
                parsed = ingester.parse_document(
                    content=doc["content"],
                    filename=doc["filename"],
                    doc_type=doc["doc_type"]
                )
                
                # Chunk text
                chunks = ingester.chunk_text(
                    text=parsed["text"],
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP
                )
                
                # Add metadata to chunks
                chunks_with_metadata = []
                for chunk in chunks:
                    chunk_metadata = parsed["metadata"].copy()
                    chunk_metadata["chunk_index"] = chunk["chunk_index"]
                    chunks_with_metadata.append({
                        "text": chunk["text"],
                        "metadata": chunk_metadata
                    })
                
                # Add to vector store
                count = vector_store.add_documents(chunks_with_metadata)
                total_chunks += count
                
            except Exception as e:
                print(f"Error processing document {doc_id}: {str(e)}")
                continue
        
        # Process HTML if provided
        html_to_process = request.html_content if request and request.html_content else html_content
        
        if html_to_process:
            try:
                parsed = ingester.parse_document(
                    content=html_to_process,
                    filename="checkout.html",
                    doc_type=".html"
                )
                
                chunks = ingester.chunk_text(
                    text=parsed["text"],
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP
                )
                
                chunks_with_metadata = []
                for chunk in chunks:
                    chunk_metadata = parsed["metadata"].copy()
                    chunk_metadata["chunk_index"] = chunk["chunk_index"]
                    chunks_with_metadata.append({
                        "text": chunk["text"],
                        "metadata": chunk_metadata
                    })
                
                count = vector_store.add_documents(chunks_with_metadata)
                total_chunks += count
                
            except Exception as e:
                print(f"Error processing HTML: {str(e)}")
        
        if total_chunks == 0:
            raise HTTPException(
                status_code=400,
                detail="No documents were successfully processed. Please upload documents first."
            )
        
        return BuildKnowledgeBaseResponse(
            success=True,
            message=f"Knowledge base built successfully with {total_chunks} chunks",
            chunks_ingested=total_chunks
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building knowledge base: {str(e)}")


@app.post("/generate-test-cases", response_model=GenerateTestCasesResponse)
async def generate_test_cases(request: GenerateTestCasesRequest):
    """Generate test cases based on user query."""
    global test_case_agent
    
    try:
        if test_case_agent is None:
            if not initialize_services():
                raise HTTPException(status_code=500, detail="Services not initialized")
        
        # Generate test cases
        test_cases_dict = test_case_agent.generate_test_cases(
            query=request.query,
            max_test_cases=request.max_test_cases
        )
        
        # Convert to Pydantic models
        test_cases = [TestCase(**tc) for tc in test_cases_dict]
        
        return GenerateTestCasesResponse(
            success=True,
            test_cases=test_cases,
            message=f"Generated {len(test_cases)} test cases"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test cases: {str(e)}")


@app.post("/generate-script", response_model=GenerateScriptResponse)
async def generate_script(request: GenerateScriptRequest):
    """Generate Selenium script from test case."""
    global script_agent, html_content
    
    try:
        if script_agent is None:
            if not initialize_services():
                raise HTTPException(status_code=500, detail="Services not initialized")
        
        # Get HTML content
        html = request.html_content
        if not html:
            # Try to load from file
            if CHECKOUT_HTML_PATH.exists():
                html = CHECKOUT_HTML_PATH.read_text(encoding='utf-8')
            elif html_content:
                html = html_content
            else:
                raise HTTPException(
                    status_code=400,
                    detail="HTML content is required. Please upload checkout.html first."
                )
        
        # Generate script
        script = script_agent.generate_script(
            test_case=request.test_case.dict(),
            html_content=html
        )
        
        return GenerateScriptResponse(
            success=True,
            script=script,
            message="Selenium script generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")


@app.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    global uploaded_documents, html_content
    
    docs = [
        {
            "id": doc_id,
            "filename": doc["filename"],
            "type": doc["doc_type"]
        }
        for doc_id, doc in uploaded_documents.items()
    ]
    
    return {
        "documents": docs,
        "html_uploaded": html_content is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

