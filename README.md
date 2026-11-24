
# Agentic Customer Support AI

An AI-powered customer support system built using Python, Ollama, RAG, and FastAPI.

The system helps customers with order-related queries, refund eligibility, product complaints, and general questions using a local AI model and a knowledge base.

## Features

- Order status lookup using a mock order database
- Refund eligibility checking based on order status
- Complaint ticket creation
- Retrieval-Augmented Generation (RAG) for policy-related questions
- Tool calling with multiple tools
- AI agent that selects and executes available tools
- FastAPI REST API
- Local LLM inference using Ollama

## Tech Stack

- Python
- Ollama
- Qwen3 1.7B
- FastAPI
- ChromaDB
- Sentence Transformers
- Requests
- Pydantic

## Project Workflow

1. Customer sends a message.
2. The system detects the customer's intent.
3. The agent decides whether a tool is required.
4. Python executes the selected tool.
5. Tool results are passed back to the AI.
6. The AI generates a customer-friendly response.

For general questions, the system retrieves relevant information from the knowledge base using RAG.

## API

### GET /

Checks whether the API is running.

### POST /chat

Example request:

```json
{
  "message": "Please check my order ORD102"
}
```

Example response:

```json
{
  "intent": "order_query",
  "response": "Your order is currently processing.",
  "order_id": "ORD102",
  "ticket_id": null
}
```

## Run Locally

### 1. Install dependencies

```bash
pip install fastapi uvicorn requests
```

Install the remaining project dependencies used for RAG and embeddings as required.

### 2. Start Ollama

Make sure Ollama is installed and running.

Pull the model:

```bash
ollama pull qwen3:1.7b
```

### 3. Run the API

```bash
uvicorn _13api:app --reload
```

### 4. Open API documentation

Visit:

http://127.0.0.1:8000/docs

## Project Scope

This project uses mock order data and a demo refund policy.

It is intended for learning and demonstration purposes and is not connected to a real e-commerce platform.
