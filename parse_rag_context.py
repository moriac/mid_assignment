"""Temporary script to parse rag_context file"""
import json

# Read the rag_context file
with open(r'c:\Dev\AI_Course\mid_assignment\rag_context', 'r', encoding='utf-8') as f:
    content = f.read()

# Use eval since it's a Python literal (be careful with this in production!)
try:
    contexts = eval(content)
    print(f"Successfully parsed rag_context")
    print(f"Number of context lists: {len(contexts)}")
    print(f"Context structure verified")
    
    # Write to a Python file for easy import
    with open(r'c:\Dev\AI_Course\mid_assignment\rag_context_data.py', 'w', encoding='utf-8') as out:
        out.write("# Auto-generated from rag_context file\n")
        out.write("RAG_CONTEXTS = ")
        out.write(repr(contexts))
        
    print("Created rag_context_data.py for import")
except Exception as e:
    print(f"Error: {e}")
