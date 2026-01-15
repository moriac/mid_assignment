"""
Hierarchical Auto-Merging Retriever for Insurance Claim PDF

This module implements LlamaIndex's AutoMergingRetriever pattern with:
- HierarchicalNodeParser for creating a chunk hierarchy (2048/512/128)
- Leaf nodes stored in Supabase vector store
- All nodes stored in a docstore for auto-merging
- Integration with existing Supabase configuration
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# LlamaIndex imports
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import PyMuPDFReader

# Optional: Supabase vector store (requires PostgreSQL connection)
try:
    from llama_index.vector_stores.supabase import SupabaseVectorStore
    SUPABASE_VECTOR_STORE_AVAILABLE = True
except ImportError:
    SUPABASE_VECTOR_STORE_AVAILABLE = False

# Make Supabase imports conditional
try:
    from supabase import create_client, Client
    SUPABASE_CLIENT_AVAILABLE = True
except ImportError:
    SUPABASE_CLIENT_AVAILABLE = False
    print("⚠️ Supabase client not available (install with: pip install supabase)")

# Import metadata extraction
from extract_claim_metadata import load_claim_document_with_metadata

load_dotenv()


class HierarchicalClaimRetriever:
    """
    Manages hierarchical indexing and retrieval for insurance claim PDFs.
    
    Uses HierarchicalNodeParser to create a 3-level hierarchy:
    - Level 1: 2048 characters (root nodes)
    - Level 2: 512 characters (mid-level nodes)
    - Level 3: 128 characters (leaf nodes)
    
    Leaf nodes are indexed in Supabase vector store, while all nodes are
    stored in a docstore for auto-merging during retrieval.
    """
    
    def __init__(
        self,
        pdf_path: str = "insurance_claim_case.pdf",
        table_name: str = "hierarchical_chunks",
        chunk_sizes: Optional[list] = None,
        use_supabase_vector_store: bool = False  # Changed default to False
    ):
        """
        Initialize the hierarchical retriever.
        
        Args:
            pdf_path: Path to the insurance claim PDF file
            table_name: Supabase table name for storing leaf node embeddings
            chunk_sizes: List of chunk sizes for hierarchy levels (default: [2048, 512, 128])
            use_supabase_vector_store: If True, use Supabase vector store (requires SUPABASE_DB_PASSWORD)
                                      If False, use in-memory vector store (default)
        """
        self.pdf_path = pdf_path
        self.table_name = table_name
        self.chunk_sizes = chunk_sizes or [2048, 512, 128]
        self.use_supabase_vector_store = use_supabase_vector_store
        
        # Initialize components
        # Only initialize Supabase if needed and available
        if self.use_supabase_vector_store:
            if not SUPABASE_CLIENT_AVAILABLE:
                raise ImportError("Supabase storage requested but supabase package not installed")
            self.supabase_client = self._init_supabase()
        else:
            self.supabase_client = None  # ✅ No Supabase needed
        
        self.embeddings = self._init_embeddings()
        self.llm = self._init_llm()
        
        # Storage components (initialized during build)
        self.docstore = None
        self.vector_store = None
        self.storage_context = None
        self.base_index = None
        self.retriever = None
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client using environment variables."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            raise ValueError(
                "Missing Supabase credentials. Please set SUPABASE_URL and "
                "SUPABASE_SERVICE_KEY in your .env file"
            )
        
        return create_client(url, key)
    
    def _init_embeddings(self) -> OpenAIEmbedding:
        """Initialize OpenAI embeddings."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in .env file")
        
        return OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=api_key
        )
    
    def _init_llm(self) -> OpenAI:
        """Initialize OpenAI LLM."""
        return OpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def load_pdf(self) -> list[Document]:
        """
        Load and parse the insurance claim PDF with metadata extraction.
        
        Returns:
            List of Document objects with metadata attached
        """
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        # Load document with metadata extraction
        print(f"Loading PDF with metadata extraction...")
        document = load_claim_document_with_metadata(self.pdf_path)
        
        print(f"✓ Document loaded with {len(document.metadata)} metadata fields")
        
        return [document]
    
    def build_hierarchy(self, documents: list[Document]) -> tuple:
        """
        Build the hierarchical node structure.
        
        Args:
            documents: List of documents to parse
            
        Returns:
            Tuple of (all_nodes, leaf_nodes)
        """
        print(f"Building hierarchy with chunk sizes: {self.chunk_sizes}")
        
        # Store metadata separately to avoid chunking issues
        doc_metadata = documents[0].metadata if documents else {}
        
        # Create hierarchical parser with metadata exclusion
        node_parser = HierarchicalNodeParser.from_defaults(
            chunk_sizes=self.chunk_sizes,
            include_metadata=False  # Don't include metadata in chunk size calculation
        )
        
        # Parse documents into hierarchical nodes
        nodes = node_parser.get_nodes_from_documents(documents)
        print(f"Created {len(nodes)} total nodes")
        
        # Manually attach metadata to all nodes after parsing
        for node in nodes:
            node.metadata.update(doc_metadata)
        
        # Extract leaf nodes (smallest chunks that go into vector store)
        leaf_nodes = get_leaf_nodes(nodes)
        print(f"Extracted {len(leaf_nodes)} leaf nodes for vector indexing")
        print(f"✓ Metadata attached to all {len(nodes)} nodes")
        
        return nodes, leaf_nodes
    
    def setup_storage(self, all_nodes: list) -> None:
        """
        Set up storage components: docstore and vector store.
        
        Args:
            all_nodes: All nodes including parents and leaves
        """
        # Initialize docstore and add all nodes
        self.docstore = SimpleDocumentStore()
        self.docstore.add_documents(all_nodes)
        print(f"Added {len(all_nodes)} nodes to docstore")
        
        # Initialize vector store
        if self.use_supabase_vector_store and SUPABASE_VECTOR_STORE_AVAILABLE:
            print("Using Supabase vector store (requires PostgreSQL connection)...")
            self.vector_store = SupabaseVectorStore(
                postgres_connection_string=self._get_postgres_connection_string(),
                collection_name=self.table_name,
                dimension=1536  # text-embedding-3-small dimension
            )
        else:
            # Use in-memory vector store (no external database required)
            print("Using in-memory vector store (no database connection required)")
            # Vector store is created implicitly by VectorStoreIndex
            self.vector_store = None
        
        # Create storage context
        if self.vector_store:
            self.storage_context = StorageContext.from_defaults(
                docstore=self.docstore,
                vector_store=self.vector_store
            )
        else:
            self.storage_context = StorageContext.from_defaults(
                docstore=self.docstore
            )
    
    def _get_postgres_connection_string(self) -> str:
        """
        Get Postgres connection string from environment.
        
        Returns:
            PostgreSQL connection string
        """
        # First, check if a full connection string is provided
        connection_string = os.getenv("SUPABASE_DB_CONNECTION_STRING")
        if connection_string:
            print(f"Using connection string from SUPABASE_DB_CONNECTION_STRING")
            return connection_string
        
        # Fallback: Try to construct from individual components
        supabase_url = os.getenv("SUPABASE_URL")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        
        if not db_password:
            raise ValueError(
                "Either SUPABASE_DB_CONNECTION_STRING or SUPABASE_DB_PASSWORD must be set.\n"
                "Add to your .env file:\n"
                "SUPABASE_DB_CONNECTION_STRING=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres"
            )
        
        # Extract project reference from Supabase URL
        # URL format: https://[project-ref].supabase.co
        if supabase_url:
            project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "").strip()
            constructed_string = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
            print(f"Constructed connection string from SUPABASE_URL and SUPABASE_DB_PASSWORD")
            return constructed_string
        
        raise ValueError("Could not construct PostgreSQL connection string")
    
    def build_index(self, leaf_nodes: list) -> VectorStoreIndex:
        """
        Build vector store index over leaf nodes.
        
        Args:
            leaf_nodes: Leaf-level nodes to index
            
        Returns:
            VectorStoreIndex instance
        """
        print("Building vector store index over leaf nodes...")
        
        self.base_index = VectorStoreIndex(
            leaf_nodes,
            storage_context=self.storage_context,
            embed_model=self.embeddings,
            show_progress=True
        )
        
        print("Vector index built successfully")
        return self.base_index
    
    def create_retriever(
        self,
        similarity_top_k: int = 6,
        verbose: bool = True
    ) -> AutoMergingRetriever:
        """
        Create AutoMergingRetriever from the base index.
        
        Args:
            similarity_top_k: Number of top similar leaf nodes to retrieve
            verbose: Whether to print merging operations
            
        Returns:
            AutoMergingRetriever instance
        """
        if not self.base_index:
            raise ValueError("Index not built. Call build_index() first.")
        
        base_retriever = self.base_index.as_retriever(
            similarity_top_k=similarity_top_k
        )
        
        self.retriever = AutoMergingRetriever(
            base_retriever,
            self.storage_context,
            verbose=verbose
        )
        
        print("AutoMergingRetriever created successfully")
        return self.retriever
    
    def build_all(self) -> AutoMergingRetriever:
        """
        Complete pipeline: load PDF, build hierarchy, create index and retriever.
        
        Returns:
            Ready-to-use AutoMergingRetriever
        """
        print("=" * 60)
        print("Building Hierarchical Auto-Merging Retriever")
        print("=" * 60)
        
        # Step 1: Load PDF
        print("\n[1/5] Loading PDF...")
        documents = self.load_pdf()
        print(f"Loaded {len(documents)} document(s)")
        
        # Step 2: Build hierarchy
        print("\n[2/5] Building node hierarchy...")
        all_nodes, leaf_nodes = self.build_hierarchy(documents)
        
        # Step 3: Setup storage
        print("\n[3/5] Setting up storage...")
        self.setup_storage(all_nodes)
        
        # Step 4: Build index
        print("\n[4/5] Building vector index...")
        self.build_index(leaf_nodes)
        
        # Step 5: Create retriever
        print("\n[5/5] Creating AutoMergingRetriever...")
        retriever = self.create_retriever()
        
        print("\n" + "=" * 60)
        print("✓ Hierarchical retriever built successfully!")
        print("=" * 60)
        
        return retriever


