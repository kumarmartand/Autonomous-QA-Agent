"""Vector store service for document embeddings and retrieval."""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class VectorStore:
    """Vector store for document embeddings and similarity search."""
    
    def __init__(self, store_type: str = "chroma", embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2", 
                 store_dir: Optional[Path] = None):
        """
        Initialize vector store.
        
        Args:
            store_type: "chroma" or "faiss"
            embedding_model: Model name for sentence transformers
            store_dir: Directory to store vector database
        """
        if not ST_AVAILABLE:
            raise ImportError("sentence-transformers is required. Install with: pip install sentence-transformers")
        
        self.store_type = store_type.lower()
        self.embedding_model_name = embedding_model
        
        # Load embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize vector store
        if self.store_type == "chroma":
            if not CHROMA_AVAILABLE:
                raise ImportError("chromadb is required. Install with: pip install chromadb")
            self._init_chroma(store_dir)
        elif self.store_type == "faiss":
            if not FAISS_AVAILABLE:
                raise ImportError("faiss-cpu is required. Install with: pip install faiss-cpu")
            self._init_faiss(store_dir)
        else:
            raise ValueError(f"Unsupported store type: {store_type}")
    
    def _init_chroma(self, store_dir: Optional[Path]):
        """Initialize ChromaDB vector store."""
        if store_dir:
            store_path = store_dir / "chroma_db"
        else:
            store_path = Path("./chroma_db")
        
        store_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(store_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="qa_agent_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"ChromaDB initialized at {store_path}")
    
    def _init_faiss(self, store_dir: Optional[Path]):
        """Initialize FAISS vector store."""
        if store_dir:
            self.store_dir = store_dir
        else:
            self.store_dir = Path("./faiss_db")
        
        self.store_dir.mkdir(parents=True, exist_ok=True)
        
        self.index = None
        self.metadata_store = []
        self.index_path = self.store_dir / "faiss.index"
        self.metadata_path = self.store_dir / "metadata.json"
        
        # Load existing index if available
        if self.index_path.exists() and self.metadata_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'r') as f:
                self.metadata_store = json.load(f)
            print(f"FAISS index loaded from {self.index_path}")
        else:
            print("Creating new FAISS index")
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add document chunks to vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata' keys
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk.get("metadata", {}) for chunk in chunks]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        if self.store_type == "chroma":
            # Add to ChromaDB
            ids = [f"chunk_{i}_{hash(chunk['text'])}" for i, chunk in enumerate(chunks)]
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            return len(chunks)
        
        elif self.store_type == "faiss":
            # Add to FAISS
            embeddings_np = np.array(embeddings).astype('float32')
            
            if self.index is None:
                # Create new index
                dimension = embeddings_np.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
            
            # Add vectors
            self.index.add(embeddings_np)
            
            # Store metadata
            for i, metadata in enumerate(metadatas):
                metadata_entry = {
                    "index": len(self.metadata_store),
                    "text": texts[i],
                    "metadata": metadata
                }
                self.metadata_store.append(metadata_entry)
            
            # Save index and metadata
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata_store, f, indent=2)
            
            return len(chunks)
    
    def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters (ChromaDB only)
            
        Returns:
            List of result dictionaries with 'text', 'metadata', and 'score' keys
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        if self.store_type == "chroma":
            # Search in ChromaDB
            where = filter_metadata if filter_metadata else None
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": 1 - results['distances'][0][i] if 'distances' in results else 0.0
                    })
            
            return formatted_results
        
        elif self.store_type == "faiss":
            # Search in FAISS
            if self.index is None or self.index.ntotal == 0:
                return []
            
            query_embedding_np = np.array([query_embedding]).astype('float32')
            
            # Search
            k = min(top_k, self.index.ntotal)
            distances, indices = self.index.search(query_embedding_np, k)
            
            # Format results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata_store):
                    metadata_entry = self.metadata_store[idx]
                    # Convert L2 distance to similarity score (approximate)
                    score = 1.0 / (1.0 + distances[0][i])
                    results.append({
                        "text": metadata_entry["text"],
                        "metadata": metadata_entry["metadata"],
                        "score": score
                    })
            
            # Sort by score descending
            results.sort(key=lambda x: x["score"], reverse=True)
            return results
    
    def clear(self):
        """Clear all documents from the vector store."""
        if self.store_type == "chroma":
            # Delete and recreate collection
            try:
                self.client.delete_collection("qa_agent_documents")
            except:
                pass
            self.collection = self.client.get_or_create_collection(
                name="qa_agent_documents",
                metadata={"hnsw:space": "cosine"}
            )
        elif self.store_type == "faiss":
            self.index = None
            self.metadata_store = []
            if self.index_path.exists():
                self.index_path.unlink()
            if self.metadata_path.exists():
                self.metadata_path.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if self.store_type == "chroma":
            count = self.collection.count()
            return {
                "store_type": "chroma",
                "document_count": count,
                "embedding_dim": self.embedding_dim
            }
        elif self.store_type == "faiss":
            count = self.index.ntotal if self.index else 0
            return {
                "store_type": "faiss",
                "document_count": count,
                "embedding_dim": self.embedding_dim
            }

