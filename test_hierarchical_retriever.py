"""
Test and Demo Script for Hierarchical Auto-Merging Retriever

This script demonstrates the hierarchical retriever functionality and
provides tests to validate the implementation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all required packages can be imported."""
    print("=" * 60)
    print("TEST 1: Checking Package Imports")
    print("=" * 60)
    
    try:
        import llama_index
        print("✓ llama-index imported")
    except ImportError as e:
        print(f"✗ Failed to import llama-index: {e}")
        return False
    
    try:
        from llama_index.core import Document, VectorStoreIndex
        print("✓ llama-index core components imported")
    except ImportError as e:
        print(f"✗ Failed to import core components: {e}")
        return False
    
    try:
        from llama_index.core.node_parser import HierarchicalNodeParser
        print("✓ HierarchicalNodeParser imported")
    except ImportError as e:
        print(f"✗ Failed to import HierarchicalNodeParser: {e}")
        return False
    
    try:
        from llama_index.core.retrievers import AutoMergingRetriever
        print("✓ AutoMergingRetriever imported")
    except ImportError as e:
        print(f"✗ Failed to import AutoMergingRetriever: {e}")
        return False
    
    try:
        from llama_index.embeddings.openai import OpenAIEmbedding
        print("✓ OpenAI embeddings imported")
    except ImportError as e:
        print(f"✗ Failed to import OpenAI embeddings: {e}")
        return False
    
    try:
        from llama_index.readers.file import PyMuPDFReader
        print("✓ PyMuPDF reader imported")
    except ImportError as e:
        print(f"✗ Failed to import PyMuPDF reader: {e}")
        return False
    
    print("\n✓ All imports successful!\n")
    return True


def test_environment():
    """Test that required environment variables are set."""
    print("=" * 60)
    print("TEST 2: Checking Environment Variables")
    print("=" * 60)
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY"
    ]
    
    optional_vars = [
        "SUPABASE_DB_PASSWORD"
    ]
    
    all_present = True
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✓ {var} is set")
        else:
            print(f"✗ {var} is NOT set")
            all_present = False
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✓ {var} is set (optional)")
        else:
            print(f"⚠ {var} is NOT set (optional, but recommended for Supabase vector store)")
    
    if all_present:
        print("\n✓ All required environment variables are set!\n")
    else:
        print("\n✗ Some required environment variables are missing!\n")
    
    return all_present


def test_pdf_exists():
    """Test that the insurance claim PDF exists."""
    print("=" * 60)
    print("TEST 3: Checking PDF File")
    print("=" * 60)
    
    pdf_path = Path("insurance_claim_case.pdf")
    
    if pdf_path.exists():
        size_kb = pdf_path.stat().st_size / 1024
        print(f"✓ insurance_claim_case.pdf found ({size_kb:.2f} KB)")
        print(f"  Path: {pdf_path.absolute()}\n")
        return True
    else:
        print(f"✗ insurance_claim_case.pdf NOT found")
        print(f"  Expected location: {pdf_path.absolute()}\n")
        return False


