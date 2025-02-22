# A RAG-Based Chainlit Chatbot Deployed on Azure

## Introduction
This document provides an overview of the deployment of a **Retrieval-Augmented Generation (RAG) chatbot** using **Chainlit, LangChain, OpenAI embeddings, and ChromaDB**. The chatbot was containerized using Docker and deployed to **Azure Container Apps**, with authentication managed via **Azure Active Directory (Microsoft Entra ID)**.

## Architecture Overview
The chatbot follows a **RAG-based approach**, retrieving relevant information from a document database before generating responses using an LLM. The key components include:

- **Chainlit:** Provides the frontend chat interface.
- **LangChain:** Handles document ingestion, vector search, and response generation.
- **OpenAI API:** Used for generating embeddings and processing user queries.
- **ChromaDB:** Stores vector embeddings for document retrieval.
- **Azure Container Apps:** Hosts the chatbot in a scalable, managed environment.
- **Azure Active Directory (Microsoft Entra ID):** Secures access to the chatbot via authentication.

## Deployment Steps

### 1. Containerizing the Application
A **Dockerfile** was created to package the chatbot with all dependencies, ensuring portability and ease of deployment. The project structure included:

```
project/
├── docs/                   # Stores the uploaded PDFs
├── chroma_db/              # Stores vector database data
├── src/
│   ├── main.py             # Chainlit chat interface
│   ├── document_loader.py  # Loads and processes PDFs
│   ├── vector_store.py     # Manages ChromaDB embeddings
└── Dockerfile              # Defines the container environment
└── requirements.txt        # Lists dependencies
```

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
docker tag chainlit-chatbot:latest <ACR_LOGIN_SERVER>/chainlit-chatbot:latest
docker push <ACR_LOGIN_SERVER>/chainlit-chatbot:latest
```

### 4. Deploying to Azure Container Apps
A **Container App** was created using the uploaded Docker image from ACR. Key settings included:

- **Port:** 8000 (Chainlit’s default)
- **Ingress:** Enabled with external access
- **Resource Allocation:** 0.5 vCPU, 1 GiB memory
- **Environment Variables:** Configured OpenAI API keys and necessary settings

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
   git clone <your-repo-url>
   cd project
   pip install -r requirements.txt
   ```

2. Build and run the chatbot locally:
   ```bash
   docker build -t chainlit-chatbot .
   docker run -p 8000:8000 chainlit-chatbot
   ```

3. Deploy the container to Azure using Azure Container Apps and configure authentication.

---

**Author:** Hemant Kuma Singh 
**License:** GNU
