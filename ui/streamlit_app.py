"""Streamlit UI for QA Agent."""
import streamlit as st
import requests
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

# API configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="QA Agent - Autonomous Test Case Generator",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "selected_test_case" not in st.session_state:
    st.session_state.selected_test_case = None
if "knowledge_base_built" not in st.session_state:
    st.session_state.knowledge_base_built = False


def check_api_health() -> bool:
    """Check if API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def upload_document(file) -> Optional[Dict]:
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/upload-document", files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error uploading document: {str(e)}")
        return None


def upload_html(file) -> bool:
    """Upload HTML file to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/upload-html", files=files)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error uploading HTML: {str(e)}")
        return False


def build_knowledge_base(html_content: Optional[str] = None) -> bool:
    """Build knowledge base."""
    try:
        payload = {}
        if html_content:
            payload["html_content"] = html_content
        
        response = requests.post(
            f"{API_BASE_URL}/build-knowledge-base",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        st.error(f"Error building knowledge base: {str(e)}")
        return False


def generate_test_cases(query: str, max_test_cases: int = 10) -> Optional[List[Dict]]:
    """Generate test cases."""
    try:
        payload = {
            "query": query,
            "max_test_cases": max_test_cases
        }
        response = requests.post(
            f"{API_BASE_URL}/generate-test-cases",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            return result.get("test_cases", [])
        return None
    except Exception as e:
        st.error(f"Error generating test cases: {str(e)}")
        return None


def generate_script(test_case: Dict, html_content: Optional[str] = None) -> Optional[str]:
    """Generate Selenium script."""
    try:
        payload = {
            "test_case": test_case,
            "html_content": html_content
        }
        response = requests.post(
            f"{API_BASE_URL}/generate-script",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            return result.get("script", "")
        return None
    except Exception as e:
        st.error(f"Error generating script: {str(e)}")
        return None


# Main UI
st.title("🤖 Autonomous QA Agent")
st.markdown("**Test Case and Selenium Script Generation System**")

# Check API health
if not check_api_health():
    st.error("⚠️ API server is not running. Please start the FastAPI backend first.")
    st.info("Run: `uvicorn app.main:app --reload`")
    st.stop()

# Sidebar for navigation
st.sidebar.title("Navigation")
phase = st.sidebar.radio(
    "Select Phase",
    ["Phase 1: Knowledge Base", "Phase 2: Test Cases", "Phase 3: Selenium Scripts"]
)

# Phase 1: Knowledge Base Ingestion
if phase == "Phase 1: Knowledge Base":
    st.header("📚 Phase 1: Build Knowledge Base")
    st.markdown("Upload support documents and checkout.html to build the knowledge base.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Support Documents")
        st.markdown("Upload documentation files (MD, TXT, JSON, PDF)")
        
        uploaded_files = st.file_uploader(
            "Choose documents",
            type=["md", "txt", "json", "pdf", "html"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for file in uploaded_files:
                if st.button(f"Upload {file.name}", key=f"upload_{file.name}"):
                    result = upload_document(file)
                    if result:
                        st.success(f"✅ {result.get('message', 'Uploaded successfully')}")
    
    with col2:
        st.subheader("Upload Checkout HTML")
        st.markdown("Upload or paste the checkout.html file")
        
        html_file = st.file_uploader(
            "Choose HTML file",
            type=["html"],
            key="html_uploader"
        )
        
        if html_file:
            if st.button("Upload HTML", key="upload_html"):
                if upload_html(html_file):
                    st.success("✅ HTML file uploaded successfully")
        
        st.markdown("---")
        st.markdown("**OR paste HTML directly:**")
        html_paste = st.text_area(
            "Paste HTML content",
            height=200,
            key="html_paste"
        )
    
    st.markdown("---")
    
    # Build Knowledge Base button
    if st.button("🔨 Build Knowledge Base", type="primary", use_container_width=True):
        with st.spinner("Building knowledge base... This may take a few moments."):
            html_content_for_build = html_paste if html_paste else None
            success = build_knowledge_base(html_content_for_build)
            
            if success:
                st.session_state.knowledge_base_built = True
                st.success("✅ Knowledge base built successfully!")
                st.balloons()
            else:
                st.error("❌ Failed to build knowledge base. Please check your documents.")

# Phase 2: Test Case Generation
elif phase == "Phase 2: Test Cases":
    st.header("🧪 Phase 2: Generate Test Cases")
    st.markdown("Generate test cases grounded in your documentation.")
    
    if not st.session_state.knowledge_base_built:
        st.warning("⚠️ Please build the knowledge base first (Phase 1).")
    
    # Query input
    st.subheader("Test Case Query")
    example_queries = [
        "Generate all positive and negative test cases for the discount code feature.",
        "Create test cases for form validation including email validation and required fields.",
        "Generate test cases for cart functionality including add to cart and quantity updates.",
        "Create test cases for shipping method selection and payment methods.",
    ]
    
    selected_example = st.selectbox(
        "Or select an example query:",
        ["Custom query"] + example_queries,
        key="example_query"
    )
    
    if selected_example != "Custom query":
        query = selected_example
    else:
        query = st.text_area(
            "Enter your query for test case generation:",
            height=100,
            placeholder="e.g., Generate test cases for discount code feature..."
        )
    
    max_test_cases = st.slider("Maximum number of test cases", 1, 20, 10)
    
    if st.button("🚀 Generate Test Cases", type="primary", use_container_width=True):
        if not query:
            st.error("Please enter a query.")
        else:
            with st.spinner("Generating test cases... This may take a minute."):
                test_cases = generate_test_cases(query, max_test_cases)
                
                if test_cases:
                    st.session_state.test_cases = test_cases
                    st.success(f"✅ Generated {len(test_cases)} test cases!")
                    
                    # Display test cases
                    st.subheader("Generated Test Cases")
                    
                    for i, tc in enumerate(test_cases):
                        with st.expander(f"**{tc.get('test_id', f'TC-{i+1}')}**: {tc.get('feature', 'Unknown')} - {tc.get('test_scenario', '')}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**Feature:** {tc.get('feature', 'N/A')}")
                                st.markdown(f"**Scenario:** {tc.get('test_scenario', 'N/A')}")
                                st.markdown(f"**Preconditions:** {tc.get('preconditions', 'N/A')}")
                            
                            with col2:
                                st.markdown(f"**Expected Result:** {tc.get('expected_result', 'N/A')}")
                                st.markdown(f"**Grounded In:** {', '.join(tc.get('grounded_in', []))}")
                            
                            st.markdown("**Steps:**")
                            for j, step in enumerate(tc.get('steps', []), 1):
                                st.markdown(f"{j}. {step}")
                            
                            # Select button
                            if st.button(f"Select this test case", key=f"select_{i}"):
                                st.session_state.selected_test_case = tc
                                st.success(f"✅ Selected: {tc.get('test_id', 'N/A')}")
                                st.info("Navigate to Phase 3 to generate the Selenium script.")
                else:
                    st.error("❌ Failed to generate test cases.")

# Phase 3: Selenium Script Generation
elif phase == "Phase 3: Selenium Scripts":
    st.header("🐍 Phase 3: Generate Selenium Scripts")
    st.markdown("Generate executable Selenium Python scripts from test cases.")
    
    if not st.session_state.test_cases:
        st.warning("⚠️ Please generate test cases first (Phase 2).")
        st.stop()
    
    # Test case selection
    st.subheader("Select Test Case")
    
    if st.session_state.selected_test_case:
        selected_tc = st.session_state.selected_test_case
        st.info(f"Currently selected: **{selected_tc.get('test_id', 'N/A')}** - {selected_tc.get('test_scenario', '')}")
    else:
        test_case_options = {
            f"{tc.get('test_id', f'TC-{i}')}: {tc.get('feature', 'Unknown')}": tc
            for i, tc in enumerate(st.session_state.test_cases)
        }
        
        selected_key = st.selectbox(
            "Choose a test case:",
            list(test_case_options.keys())
        )
        selected_tc = test_case_options[selected_key]
    
    # Display selected test case details
    with st.expander("View Test Case Details"):
        st.json(selected_tc)
    
    # Generate script button
    if st.button("🔧 Generate Selenium Script", type="primary", use_container_width=True):
        with st.spinner("Generating Selenium script... This may take a minute."):
            script = generate_script(selected_tc)
            
            if script:
                st.success("✅ Selenium script generated successfully!")
                
                st.subheader("Generated Script")
                st.code(script, language="python")
                
                # Download button
                st.download_button(
                    label="📥 Download Script",
                    data=script,
                    file_name=f"{selected_tc.get('test_id', 'test')}_selenium.py",
                    mime="text/x-python"
                )
            else:
                st.error("❌ Failed to generate script.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>Autonomous QA Agent - Test Case and Script Generation System</p>
    </div>
    """,
    unsafe_allow_html=True
)

