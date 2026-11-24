import requests
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

file_path = Path(__file__).with_name("_09knowledge_base.txt")

with open(file_path, "r", encoding="utf-8") as file:
    knowledge = file.read()

print(knowledge)


chunks = [
    chunk.strip()
    for chunk in knowledge.split("\n\n")
    if chunk.strip()
]

print("\nTotal chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):
    print(f"\nChunk {i}:")
    print(chunk)


model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(chunks)

print("\nEmbeddings generated successfully!")
print("Number of chunks:", len(chunks))
print("Embedding shape:", embeddings.shape)

print("\nFirst chunk's embedding:")
print(embeddings[0][:10])

# ChromaDB ka local database create/open kar rahe hain
client = chromadb.PersistentClient(path="./chroma_db")

# Knowledge base ke liye collection create/open kar rahe hain
collection = client.get_or_create_collection(
    name="smartshop_knowledge"
)

# Knowledge chunks aur unki embeddings database mein store kar rahe hain
collection.upsert(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings.tolist()
)

print("\nKnowledge base stored in ChromaDB successfully!")


# Customer ka question
customer_question = customer_question = "Who is the CEO of SmartShop?"

# Customer question ko embedding mein convert kar rahe hain
question_embedding = model.encode(customer_question)

# ChromaDB se similar knowledge chunks search kar rahe hain
results = collection.query(
    query_embeddings=[question_embedding.tolist()],
    n_results=2
)

print("\nRetrieved knowledge:")

for document in results["documents"][0]:
    print("\n", document)

# Retrieved knowledge ko ek single string mein combine kar rahe hain
retrieved_context = "\n\n".join(results["documents"][0])

print("\nContext for AI:")
print(retrieved_context)


# Ollama ko customer question aur retrieved knowledge bhej rahe hain
data = {
    "model": "qwen3:1.7b",
    "stream": False,
    "messages": [
        {
            "role": "system",
            "content": f"""
You are a customer support assistant for SmartShop.

Answer the customer using only the knowledge provided below.
Do not make up any policy or information.
If the knowledge does not contain the answer, say that you don't have enough information.

Knowledge:
{retrieved_context}
"""
        },
        {
            "role": "user",
            "content": customer_question
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

print("\nAI Answer:")
print(result["message"]["content"])