"""
Check PDF content to diagnose why no chunks were created
"""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

pdf_folder = Path("tik")
pdf_files = list(pdf_folder.glob("*.pdf"))

print("Checking PDF content...\n")

for pdf_file in pdf_files:
    print(f"📄 {pdf_file.name}")
    loader = PyPDFLoader(str(pdf_file))
    documents = loader.load()
    
    total_text = ""
    for i, doc in enumerate(documents):
        total_text += doc.page_content
        print(f"  Page {i+1}: {len(doc.page_content)} characters")
    
    print(f"  Total text: {len(total_text)} characters")
    if total_text.strip():
        print(f"  Sample: {total_text[:100].strip()}...")
    else:
        print("  ⚠️ NO TEXT FOUND - might be scanned images")
    print()
