"""Pydantic models for API request/response schemas."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentUpload(BaseModel):
    """Schema for document upload."""
    filename: str
    content: str
    doc_type: str


class BuildKnowledgeBaseRequest(BaseModel):
    """Schema for building knowledge base."""
    document_ids: List[str] = Field(default_factory=list)
    html_content: Optional[str] = None


class BuildKnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base build response."""
    success: bool
    message: str
    chunks_ingested: int = 0


class GenerateTestCasesRequest(BaseModel):
    """Schema for test case generation request."""
    query: str = Field(..., description="User query for test case generation")
    max_test_cases: int = Field(default=10, ge=1, le=50)


class TestCase(BaseModel):
    """Schema for a single test case."""
    test_id: str
    feature: str
    test_scenario: str
    preconditions: str
    steps: List[str]
    expected_result: str
    grounded_in: List[str] = Field(..., description="Source documents this test case is based on")


class GenerateTestCasesResponse(BaseModel):
    """Schema for test case generation response."""
    success: bool
    test_cases: List[TestCase]
    message: Optional[str] = None


class GenerateScriptRequest(BaseModel):
    """Schema for Selenium script generation request."""
    test_case: TestCase
    html_content: str = Field(..., description="Full HTML content of checkout.html")


class GenerateScriptResponse(BaseModel):
    """Schema for Selenium script generation response."""
    success: bool
    script: str
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    vector_store_ready: bool = False

