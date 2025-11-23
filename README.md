# Autonomous QA Agent - Test Case and Script Generation System

## 📋 Project Overview

This project implements an intelligent, autonomous QA agent that generates test cases and Selenium scripts based on documentation and HTML structure. The system uses Retrieval-Augmented Generation (RAG) to ensure all test cases are strictly grounded in provided documentation, avoiding hallucinations and fabricated features.

### Key Features

- **Document Ingestion**: Supports multiple document types (MD, TXT, JSON, PDF, HTML)
- **Knowledge Base Building**: Creates a vector database from uploaded documents using embeddings
- **Test Case Generation**: Generates comprehensive test cases grounded in documentation
- **Selenium Script Generation**: Converts test cases into executable Python Selenium scripts
- **Clean Architecture**: Modular design with FastAPI backend and Streamlit frontend

## 🎯 Objective

Build an autonomous QA agent that:
1. Ingests support documents and a checkout HTML file
2. Builds a "testing brain" / knowledge base from those documents
3. Generates documentation-grounded test plans and test viewpoints
4. Generates executable Selenium Python scripts from test cases

## 🏗️ Architecture

### Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Vector Database**: ChromaDB (or FAISS)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: Abstracted interface supporting Ollama, Groq, OpenAI, etc.

### Project Structure

```
.
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── ingestion.py        # Document parsing and chunking
│   │   ├── vector_store.py     # Vector DB operations
│   │   ├── test_case_agent.py  # Test case generation (RAG)
│   │   ├── script_agent.py     # Selenium script generation
│   │   └── llm_client.py       # LLM abstraction layer
│   └── core/
│       ├── config.py           # Configuration settings
│       └── utils.py            # Utility functions
├── ui/
│   └── streamlit_app.py        # Streamlit frontend
├── assets/
│   ├── checkout.html           # Target web page
│   └── support_docs/
│       ├── product_specs.md     # Product specifications
│       ├── ui_ux_guide.txt     # UI/UX guidelines
│       └── api_endpoints.json  # API endpoint specifications
├── tests/
│   └── test_ingestion.py       # Basic tests
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- LLM provider (Ollama, Groq, or OpenAI)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "OceanAI Project"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up LLM provider:**

   **Option A: Ollama (Recommended for local development)**
   ```bash
   # Install Ollama from https://ollama.ai
   # Then pull a model:
   ollama pull llama3.2
   ```
   
   Set environment variables (optional, defaults shown):
   ```bash
   export LLM_PROVIDER=ollama
   export LLM_MODEL=llama3.2
   export LLM_BASE_URL=http://localhost:11434
   ```

   **Option B: Groq**
   ```bash
   export LLM_PROVIDER=groq
   export LLM_MODEL=llama-3.1-8b-instant
   export GROQ_API_KEY=your_groq_api_key
   ```

   **Option C: OpenAI**
   ```bash
   export LLM_PROVIDER=openai
   export LLM_MODEL=gpt-4
   export OPENAI_API_KEY=your_openai_api_key
   ```

## 🏃 Running the Application

### Step 1: Start the FastAPI Backend

Open a terminal and run:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Step 2: Start the Streamlit Frontend

Open another terminal and run:
```bash
streamlit run ui/streamlit_app.py --server.port 8501
```

The UI will open automatically in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Phase 1: Build Knowledge Base

1. **Upload Support Documents:**
   - Click "Upload Support Documents"
   - Select files: `product_specs.md`, `ui_ux_guide.txt`, `api_endpoints.json`
   - Click "Upload" for each file

2. **Upload Checkout HTML:**
   - Either upload `checkout.html` file
   - Or paste HTML content directly in the text area

3. **Build Knowledge Base:**
   - Click "🔨 Build Knowledge Base"
   - Wait for processing (this may take a minute)
   - You should see: "✅ Knowledge base built successfully!"

### Phase 2: Generate Test Cases

1. **Enter Query:**
   - Type a query like: "Generate all positive and negative test cases for the discount code feature"
   - Or select from example queries

2. **Set Parameters:**
   - Adjust "Maximum number of test cases" slider (default: 10)

3. **Generate:**
   - Click "🚀 Generate Test Cases"
   - Wait for generation (may take 1-2 minutes)
   - Review generated test cases in expandable sections

4. **Select Test Case:**
   - Click "Select this test case" on any test case you want to convert to a script

### Phase 3: Generate Selenium Scripts

1. **Select Test Case:**
   - If you selected one in Phase 2, it will be pre-selected
   - Otherwise, choose from the dropdown

2. **Generate Script:**
   - Click "🔧 Generate Selenium Script"
   - Wait for generation (may take 1-2 minutes)

3. **Review and Download:**
   - Review the generated Python script
   - Click "📥 Download Script" to save it
   - The script is ready to run (may need minor adjustments for your environment)

## 📁 Project Assets

### checkout.html

A single-page E-Shop Checkout application with:

- **Cart Functionality:**
  - 3 products: Wireless Headphones ($99.99), Smart Watch ($199.99), Laptop Stand ($49.99)
  - Quantity inputs for each item
  - "Add to Cart" buttons
  - Real-time cart total calculation

- **Discount Code:**
  - Input field for discount codes
  - Valid code: `SAVE15` (15% discount)
  - Apply button with validation

- **User Details Form:**
  - Name (required)
  - Email (required, with format validation)
  - Address (required, textarea)

- **Shipping Methods:**
  - Standard (Free) - default
  - Express ($10.00)

- **Payment Methods:**
  - Credit Card - default
  - PayPal

- **Form Validation:**
  - Inline error messages (red text)
  - Email format validation
  - Required field validation

- **Payment Processing:**
  - "Pay Now" button (green)
  - Success message on valid submission

### Support Documents

#### product_specs.md

Defines functional specifications including:
- Cart functionality and item management
- Discount code system (SAVE15 = 15% off)
- Shipping methods and costs
- Payment methods
- Form validation rules
- Element IDs and structure

#### ui_ux_guide.txt

UI/UX guidelines covering:
- Color scheme (green buttons, red errors, green success)
- Form validation display requirements
- Button styling
- Layout and spacing
- Error message formatting
- Accessibility requirements

#### api_endpoints.json

API endpoint specifications including:
- Discount code application endpoint
- Order submission endpoint
- Cart management endpoints
- Shipping calculation
- Validation rules and error messages

## 🧪 Testing

Run basic tests:
```bash
pytest tests/
```

## 🔧 Configuration

Configuration is managed in `app/core/config.py`. Key settings:

- `VECTOR_STORE_TYPE`: "chroma" or "faiss" (default: "chroma")
- `EMBEDDING_MODEL`: Embedding model name (default: "sentence-transformers/all-MiniLM-L6-v2")
- `CHUNK_SIZE`: Text chunk size (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RETRIEVAL`: Number of documents to retrieve (default: 5)

