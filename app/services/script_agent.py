"""Selenium script generation agent."""
import json
from typing import Dict, Any
from app.services.vector_store import VectorStore
from app.services.llm_client import LLMClient
from app.core.config import TOP_K_RETRIEVAL


class ScriptAgent:
    """Agent for generating Selenium Python scripts from test cases."""
    
    def __init__(self, vector_store: VectorStore, llm_client: LLMClient):
        """
        Initialize script generation agent.
        
        Args:
            vector_store: Vector store instance for retrieval
            llm_client: LLM client for generation
        """
        self.vector_store = vector_store
        self.llm_client = llm_client
    
    def generate_script(self, test_case: Dict[str, Any], html_content: str) -> str:
        """
        Generate Selenium Python script from test case and HTML structure.
        
        Args:
            test_case: Test case dictionary
            html_content: Full HTML content of checkout.html
            
        Returns:
            Python Selenium script as string
        """
        # Step 1: Retrieve relevant documentation for context
        query = f"{test_case.get('feature', '')} {test_case.get('test_scenario', '')}"
        retrieved_docs = self.vector_store.search(query, top_k=TOP_K_RETRIEVAL)
        
        # Build context from retrieved docs
        doc_context = ""
        if retrieved_docs:
            context_parts = []
            for doc in retrieved_docs:
                source = doc["metadata"].get("source_document", "unknown")
                context_parts.append(f"[Source: {source}]\n{doc['text']}\n")
            doc_context = "\n---\n".join(context_parts)
        
        # Step 2: Extract HTML structure information
        # Parse HTML to get available selectors (IDs, names, classes)
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all IDs
            all_ids = [elem.get('id') for elem in soup.find_all(True) if elem.get('id')]
            
            # Extract all names
            all_names = [elem.get('name') for elem in soup.find_all(True) if elem.get('name')]
            
            # Extract form elements
            form_elements = []
            for elem in soup.find_all(['input', 'button', 'select', 'textarea']):
                form_elements.append({
                    "tag": elem.name,
                    "type": elem.get('type', ''),
                    "id": elem.get('id', ''),
                    "name": elem.get('name', ''),
                    "class": ' '.join(elem.get('class', []))
                })
            
            html_structure = f"""
AVAILABLE HTML SELECTORS:
IDs: {', '.join(set(all_ids))}
Names: {', '.join(set(all_names))}

FORM ELEMENTS:
{json.dumps(form_elements, indent=2)}
"""
        except:
            # Fallback if BeautifulSoup not available
            import re
            id_pattern = r'id=["\']([^"\']+)["\']'
            name_pattern = r'name=["\']([^"\']+)["\']'
            ids = re.findall(id_pattern, html_content)
            names = re.findall(name_pattern, html_content)
            html_structure = f"""
AVAILABLE HTML SELECTORS:
IDs: {', '.join(set(ids))}
Names: {', '.join(set(names))}
"""
        
        # Step 3: Construct prompt for LLM
        system_prompt = """You are an expert Selenium (Python) automation engineer. 
Your task is to generate clean, runnable Selenium Python scripts based on test cases and HTML structure.

CRITICAL REQUIREMENTS:
1. Use ONLY the selectors (IDs, names, classes) that are ACTUALLY present in the provided HTML.
2. Prefer IDs and names over CSS selectors when available (more reliable).
3. Use explicit waits (WebDriverWait) for dynamic elements.
4. Include proper setup and teardown (at least driver.quit()).
5. Make the script self-contained and runnable.
6. Follow the test steps exactly as specified in the test case.
7. Add appropriate assertions to verify expected results.
8. Use clear, descriptive variable names.
9. Include comments explaining key actions.

Script structure:
- Import necessary Selenium modules
- Set up WebDriver (use ChromeDriver by default)
- Navigate to the page (use a local file path or URL)
- Execute test steps with proper waits
- Assert expected results
- Clean up (driver.quit())

Return ONLY the Python code, no markdown code blocks, no explanations."""

        user_prompt = f"""Generate a Selenium Python script for the following test case:

TEST CASE:
Test ID: {test_case.get('test_id', 'N/A')}
Feature: {test_case.get('feature', 'N/A')}
Scenario: {test_case.get('test_scenario', 'N/A')}
Preconditions: {test_case.get('preconditions', 'N/A')}
Steps:
{chr(10).join(f"  {i+1}. {step}" for i, step in enumerate(test_case.get('steps', [])))}
Expected Result: {test_case.get('expected_result', 'N/A')}

HTML STRUCTURE:
{html_structure}

RELEVANT DOCUMENTATION:
{doc_context if doc_context else "No additional documentation context."}

Generate a complete, runnable Selenium Python script that:
1. Uses the actual selectors from the HTML structure above
2. Follows all test steps
3. Verifies the expected result
4. Is ready to run (assume checkout.html is in the same directory or provide path)

Return ONLY the Python code."""

        # Step 4: Generate script using LLM
        print("Generating Selenium script with LLM...")
        try:
            response = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for more deterministic code
            )
            
            # Clean up response (remove markdown code blocks if present)
            script = response.strip()
            
            # Remove markdown code block markers if present
            if script.startswith("```python"):
                script = script[9:]
            elif script.startswith("```"):
                script = script[3:]
            
            if script.endswith("```"):
                script = script[:-3]
            
            script = script.strip()
            
            # Ensure basic imports are present
            if "from selenium" not in script:
                # Prepend basic imports if missing
                basic_imports = """from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

"""
                script = basic_imports + script
            
            print("Selenium script generated successfully")
            return script
            
        except Exception as e:
            raise Exception(f"Error generating Selenium script: {str(e)}")

