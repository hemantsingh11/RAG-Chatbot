# RAG-Based Chatbot built with Chainlit and Azure

This repository implements a Retrieval-Augmented Generation (RAG) chatbot using Chainlit, LangChain, OpenAI embeddings, and ChromaDB. The chatbot can be containerized with Docker and deployed on Azure Container Apps, with secure access via Azure Active Directory (Microsoft Entra ID). This document explains the code structure, how each module works, and the steps for both local testing and deployment.





## Overview

This chatbot uses a RAG approach to first retrieve relevant document segments from a pre-indexed PDF corpus and then uses a language model (via the OpenAI API) to generate answers based on the context. The key benefits include:

- **Dynamic Document Retrieval:** Uses a vector store (ChromaDB) to search for document chunks that are semantically similar to the user query.
- **Conversational Memory:** Maintains chat history using LangChain’s memory module.
- **Secure and Scalable Deployment:** Built to run in a container on Azure Container Apps with user authentication provided by Azure AD.




## Architecture

1. **Document Ingestion & Preprocessing:**  
   The PDFs stored in a specified azure blob storage are loaded and split into manageable chunks.  
   (_See [document_loader.py](./src/document_loader.py) for details._)

2. **Vector Store Management:**  
   ChromaDB is used to create or update a vector store from the document chunks. The vector store leverages OpenAI embeddings for semantic search.  
   (_See [vector_store.py](./src/vector_store.py) for details._)

3. **Conversational Retrieval Chain:**  
   When the chatbot starts, it loads and indexes the documents, sets up a retriever from the vector store, and initializes a retrieval-based conversation chain with memory.  
   (_See [main.py](./src/main.py) for details._)

4. **User Interaction:**  
   Users interact through a Chainlit chat interface. On each query, the system:
   - Retrieves relevant document chunks.
   - Generates an answer using an LLM (ChatOpenAI).
   - Displays source excerpts in a side-panel for transparency.




## Deployment Steps For Azure

### 1. Containerizing the Application
A **Dockerfile** can be created to package the chatbot with all dependencies, ensuring portability and ease of deployment. 
After preparing the Docker environment, the image can be built and tested locally using Docker Desktop.

### 2. Creating Azure Resources
The following Azure resources were provisioned:

- **Azure Container Registry (ACR):** Stores the containerized chatbot image.
- **Azure Storage Account & File Share:** Ensures persistent storage for documents and embeddings.
- **Azure Container Apps Environment:** Provides a managed execution environment.
- **Azure Active Directory (Microsoft Entra ID):** Restricts access to authorized users.

### 3. Pushing the Docker Image to ACR
After successful local testing, the image can be tagged and pushed to ACR:

```bash
docker build -t chainlit-chatbot .
docker tag chainlit-chatbot:latest <ACR_LOGIN_SERVER>/chainlit-chatbot:latest
docker push <ACR_LOGIN_SERVER>/chainlit-chatbot:latest
```

### 4. Deploying to Azure Container Apps
A **Container App** can be created using the uploaded Docker image from ACR. Key settings included:

- **Port:** 8000 (Chainlit’s default)
- **Ingress:** Enabled with external access


### 5. Enabling Authentication
To restrict access, authentication can be configured using **Microsoft Entra ID**:

1. A new **App Registration** can be created in Azure AD.
2. The **Client ID** and **Tenant ID** can be added to the Container App.
3. Authentication can be enforced, requiring users to log in via Microsoft before accessing the chatbot.

### 6. Final Testing and Validation
Once deployed, the chatbot can be accessed via the provided **Azure Container Apps URL**. The authentication mechanism redirected users to Microsoft login, ensuring only authorized individuals could chat with the bot.


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