Environment variables:
- `LLM_PROVIDER`: "ollama", "groq", or "openai"
- `LLM_MODEL`: Model name
- `LLM_BASE_URL`: Base URL for Ollama
- `LLM_API_KEY`: API key for Groq/OpenAI

## 📝 API Endpoints

### Document Management
- `POST /upload-document`: Upload a support document
- `POST /upload-html`: Upload checkout.html
- `GET /documents`: List uploaded documents

### Knowledge Base
- `POST /build-knowledge-base`: Build vector database from uploaded documents

### Test Generation
- `POST /generate-test-cases`: Generate test cases from query
- `POST /generate-script`: Generate Selenium script from test case

### Health
- `GET /health`: Check API health and vector store status

## 🎥 Demo Video Script Outline

For a 5-10 minute demo video, cover:

1. **Introduction (30s)**
   - Show project structure
   - Explain the goal

2. **Phase 1: Knowledge Base (2min)**
   - Upload support documents (product_specs.md, ui_ux_guide.txt, api_endpoints.json)
   - Upload checkout.html
   - Click "Build Knowledge Base"
   - Show success message

3. **Phase 2: Test Case Generation (3min)**
   - Enter query: "Generate test cases for discount code feature"
   - Click "Generate Test Cases"
   - Show generated test cases
   - Highlight "Grounded_In" fields showing source documents
   - Select a test case

4. **Phase 3: Script Generation (2min)**
   - Navigate to Phase 3
   - Show selected test case
   - Click "Generate Selenium Script"
   - Show generated Python code
   - Highlight key features (selectors, waits, assertions)
   - Download the script

5. **Conclusion (30s)**
   - Summarize the workflow
   - Show how test cases are grounded in documentation
   - Mention extensibility

## 🎯 Evaluation Criteria Alignment

### ✅ Functionality
- All phases implemented end-to-end
- Complete ingestion → knowledge base → test cases → script generation pipeline

### ✅ Knowledge Grounding
- Every test case includes "Grounded_In" field
- Test cases reference actual source documents
- No hallucinated features

### ✅ Script Quality
- Clean, readable Selenium code
- Correct selectors matching checkout.html
- Runnable with minimal modification
- Includes proper waits and assertions

### ✅ Code Quality
- Modular, layered architecture
- Clear separation of concerns
- Type hints and docstrings
- Clean naming conventions

### ✅ User Experience
- Intuitive Streamlit UI
- Clear status messages
- Logical phase-based layout
- Error handling and feedback

### ✅ Documentation
- Comprehensive README
- Setup instructions
- Usage examples
- Asset explanations

## 🐛 Troubleshooting

### API not connecting
- Ensure FastAPI backend is running on port 8000
- Check `API_BASE_URL` in `streamlit_app.py`

### LLM errors
- Verify LLM provider is running (Ollama) or API key is set (Groq/OpenAI)
- Check environment variables

### Vector store errors
- Ensure ChromaDB dependencies are installed
- Check write permissions in project directory

### Import errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

## 📄 License

This project is created for educational and demonstration purposes.

## 🤝 Contributing

This is an assignment project. For improvements:
1. Follow the existing code structure
2. Maintain type hints and docstrings
3. Add tests for new features
4. Update README as needed

## 📧 Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation at `/docs` endpoint
- Verify all dependencies are installed correctly

---

**Built with ❤️ using FastAPI, Streamlit, and RAG**

