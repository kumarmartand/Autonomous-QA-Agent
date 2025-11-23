"""Tests for document ingestion service."""
import pytest
from app.services.ingestion import DocumentIngester


def test_parse_markdown():
    """Test Markdown parsing."""
    ingester = DocumentIngester()
    content = "# Test Document\n\nThis is a test."
    result = ingester.parse_document(content, "test.md")
    
    assert "text" in result
    assert "metadata" in result
    assert result["metadata"]["type"] == "markdown"
    assert result["text"] == content


def test_parse_text():
    """Test plain text parsing."""
    ingester = DocumentIngester()
    content = "This is plain text content."
    result = ingester.parse_document(content, "test.txt")
    
    assert "text" in result
    assert result["metadata"]["type"] == "text"


def test_parse_json():
    """Test JSON parsing."""
    ingester = DocumentIngester()
    content = '{"key": "value", "number": 123}'
    result = ingester.parse_document(content, "test.json")
    
    assert "text" in result
    assert result["metadata"]["type"] == "json"
    assert "key" in result["text"]


def test_chunk_text():
    """Test text chunking."""
    ingester = DocumentIngester()
    text = "This is a long text. " * 100  # Create long text
    chunks = ingester.chunk_text(text, chunk_size=100, chunk_overlap=20)
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("chunk_index" in chunk for chunk in chunks)


def test_chunk_text_short():
    """Test chunking of short text."""
    ingester = DocumentIngester()
    text = "Short text"
    chunks = ingester.chunk_text(text, chunk_size=1000)
    
    assert len(chunks) == 1
    assert chunks[0]["text"] == text

