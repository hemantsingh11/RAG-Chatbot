# src/main.py

import os
from dotenv import load_dotenv
import chainlit as cl
from prompts.system_message import SYSTEM_PROMPT

# Load environment variables from .env file
# load_dotenv()
from langchain.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory

# Import our document loading and vector store functions
from document_loader import load_pdf_documents, split_documents
from vector_store import create_or_load_vector_store

from dotenv import load_dotenv
from pathlib import Path

# Import our Azure PDF loader and the text splitter
from document_loader import load_pdf_documents_from_azure, split_documents

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

@cl.on_chat_start
async def on_chat_start():
    """
    On chat start, load PDF documents from the /docs folder, split them into chunks,
    create (or load) the Chroma vector store, and initialize a ConversationalRetrievalChain
    with conversation memory.
    """
    # Define the path to the docs folder (adjust if needed)
    docs_folder = os.path.join(os.path.dirname(__file__), "..", "docs")
    
    # Load PDFs and split them into chunks
    # docs = load_pdf_documents(docs_folder)
    docs = load_pdf_documents_from_azure(AZURE_CONTAINER_NAME, AZURE_CONNECTION_STRING)

    chunks = split_documents(docs)
    
    # Create (or load) the vector store using our pre-defined function
    vectorstore = create_or_load_vector_store(chunks)
    
    # Build a retriever from the vector store
    retriever = vectorstore.as_retriever()
    
    # Set up conversation memory
    message_history = ChatMessageHistory()
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )
    
    # Modified prompt now includes a {context} placeholder
    qa_prompt = ChatPromptTemplate.from_messages([
        (
            "system",SYSTEM_PROMPT
        ),
        ("human", "Context: {context}\nQuestion: {question}"),
    ])

    chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0,
            streaming=True,
            openai_api_key=OPENAI_API_KEY,
        ),
        chain_type="stuff",
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": qa_prompt}
    )
    
    # Store the chain in the user session for later retrieval in on_message
    cl.user_session.set("chain", chain)
    await cl.Message("Document processing complete. You can now ask questions.").send()

@cl.on_message
async def main(message: cl.Message):
    """
    When a user sends a message, retrieve the conversation chain from the session,
    run an asynchronous call to the chain, and return the answer along with any source documents.
    """
    chain = cl.user_session.get("chain")
    
    # Create an async callback handler for streaming responses
    cb = cl.AsyncLangchainCallbackHandler()
    
    # Call the chain asynchronously with the user's query
    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["answer"]
    source_documents = res.get("source_documents", [])
    
    # Build side-panel text elements for any source documents retrieved
    text_elements = []
    for idx, doc in enumerate(source_documents):
        text_elements.append(cl.Text(content=doc.page_content, name=f"source_{idx}", display="side"))
    
    if text_elements:
        answer += "\nSources: " + ", ".join([t.name for t in text_elements])
    else:
        answer += "\nNo sources found."
    
    await cl.Message(content=answer, elements=text_elements).send()
