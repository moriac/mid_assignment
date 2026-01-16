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

# ChromaDB vector store (default storage backend)
try:
    from llama_index.vector_stores.chroma import ChromaVectorStore
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDB not available (install with: pip install llama-index-vector-stores-chroma chromadb)")

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
    
    Leaf nodes are indexed in ChromaDB vector store by default (or in-memory),
    while all nodes are stored in a docstore for auto-merging during retrieval.
    """
    
    def __init__(
        self,
        pdf_path: str = "insurance_claim_case.pdf",
        collection_name: str = "small_chunks",
        chunk_sizes: Optional[list] = None,
        use_chromadb: bool = True,
        chroma_persist_dir: str = "./chroma_db"
    ):
        """
        Initialize the hierarchical retriever.
        
        Args:
            pdf_path: Path to the insurance claim PDF file
            collection_name: ChromaDB collection name for storing leaf node embeddings (default: "small_chunks")
            chunk_sizes: List of chunk sizes for hierarchy levels (default: [2048, 512, 128])
            use_chromadb: If True, use ChromaDB vector store (default: True)
                         If False, use in-memory vector store
            chroma_persist_dir: Directory for ChromaDB persistent storage (default: "./chroma_db")
        """
        self.pdf_path = pdf_path
        self.collection_name = collection_name
        self.chunk_sizes = chunk_sizes or [2048, 512, 128]
        self.use_chromadb = use_chromadb
        self.chroma_persist_dir = chroma_persist_dir
        self.docstore_persist_dir = os.path.join(chroma_persist_dir, "docstore")
        
        # Initialize components
        self.chroma_client = None
        self.chroma_collection = None
        
        if self.use_chromadb:
            if not CHROMA_AVAILABLE:
                raise ImportError(
                    "ChromaDB storage requested but required packages not installed.\n"
                    "Install with: pip install llama-index-vector-stores-chroma chromadb"
                )
            self.chroma_client, self.chroma_collection = self._init_chromadb()
        
        self.embeddings = self._init_embeddings()
        self.llm = self._init_llm()
        
        # Storage components (initialized during build)
        self.docstore = None
        self.vector_store = None
        self.storage_context = None
        self.base_index = None
        self.retriever = None
        
    def _init_chromadb(self) -> tuple:
        """
        Initialize ChromaDB client and collection.
        
        Returns:
            Tuple of (chromadb_client, collection)
        """
        print(f"Initializing ChromaDB with collection: {self.collection_name}")
        
        # Create persistent client
        client = chromadb.PersistentClient(path=self.chroma_persist_dir)
        
        # Get or create collection
        collection = client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Hierarchical chunks for insurance claim retrieval"}
        )
        
        print(f"✓ ChromaDB initialized: {collection.count()} existing documents")
        return client, collection
    
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
        
        # Persist docstore to disk if using ChromaDB
        if self.use_chromadb:
            os.makedirs(self.docstore_persist_dir, exist_ok=True)
            self.docstore.persist(persist_path=os.path.join(self.docstore_persist_dir, "docstore.json"))
            print(f"✓ Docstore persisted to: {self.docstore_persist_dir}")
        
        # Initialize vector store
        if self.use_chromadb and CHROMA_AVAILABLE:
            print(f"Using ChromaDB vector store (collection: {self.collection_name})...")
            self.vector_store = ChromaVectorStore(
                chroma_collection=self.chroma_collection
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
    
    def _can_load_from_existing(self) -> bool:
        """
        Check if we can load from existing ChromaDB collection.
        
        Returns:
            True if ChromaDB is enabled and collection has data and docstore exists
        """
        if not self.use_chromadb:
            return False
        
        if self.chroma_collection is None:
            return False
        
        # Check if collection has embeddings
        count = self.chroma_collection.count()
        if count == 0:
            return False
        
        # Check if persisted docstore exists
        docstore_path = os.path.join(self.docstore_persist_dir, "docstore.json")
        if not os.path.exists(docstore_path):
            print(f"⚠️ ChromaDB collection exists but docstore not found at {docstore_path}")
            return False
        
        return True
    
    def _load_from_chromadb(self) -> AutoMergingRetriever:
        """
        Load existing index and retriever from ChromaDB.
        
        Returns:
            AutoMergingRetriever loaded from existing data
        """
        print("\n" + "=" * 60)
        print("Loading Existing Index from ChromaDB")
        print("=" * 60)
        
        # Step 1: Load persisted docstore
        print("\n[1/2] Loading persisted docstore...")
        docstore_path = os.path.join(self.docstore_persist_dir, "docstore.json")
        self.docstore = SimpleDocumentStore.from_persist_path(docstore_path)
        doc_count = len(self.docstore.docs)
        print(f"✓ Loaded docstore with {doc_count} nodes from: {docstore_path}")
        
        # Create ChromaDB vector store
        vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        
        # Create storage context
        self.storage_context = StorageContext.from_defaults(
            docstore=self.docstore,
            vector_store=vector_store
        )
        
        # Step 2: Load index from existing vector store
        print("\n[2/2] Loading vector index from ChromaDB...")
        self.base_index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=self.storage_context,
            embed_model=self.embeddings
        )
        print(f"✓ Vector index loaded with {self.chroma_collection.count()} embeddings")
        
        # Create retriever
        base_retriever = self.base_index.as_retriever(similarity_top_k=6)
        retriever = AutoMergingRetriever(
            base_retriever,
            self.storage_context,
            verbose=True
        )
        
        self.retriever = retriever
        
        print("\n" + "=" * 60)
        print("✓ Loaded retriever from existing ChromaDB collection!")
        print("=" * 60)
        
        return retriever
    
    def build_all(self, force_rebuild: bool = False) -> AutoMergingRetriever:
        """
        Complete pipeline: load PDF, build hierarchy, create index and retriever.
        
        If using ChromaDB and data already exists, loads from existing collection.
        Otherwise, builds everything from scratch.
        
        Args:
            force_rebuild: If True, rebuild from scratch even if data exists
        
        Returns:
            Ready-to-use AutoMergingRetriever
        """
        # Check if we can load from existing ChromaDB data
        if not force_rebuild and self._can_load_from_existing():
            print("📦 Existing ChromaDB collection found with data!")
            return self._load_from_chromadb()
        
        # Clear existing collection if force_rebuild
        if force_rebuild and self.use_chromadb and self.chroma_collection:
            count = self.chroma_collection.count()
            if count > 0:
                print(f"🔄 Force rebuild requested - clearing {count} existing embeddings...")
                self.chroma_client.delete_collection(self.collection_name)
                self.chroma_collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Hierarchical chunks for insurance claim retrieval"}
                )
        
        # Build from scratch
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
    use_chromadb: bool = True,
    **kwargs
) -> AutoMergingRetriever:
    """
    Get a ready-to-use AutoMergingRetriever for insurance claim queries.
    
    This is the main entry point for using the hierarchical retriever.
    It implements a singleton pattern to avoid rebuilding the index on every call.
    
    Args:
        rebuild: If True, force rebuild the retriever even if one exists
        pdf_path: Path to the insurance claim PDF
        use_chromadb: If True, store embeddings in ChromaDB (default: True)
                     If False, use in-memory storage
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
            use_chromadb=use_chromadb,
            **kwargs
        )
        return _global_retriever_instance.build_all(force_rebuild=rebuild)
    
    if _global_retriever_instance.retriever is None:
        print("Building retriever from existing instance...")
        return _global_retriever_instance.build_all(force_rebuild=False)
    
    print("Using cached retriever instance")
    return _global_retriever_instance.retriever


def demo_retrieval(query: str = "When did the incident occur?"):
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
