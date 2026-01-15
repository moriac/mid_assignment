"""
Setup script to ensure all required dependencies are installed in your virtual environment
Run this before using ChromaDB-based scripts
"""

import subprocess
import sys
import os

def check_venv():
    """Check if running in a virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("✅ Running in virtual environment")
        print(f"   Python: {sys.executable}")
        return True
    else:
        print("⚠️  NOT running in a virtual environment")
        print(f"   Python: {sys.executable}")
        print("\n💡 Recommendation: Activate your virtual environment first:")
        print("   Windows: .venv\\Scripts\\activate")
        print("   Linux/Mac: source .venv/bin/activate")
        response = input("\nContinue anyway? (y/n): ")
        return response.lower() == 'y'

def install_package(package_name):
    """Install a package using pip"""
    print(f"\n📦 Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "--quiet"])
        print(f"   ✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"   ❌ Failed to install {package_name}")
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("=" * 70)
    print("ChromaDB Environment Setup Script")
    print("=" * 70)
    print()
    
    # Check virtual environment
    if not check_venv():
        print("\n❌ Setup cancelled")
        return
    
    print("\n" + "-" * 70)
    print("Checking and installing required packages...")
    print("-" * 70)
    
    # Required packages for ChromaDB-based chunking
    required_packages = {
        'chromadb': 'chromadb>=0.4.0',
        'openai': 'openai>=1.0.0',
        'dotenv': 'python-dotenv>=1.0.0',
        'fitz': 'pymupdf>=1.23.0',  # Note: fitz is the import name for pymupdf
    }
    
    packages_to_install = []
    
    for import_name, package_spec in required_packages.items():
        if check_package(import_name):
            print(f"✅ {package_spec.split('>=')[0]} - already installed")
        else:
            print(f"❌ {package_spec.split('>=')[0]} - NOT installed")
            packages_to_install.append(package_spec)
    
    if packages_to_install:
        print(f"\n📦 Need to install {len(packages_to_install)} package(s)")
        print("-" * 70)
        
        for package in packages_to_install:
            if not install_package(package):
                print(f"\n❌ Failed to install {package}")
                print("   Try running manually: pip install " + package)
                return
    else:
        print("\n✨ All required packages are already installed!")
    
    print("\n" + "=" * 70)
    print("✅ Environment setup complete!")
    print("=" * 70)
    print("\n📚 You can now use:")
    print("   1. chromadb_chunk_pdf.py - Process PDF and store in ChromaDB")
    print("   2. test_chromadb_retrieval.py - Query and test the system")
    print("\n💡 Make sure you have:")
    print("   - .env file with OPENAI_API_KEY")
    print("   - insurance_claim_case.pdf in the project directory")
    print()

if __name__ == "__main__":
    main()
