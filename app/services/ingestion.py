"""Document ingestion service for parsing various file types."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class DocumentIngester:
    """Service for ingesting and parsing various document types."""
    
    def __init__(self):
        self.supported_types = {".md", ".txt", ".json", ".pdf", ".html"}
    
    def parse_document(self, content: str, filename: str, doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a document and extract text content.
        
        Args:
            content: Raw file content (bytes or string)
            filename: Name of the file
            doc_type: Optional file type override
            
        Returns:
            Dictionary with 'text' and 'metadata' keys
        """
        if doc_type is None:
            doc_type = Path(filename).suffix.lower()
        
        if doc_type == ".md":
            return self._parse_markdown(content, filename)
        elif doc_type == ".txt":
            return self._parse_text(content, filename)
        elif doc_type == ".json":
            return self._parse_json(content, filename)
        elif doc_type == ".pdf":
            return self._parse_pdf(content, filename)
        elif doc_type == ".html":
            return self._parse_html(content, filename)
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")
    
    def _parse_markdown(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse Markdown file."""
        return {
            "text": content,
            "metadata": {
                "source_document": filename,
                "type": "markdown",
                "format": "md"
            }
        }
    
    def _parse_text(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse plain text file."""
        return {
            "text": content,
            "metadata": {
                "source_document": filename,
                "type": "text",
                "format": "txt"
            }
        }
    
    def _parse_json(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse JSON file."""
        try:
            data = json.loads(content)
            # Convert JSON to readable text format
            text = json.dumps(data, indent=2)
            return {
                "text": text,
                "metadata": {
                    "source_document": filename,
                    "type": "json",
                    "format": "json"
                }
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {str(e)}")
    
    def _parse_pdf(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse PDF file."""
        if not PDF_AVAILABLE:
            raise ImportError("PyMuPDF (fitz) is required for PDF parsing. Install with: pip install pymupdf")
        
        try:
            # content should be bytes for PDF
            if isinstance(content, str):
                content = content.encode('latin-1')
            
            doc = fitz.open(stream=content, filetype="pdf")
            text_parts = []
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}\n")
            
            doc.close()
            
            return {
                "text": "\n".join(text_parts),
                "metadata": {
                    "source_document": filename,
                    "type": "pdf",
                    "format": "pdf",
                    "pages": len(doc)
                }
            }
        except Exception as e:
            raise ValueError(f"Error parsing PDF {filename}: {str(e)}")
    
    def _parse_html(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse HTML file, extracting structure and relevant text."""
        if not BS4_AVAILABLE:
            # Fallback: basic regex extraction
            return self._parse_html_basic(content, filename)
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Extract form elements and their attributes
            form_elements = []
            for form in soup.find_all('form'):
                form_info = {
                    "id": form.get('id', ''),
                    "action": form.get('action', ''),
                    "method": form.get('method', 'GET')
                }
                form_elements.append(form_info)
            
            # Extract input elements
            inputs = []
            for inp in soup.find_all(['input', 'button', 'select', 'textarea']):
                inp_info = {
                    "tag": inp.name,
                    "type": inp.get('type', ''),
                    "id": inp.get('id', ''),
                    "name": inp.get('name', ''),
                    "placeholder": inp.get('placeholder', ''),
                    "value": inp.get('value', '')
                }
                inputs.append(inp_info)
            
            # Extract IDs and classes for selectors
            all_ids = [elem.get('id') for elem in soup.find_all(True) if elem.get('id')]
            all_classes = []
            for elem in soup.find_all(True):
                classes = elem.get('class', [])
                if classes:
                    all_classes.extend(classes)
            
            # Build structured text representation
            structured_text = f"""
HTML Structure Analysis for {filename}:

TEXT CONTENT:
{text_content}

FORM ELEMENTS:
{json.dumps(form_elements, indent=2)}

INPUT ELEMENTS:
{json.dumps(inputs, indent=2)}

AVAILABLE SELECTORS:
IDs: {', '.join(set(all_ids))}
Classes: {', '.join(set(all_classes))}

FULL HTML:
{content}
"""
            
            return {
                "text": structured_text,
                "metadata": {
                    "source_document": filename,
                    "type": "html",
                    "format": "html",
                    "form_count": len(form_elements),
                    "input_count": len(inputs),
                    "available_ids": list(set(all_ids)),
                    "available_classes": list(set(all_classes))
                }
            }
        except Exception as e:
            # Fallback to basic parsing
            return self._parse_html_basic(content, filename)
    
    def _parse_html_basic(self, content: str, filename: str) -> Dict[str, Any]:
        """Basic HTML parsing without BeautifulSoup."""
        # Extract IDs
        id_pattern = r'id=["\']([^"\']+)["\']'
        ids = re.findall(id_pattern, content)
        
        # Extract names
        name_pattern = r'name=["\']([^"\']+)["\']'
        names = re.findall(name_pattern, content)
        
        # Extract text content (basic)
        text_pattern = r'>([^<]+)<'
        text_parts = re.findall(text_pattern, content)
        text_content = '\n'.join([t.strip() for t in text_parts if t.strip()])
        
        structured_text = f"""
HTML Structure Analysis for {filename}:

TEXT CONTENT:
{text_content}

AVAILABLE SELECTORS:
IDs: {', '.join(set(ids))}
Names: {', '.join(set(names))}

FULL HTML:
{content}
"""
        
        return {
            "text": structured_text,
            "metadata": {
                "source_document": filename,
                "type": "html",
                "format": "html",
                "available_ids": list(set(ids)),
                "available_names": list(set(names))
            }
        }
    
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            
        Returns:
            List of chunk dictionaries with 'text' and 'chunk_index' keys
        """
        if len(text) <= chunk_size:
            return [{"text": text, "chunk_index": 0}]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence or paragraph boundary
            if end < len(text):
                # Look for sentence endings
                for break_char in ['\n\n', '\n', '. ', '! ', '? ']:
                    last_break = text.rfind(break_char, start, end)
                    if last_break != -1:
                        end = last_break + len(break_char)
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "chunk_index": chunk_index
                })
                chunk_index += 1
            
            # Move start position with overlap
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        return chunks

