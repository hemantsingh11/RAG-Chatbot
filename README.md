# RAG-Based Chatbot built with Chainlit and Azure

This repository implements a Retrieval-Augmented Generation (RAG) chatbot using Chainlit, LangChain, OpenAI embeddings, and ChromaDB. The chatbot is containerized with Docker and deployed on Azure Container Apps, with secure access via Azure Active Directory (Microsoft Entra ID). This document explains the code structure, how each module works, and the steps for both local testing and deployment.

---



## Overview

This chatbot uses a RAG approach to first retrieve relevant document segments from a pre-indexed PDF corpus and then uses a language model (via the OpenAI API) to generate answers based on the context. The key benefits include:

- **Dynamic Document Retrieval:** Uses a vector store (ChromaDB) to search for document chunks that are semantically similar to the user query.
- **Conversational Memory:** Maintains chat history using LangChain’s memory module.
- **Secure and Scalable Deployment:** Runs in a container on Azure Container Apps with user authentication provided by Azure AD.

---

## Architecture

1. **Document Ingestion & Preprocessing:**  
   The PDFs stored in a specified azure blob storage are loaded and split into manageable chunks.  
   (_See [document_loader.py](#document_loaderpy) for details._)

2. **Vector Store Management:**  
   ChromaDB is used to create or update a vector store from the document chunks. The vector store leverages OpenAI embeddings for semantic search.  
   (_See [vector_store.py](#vector_storepy) for details._)

3. **Conversational Retrieval Chain:**  
   When the chatbot starts, it loads and indexes the documents, sets up a retriever from the vector store, and initializes a retrieval-based conversation chain with memory.  
   (_See [main.py](#mainpy) for details._)

4. **User Interaction:**  
   Users interact through a Chainlit chat interface. On each query, the system:
   - Retrieves relevant document chunks.
   - Generates an answer using an LLM (ChatOpenAI).
   - Displays source excerpts in a side-panel for transparency.

---

## File Breakdown

### vector_store.py

This module handles all interactions with the vector store (ChromaDB).

- **create_or_load_vector_store(documents, ...):**  
  Creates a new vector store from document chunks or loads an existing one from a persistent directory. It uses OpenAI embeddings to convert text chunks into vector representations and then indexes them in ChromaDB.

- **update_vector_store(new_documents, ...):**  
  Loads an existing vector store and adds new document chunks. This function is useful when you need to update your knowledge base without rebuilding from scratch.

- **query_vector_store(query, k, ...):**  
  Searches the vector store using a user-provided query. It retrieves the top `k` document chunks most similar to the query.

*Example Usage:*  
When run as a script, the module loads PDFs from a folder, splits them into chunks, and creates a vector store from these chunks.

---

### document_loader.py

This module is responsible for loading and preprocessing the documents.

- **load_pdf_documents_from_azure(container_name: str, connection_string: str):**
   Retrieves all PDF documents stored in an Azure Blob Storage container, loads them using a PDF loader (PyPDFLoader), and returns a list of document objects.

- **load_pdf_documents(docs_folder):**  
  Searches for all PDF files in the provided local folder, loads them using a PDF loader (PyPDFLoader), and returns a list of document objects.

- **split_documents(documents, chunk_size, chunk_overlap):**  
  Uses a recursive character text splitter to divide each document into smaller chunks. This ensures that long documents are broken down into segments that are easier to index and query.

*Example Usage:*  
When executed directly, the module prints out the number of loaded documents and the resulting chunks after splitting.

---

### main.py

This is the entry point for the chatbot application integrated with Chainlit.

- **On Chat Start (`@cl.on_chat_start`):**  
  - **Document Processing:**  
    Loads PDFs from the designated `/docs` folder, splits them into chunks, and creates or loads the Chroma vector store.
  - **Retriever Setup:**  
    Converts the vector store into a retriever to find relevant document chunks for incoming queries.
  - **Memory and Prompt Configuration:**  
    Sets up conversational memory to maintain chat history and defines a custom prompt that includes both system-level instructions and user context.
  - **Chain Initialization:**  
    Creates a `ConversationalRetrievalChain` using a ChatOpenAI model (with streaming support) that is stored in the user session.

- **On User Message (`@cl.on_message`):**  
  When a message is received, the system:
  - Retrieves the pre-initialized chain from the session.
  - Executes the chain asynchronously, fetching the answer and any source documents.
  - Builds a side-panel display for source excerpts, appending the source information to the final answer.

---

## Getting Started Locally

### Prerequisites

- **Python 3.8+**
- Required Python libraries (install via `pip install -r requirements.txt`)
- **Docker** (for containerizing the application)
- **.env file** with your OpenAI API key (and any other required secrets)

### Steps to Run Locally

1. **Clone the Repository:**

   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare Documents:**

   Place your PDF documents in the `/docs` folder at the root level of the repository.

4. **Run Locally:**

   ```bash
   python src/main.py
   ```

   Or run using Docker:

   ```bash
   docker build -t chainlit-chatbot .
   docker run -p 8000:8000 chainlit-chatbot
   ```

---
## Deployment Steps For Azure

### 1. Containerizing the Application
A **Dockerfile** was created to package the chatbot with all dependencies, ensuring portability and ease of deployment. 
After preparing the Docker environment, the image was built and tested locally using Docker Desktop.

### 2. Creating Azure Resources
The following Azure resources were provisioned:

- **Azure Container Registry (ACR):** Stores the containerized chatbot image.
- **Azure Storage Account & File Share:** Ensures persistent storage for documents and embeddings.
- **Azure Container Apps Environment:** Provides a managed execution environment.
- **Azure Active Directory (Microsoft Entra ID):** Restricts access to authorized users.

### 3. Pushing the Docker Image to ACR
After successful local testing, the image was tagged and pushed to ACR:

```bash
docker build -t chainlit-chatbot .
docker tag chainlit-chatbot:latest <ACR_LOGIN_SERVER>/chainlit-chatbot:latest
docker push <ACR_LOGIN_SERVER>/chainlit-chatbot:latest
```

### 4. Deploying to Azure Container Apps
A **Container App** was created using the uploaded Docker image from ACR. Key settings included:

- **Port:** 8000 (Chainlit’s default)
- **Ingress:** Enabled with external access


### 5. Enabling Authentication
To restrict access, authentication was configured using **Microsoft Entra ID**:

1. A new **App Registration** was created in Azure AD.
2. The **Client ID** and **Tenant ID** were added to the Container App.
3. Authentication was enforced, requiring users to log in via Microsoft before accessing the chatbot.

### 6. Final Testing and Validation
Once deployed, the chatbot was accessed via the provided **Azure Container Apps URL**. The authentication mechanism redirected users to Microsoft login, ensuring only authorized individuals could chat with the bot.

## Conclusion
This deployment provides a **scalable, secure, and easily accessible** RAG-based chatbot on Azure. Using Azure Container Apps ensures **automatic scaling**, while **Azure AD authentication** keeps access restricted. Additionally, **persistent storage** for ChromaDB allows seamless updates and document re-indexing.

This architecture is suitable for **internal knowledge assistants, document-based search applications, and enterprise AI chatbots** requiring secure access and dynamic data retrieval.

---

## Getting Started
To set up this chatbot for your own use, follow these steps:

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/hemantsingh11/RAG-Chatbot.git
   cd project
   pip install -r requirements.txt
   ```

2. Set up environment variable:

   Create a .env file in root directory and add following variables.
   ```bash
   # Select LLM provider (only openai supported right now)
   LLM_PROVIDER=openai

   # provide your API key:
   OPENAI_API_KEY=<your_api_key>

   # Azure Storage Account
   AZURE_CONNECTION_STRING="<your_blob_storage_connection_string>"
   AZURE_CONTAINER_NAME=<your_blob_storage_container_name>
   ```

3. Run chatbot on localhost:
   ```bash
   chainlit run .\src\main.py
   ```

4. Build and run the chatbot on docker desktop:
   ```bash
   docker build -t chainlit-chatbot .
   docker run -p 8000:8000 chainlit-chatbot
   ```

5. Deploy the container to Azure using Azure Container Apps and configure authentication.


