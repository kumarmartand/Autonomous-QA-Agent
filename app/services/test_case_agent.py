"""Test case generation agent using RAG."""
import json
from typing import List, Dict, Any
from app.services.vector_store import VectorStore
from app.services.llm_client import LLMClient
from app.core.config import TOP_K_RETRIEVAL


class TestCaseAgent:
    """Agent for generating test cases grounded in documentation."""
    
    def __init__(self, vector_store: VectorStore, llm_client: LLMClient):
        """
        Initialize test case agent.
        
        Args:
            vector_store: Vector store instance for retrieval
            llm_client: LLM client for generation
        """
        self.vector_store = vector_store
        self.llm_client = llm_client
    
    def generate_test_cases(self, query: str, max_test_cases: int = 10) -> List[Dict[str, Any]]:
        """
        Generate test cases based on user query and retrieved context.
        
        Args:
            query: User query describing what test cases to generate
            max_test_cases: Maximum number of test cases to generate
            
        Returns:
            List of test case dictionaries
        """
        # Step 1: Retrieve relevant context from vector store
        print(f"Retrieving relevant context for query: {query}")
        retrieved_docs = self.vector_store.search(query, top_k=TOP_K_RETRIEVAL)
        
        if not retrieved_docs:
            raise ValueError("No relevant documents found in knowledge base. Please build the knowledge base first.")
        
        # Step 2: Build context string from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc["metadata"].get("source_document", "unknown")
            context_parts.append(f"[Document {i} - Source: {source}]\n{doc['text']}\n")
        
        context = "\n---\n".join(context_parts)
        
        # Step 3: Construct prompt for LLM
        system_prompt = """You are an expert QA engineer specializing in test case generation. 
Your task is to generate comprehensive test cases based ONLY on the provided documentation and requirements.

CRITICAL RULES:
1. ONLY use information from the provided context documents. Do NOT invent or assume features that are not explicitly mentioned.
2. Every test case MUST include a "Grounded_In" field listing the source document(s) it is based on.
3. Test cases should cover both positive (happy path) and negative (error cases) scenarios.
4. Be specific and actionable - each test case should be executable.
5. Reference actual features, field names, and behaviors from the documentation.

Output format: Return a valid JSON array of test cases. Each test case must have:
- test_id: Unique identifier (e.g., "TC-001")
- feature: Feature or component being tested
- test_scenario: Brief description of what is being tested
- preconditions: What must be true before the test runs
- steps: Array of step-by-step instructions
- expected_result: What should happen when the test passes
- grounded_in: Array of source document names this test case is based on

Example format:
[
  {
    "test_id": "TC-001",
    "feature": "Discount Code",
    "test_scenario": "Apply valid discount code",
    "preconditions": "User has items in cart",
    "steps": ["Navigate to checkout", "Enter discount code 'SAVE15'", "Click apply"],
    "expected_result": "Discount of 15% is applied to total",
    "grounded_in": ["product_specs.md"]
  }
]"""

        user_prompt = f"""Based on the following documentation, generate {max_test_cases} test cases for: {query}

DOCUMENTATION CONTEXT:
{context}

Generate test cases that are:
- Strictly grounded in the provided documentation
- Cover both positive and negative scenarios
- Include clear steps and expected results
- Reference source documents in the "grounded_in" field

Return ONLY a valid JSON array, no additional text or explanation."""

        # Step 4: Generate test cases using LLM
        print("Generating test cases with LLM...")
        try:
            response = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            # Step 5: Parse JSON response
            # Try to extract JSON from response (in case LLM adds extra text)
            response = response.strip()
            
            # Find JSON array in response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                test_cases = json.loads(json_str)
            else:
                # Try parsing entire response
                test_cases = json.loads(response)
            
            # Validate and format test cases
            formatted_test_cases = []
            for tc in test_cases:
                if isinstance(tc, dict):
                    # Ensure all required fields exist
                    formatted_tc = {
                        "test_id": tc.get("test_id", f"TC-{len(formatted_test_cases) + 1:03d}"),
                        "feature": tc.get("feature", "Unknown"),
                        "test_scenario": tc.get("test_scenario", ""),
                        "preconditions": tc.get("preconditions", ""),
                        "steps": tc.get("steps", []),
                        "expected_result": tc.get("expected_result", ""),
                        "grounded_in": tc.get("grounded_in", [])
                    }
                    formatted_test_cases.append(formatted_tc)
            
            print(f"Generated {len(formatted_test_cases)} test cases")
            return formatted_test_cases
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {response[:500]}")
        except Exception as e:
            raise Exception(f"Error generating test cases: {str(e)}")

