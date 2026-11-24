
# But in our actual project, customers will send different messages:
# - Where is my order?
# - I want to return my product.
# - My payment failed.
# - I received a damaged product.
#     We need a function that accepts any customer message.
#     Replace your existing code with this:



import requests

def get_ai_response(message):

    url = "http://localhost:11434/api/chat"

    data = {
        "model": "qwen3:1.7b",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional customer support assistant. Respond politely, empathetically, and concisely."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "stream": False
    }

    response = requests.post(url, json=data, timeout=180)

    response.raise_for_status()

    result = response.json()

    return result["message"]["content"]


# Take message from customer        ,, here we also handling the error by using {try except} concept 
customer_message = input("Customer: ")

try:
    answer = get_ai_response(customer_message)
    print("\nAI Assistant:", answer)

except requests.RequestException as e:
    print("Error communicating with Ollama:", e)