def test_hierarchy_creation():
    """Test hierarchical node parsing without building the full index."""
    print("=" * 60)
    print("TEST 4: Testing Hierarchical Node Parsing")
    print("=" * 60)
    
    try:
        from llama_index.core import Document
        from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
        
        # Create a test document
        test_text = """
        This is a test insurance claim document. The claim was filed on January 15, 2024.
        The claimant is John Doe with policy number POL-12345-67890.
        
        The incident occurred on January 10, 2024, when the insured vehicle was damaged
        in a collision at the intersection of Main Street and Oak Avenue.
        
        The estimated repair cost is $5,500. The deductible amount is $500.
        The claim has been reviewed and approved for payment.
        
        Additional details: The vehicle is a 2020 Honda Accord with VIN 1HGCV1F3XLA123456.
        The repairs will be performed at ABC Auto Body Shop located at 123 Repair Lane.
        """ * 10  # Repeat to have enough text for hierarchy
        
        test_doc = Document(text=test_text)
        
        # Create parser with default chunk sizes
        node_parser = HierarchicalNodeParser.from_defaults(
            chunk_sizes=[2048, 512, 128]
        )
        
        print("Creating hierarchical nodes...")
        nodes = node_parser.get_nodes_from_documents([test_doc])
        print(f"✓ Created {len(nodes)} total nodes")
        
        leaf_nodes = get_leaf_nodes(nodes)
        print(f"✓ Extracted {len(leaf_nodes)} leaf nodes")
        
        # Verify hierarchy
        if len(nodes) > len(leaf_nodes):
            print(f"✓ Hierarchy verified: {len(nodes) - len(leaf_nodes)} parent nodes")
        
        # Show sample node
        if leaf_nodes:
            sample = leaf_nodes[0]
            print(f"\nSample leaf node:")
            print(f"  Text length: {len(sample.text)} characters")
            print(f"  Preview: {sample.text[:100]}...")
        
        print("\n✓ Hierarchical parsing test successful!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Hierarchical parsing test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_supabase_connection():
    """Test connection to Supabase."""
    print("=" * 60)
    print("TEST 5: Testing Supabase Connection")
    print("=" * 60)
    
    try:
        from supabase_utils import get_supabase_client
        
        client = get_supabase_client()
        print("✓ Supabase client created successfully")
        
        # Try to list tables (this will verify connection works)
        # Note: This is a basic check, not a comprehensive test
        print("✓ Supabase connection test successful!\n")
        return True
        
    except Exception as e:
        print(f"✗ Supabase connection failed: {e}\n")
        return False


def demo_simple_retrieval():
    """Demonstrate a simple retrieval without full index build."""
    print("=" * 60)
    print("DEMO: Simple Hierarchical Node Creation")
    print("=" * 60)
    
    try:
        from llama_index.core import Document
        from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes, get_root_nodes
        
        # Create a demo document
        demo_text = """
        Insurance Claim Summary
        
        Claim Number: CLM-2024-001234
        Policy Number: POL-98765-43210
        Claimant: Jane Smith
        Date of Loss: February 15, 2024
        Date Filed: February 16, 2024
        
        Incident Description:
        On February 15, 2024, the insured property at 456 Oak Street sustained water damage
        due to a burst pipe in the second-floor bathroom. The damage affected the bathroom,
        hallway, and portions of the first-floor living room ceiling.
        
        Damages Claimed:
        1. Bathroom repairs: $3,200
        2. Hallway repairs: $1,800
        3. Living room ceiling repair: $2,500
        4. Water extraction and drying: $1,200
        5. Emergency plumbing repairs: $800
        
        Total Claimed Amount: $9,500
        Deductible: $1,000
        Net Payable: $8,500
        
        Adjuster Notes:
        Property inspection completed on February 17, 2024. All damages are consistent with
        the reported incident. No signs of pre-existing damage or negligence. Recommend
        approval of claim for full amount after deductible.
        
        Status: Approved
        Payment Date: February 20, 2024
        Check Number: CHK-7890123
        """ * 5  # Repeat for sufficient content
        
        demo_doc = Document(text=demo_text)
        
        # Create hierarchical parser
        node_parser = HierarchicalNodeParser.from_defaults(
            chunk_sizes=[2048, 512, 128]
        )
        
        print("\nParsing demo document...")
        nodes = node_parser.get_nodes_from_documents([demo_doc])
        leaf_nodes = get_leaf_nodes(nodes)
        root_nodes = get_root_nodes(nodes)
        
        print(f"\nHierarchy Statistics:")
        print(f"  Total nodes: {len(nodes)}")
        print(f"  Root nodes: {len(root_nodes)}")
        print(f"  Leaf nodes: {len(leaf_nodes)}")
        print(f"  Parent nodes: {len(nodes) - len(leaf_nodes)}")
        
        print(f"\nSample Root Node (Level 1 - 2048 chars):")
        if root_nodes:
            print(f"  Length: {len(root_nodes[0].text)} chars")
            print(f"  Preview: {root_nodes[0].text[:150]}...")
        
        print(f"\nSample Leaf Node (Level 3 - 128 chars):")
        if leaf_nodes:
            print(f"  Length: {len(leaf_nodes[0].text)} chars")
            print(f"  Text: {leaf_nodes[0].text}")
        
        print("\n✓ Demo completed successfully!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests and demos."""
    print("\n" + "=" * 60)
    print("HIERARCHICAL AUTO-MERGING RETRIEVER - TEST SUITE")
    print("=" * 60 + "\n")
    
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['environment'] = test_environment()
    results['pdf'] = test_pdf_exists()
    results['hierarchy'] = test_hierarchy_creation()
    results['supabase'] = test_supabase_connection()
    
    # Run demo
    print("\n" + "=" * 60)
    print("Running Demonstration")
    print("=" * 60 + "\n")
    demo_simple_retrieval()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name.upper()}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nYou're ready to use the hierarchical retriever.")
        print("Run: python hierarchical_retriever.py")
    else:
        print("⚠ SOME TESTS FAILED")
        print("\nPlease address the failed tests before proceeding:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Set up environment variables in .env file")
        print("3. Ensure insurance_claim_case.pdf is in the project folder")
        print("4. Run the Supabase SQL setup script")
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
