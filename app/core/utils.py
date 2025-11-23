"""Shared utility functions."""
import hashlib
from pathlib import Path
from typing import Dict, Any


def generate_document_id(file_path: str, content: str) -> str:
    """Generate a unique document ID based on file path and content."""
    combined = f"{file_path}:{content[:100]}"
    return hashlib.md5(combined.encode()).hexdigest()


def validate_file_type(file_path: str, allowed_types: set) -> bool:
    """Validate if file extension is in allowed types."""
    ext = Path(file_path).suffix.lower()
    return ext in allowed_types


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove path separators and other problematic characters
    return "".join(c for c in filename if c.isalnum() or c in "._- ")


def format_metadata(source: str, doc_type: str, **kwargs) -> Dict[str, Any]:
    """Format metadata dictionary for document chunks."""
    metadata = {
        "source_document": source,
        "type": doc_type,
    }
    metadata.update(kwargs)
    return metadata

