# src/vector_store.py

import os
from langchain_openai import OpenAIEmbeddings  # Updated import for OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Directory where the ChromaDB files will be stored
PERSIST_DIRECTORY = "chroma_db"
# A collection name for our documents (you can choose any name)
COLLECTION_NAME = "document_collection"


from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path('.env'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Replace this with your actual OpenAI API key for now

def create_or_load_vector_store(documents, persist_directory=PERSIST_DIRECTORY, collection_name=COLLECTION_NAME):
    """
    Create a new Chroma vector store from the given documents (if it doesn't exist)
    or load an existing one from the persist_directory.
    
    Args:
        documents (list): A list of document chunks to index.
        persist_directory (str): Directory to persist the vector store.
        collection_name (str): Name of the collection in the vector store.
        
    Returns:
        Chroma: An instance of the Chroma vector store.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    # Create the vector store from documents; persistence is now automatic
    vectorstore = Chroma.from_documents(
        documents, 
        embeddings, 
        persist_directory=persist_directory, 
        collection_name=collection_name
    )
    return vectorstore

def update_vector_store(new_documents, persist_directory=PERSIST_DIRECTORY, collection_name=COLLECTION_NAME):
    """
    Load an existing vector store and add new documents to it.
    
    Args:
        new_documents (list): A list of new document chunks to add.
        persist_directory (str): Directory where the vector store is persisted.
        collection_name (str): Name of the collection in the vector store.
        
    Returns:
        Chroma: Updated vector store instance.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    # Load the existing store
    vectorstore = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embeddings, 
        collection_name=collection_name
    )
    # Add the new document chunks
    vectorstore.add_documents(new_documents)
    return vectorstore

def query_vector_store(query, k=4, persist_directory=PERSIST_DIRECTORY, collection_name=COLLECTION_NAME):
    """
    Query the vector store to retrieve the top k document chunks relevant to the query.
    
    Args:
        query (str): The user's query.
        k (int): Number of top results to return.
        persist_directory (str): Directory where the vector store is persisted.
        collection_name (str): Name of the collection in the vector store.
        
    Returns:
        list: A list of relevant document chunks.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embeddings, 
        collection_name=collection_name
    )
    results = vectorstore.similarity_search(query, k=k)
    return results

# For local testing:
if __name__ == "__main__":
    from document_loader import load_pdf_documents, split_documents
    
    docs_folder = os.path.join(os.path.dirname(__file__), "..", "docs")
    
    print("Loading PDFs from:", docs_folder)
    docs = load_pdf_documents(docs_folder)
    print(f"Loaded {len(docs)} document(s).")
    
    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")
    
    vs = create_or_load_vector_store(chunks)
    print("Vector store created with", len(chunks), "document chunks.")
