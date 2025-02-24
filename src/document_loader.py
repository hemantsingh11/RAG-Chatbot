# src/document_loader.py

import os
from glob import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


# In document_loader.py (or create a new module if preferred)

import os
import tempfile
from azure.storage.blob import ContainerClient
from langchain_community.document_loaders import PyPDFLoader

def load_pdf_documents_from_azure(container_name: str, connection_string: str):
    """
    Loads all PDF documents from an Azure Blob Storage container.
    
    Args:
        container_name (str): The name of your Azure Blob Storage container.
        connection_string (str): Your Azure Storage connection string.
        
    Returns:
        list: A list of Document objects loaded from the PDFs.
    """
    container_client = ContainerClient.from_connection_string(
        conn_str=connection_string, container_name=container_name
    )
    
    documents = []
    
    # List all blobs in the container and filter for PDF files
    for blob in container_client.list_blobs():
        if blob.name.lower().endswith(".pdf"):
            # Download the blob's content
            downloader = container_client.download_blob(blob)
            pdf_bytes = downloader.readall()
            
            # Write the PDF content to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp.flush()
                # Use PyPDFLoader to load the document from the temporary file
                loader = PyPDFLoader(tmp.name)
                docs = loader.load()
                documents.extend(docs)
            # Clean up the temporary file
            os.remove(tmp.name)
            
    return documents


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
