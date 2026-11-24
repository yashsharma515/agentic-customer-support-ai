# Now we'll combine both files:
# - intent.py identifies the customer's problem.
# - day1_test1.py generates an AI response.


# any(word in message for word in ["refund", "return", "money back"])

# It checks whether at least one of these words or phrases exists in the message.
# If any one matches, it returns True.
# This makes our code shorter and easier to maintain.



import requests

# Import our intent detection function
from _02intent import detect_intent

def get_ai_response(message, intent):

    url = "http://localhost:11434/api/chat"

    system_prompt = f"""
    You are a professional customer support assistant.

    Customer intent: {intent}

    Respond politely, empathetically and concisely.
    Do not invent order details, refund policies or payment information.
    If information is missing, ask the customer for it.
    """

    data = {
        "model": "qwen3:1.7b",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
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


# Main application
customer_message = input("Customer: ")

intent = detect_intent(customer_message)

print("\nDetected intent:", intent)

answer = get_ai_response(customer_message, intent)

print("\nAI Assistant:", answer)
