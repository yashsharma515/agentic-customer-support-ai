import requests
import chromadb
from sentence_transformers import SentenceTransformer


# Embedding model load kar rahe hain
model = SentenceTransformer("all-MiniLM-L6-v2")

# Existing local ChromaDB database open kar rahe hain
client = chromadb.PersistentClient(path="./chroma_db")

# Existing knowledge collection open kar rahe hain
collection = client.get_collection(
    name="smartshop_knowledge"
)


def retrieve_knowledge(question):

    # Customer question ko embedding mein convert kar rahe hain
    question_embedding = model.encode(question)

    # Relevant knowledge chunks retrieve kar rahe hain
    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=2
    )

    # Retrieved chunks ko ek context string mein combine kar rahe hain
    retrieved_context = "\n\n".join(results["documents"][0])

    return retrieved_context



def get_rag_response(question):

    # Customer question ke liye relevant knowledge retrieve kar rahe hain
    context = retrieve_knowledge(question)

    # Retrieved knowledge aur customer question Ollama ko bhej rahe hain
    data = {
        "model": "qwen3:1.7b",
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": f"""
You are a SmartShop customer support assistant.

Answer using only the provided knowledge.
Do not invent information.
If the knowledge does not contain the answer,
say you don't have enough information.

Knowledge:
{context}
"""
            },
            {
                "role": "user",
                "content": question
            }
        ]
    }

    response = requests.post(
        "http://localhost:11434/api/chat",
        json=data,
        timeout=180
    )

    response.raise_for_status()

    result = response.json()

    return result["message"]["content"]