# Global instance for singleton pattern
_global_retriever_instance: Optional[HierarchicalClaimRetriever] = None


def get_claim_retriever(
    rebuild: bool = False,
    pdf_path: str = "insurance_claim_case.pdf",
    use_supabase: bool = False,  # Changed default to False - use in-memory by default
    **kwargs
) -> AutoMergingRetriever:
    """
    Get a ready-to-use AutoMergingRetriever for insurance claim queries.
    
    This is the main entry point for using the hierarchical retriever.
    It implements a singleton pattern to avoid rebuilding the index on every call.
    
    Args:
        rebuild: If True, force rebuild the retriever even if one exists
        pdf_path: Path to the insurance claim PDF
        use_supabase: If True, store embeddings in Supabase (requires SUPABASE_DB_PASSWORD)
                     If False, use in-memory storage (default: True)
        **kwargs: Additional arguments passed to HierarchicalClaimRetriever
        
    Returns:
        AutoMergingRetriever ready for queries
        
    Example:
        >>> retriever = get_claim_retriever()
        >>> nodes = retriever.retrieve("What is the claim amount?")
        >>> for node in nodes:
        ...     print(node.text)
    """
    global _global_retriever_instance
    
    if _global_retriever_instance is None or rebuild:
        print("Initializing new hierarchical retriever...")
        _global_retriever_instance = HierarchicalClaimRetriever(
            pdf_path=pdf_path,
            use_supabase_vector_store=use_supabase,
            **kwargs
        )
        return _global_retriever_instance.build_all()
    
    if _global_retriever_instance.retriever is None:
        print("Building retriever from existing instance...")
        return _global_retriever_instance.build_all()
    
    print("Using cached retriever instance")
    return _global_retriever_instance.retriever


def demo_retrieval(query: str = "What is the claim date?"):
    """
    Demonstrate the hierarchical retriever with a sample query.
    
    Args:
        query: Query string to test
    """
    print("\n" + "=" * 60)
    print("DEMO: Hierarchical Auto-Merging Retrieval")
    print("=" * 60)
    
    # Get retriever
    retriever = get_claim_retriever()
    
    # Perform retrieval
    print(f"\nQuery: {query}")
    print("\nRetrieving nodes (with auto-merging)...")
    nodes = retriever.retrieve(query)
    
    print(f"\nRetrieved {len(nodes)} node(s) after auto-merging:")
    print("-" * 60)
    
    for i, node in enumerate(nodes, 1):
        print(f"\n[Node {i}]")
        print(f"Node ID: {node.node_id}")
        print(f"Score: {node.score:.4f}")
        print(f"Text length: {len(node.text)} characters")
        print(f"Text preview: {node.text[:200]}...")
    
    return nodes


if __name__ == "__main__":
    # Run demo
    demo_retrieval()
