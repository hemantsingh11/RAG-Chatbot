# src/document_loader.py

import os
from glob import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_pdf_documents(docs_folder: str):
    """
    Loads all PDF documents from the specified folder.
    
    Args:
        docs_folder (str): Path to the folder containing PDF files.
    
    Returns:
        list: A list of Document objects loaded from the PDFs.
    """
    documents = []
    # Look for all PDF files in the given folder
    pdf_files = glob(os.path.join(docs_folder, "*.pdf"))
    
    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        docs = loader.load()  # This returns a list of Document objects
        documents.extend(docs)
    
    return documents

def split_documents(documents, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Splits loaded documents into smaller text chunks.
    
    Args:
        documents (list): List of Document objects to split.
        chunk_size (int): Maximum size of each text chunk.
        chunk_overlap (int): Number of overlapping characters between chunks.
    
    Returns:
        list: A list of Document objects representing the chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

# Example usage for local testing:
if __name__ == "__main__":
    docs_folder = os.path.join(os.path.dirname(__file__), "..", "docs")
    print("Loading PDFs from:", docs_folder)
    docs = load_pdf_documents(docs_folder)
    print(f"Loaded {len(docs)} document(s).")
    
    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")
