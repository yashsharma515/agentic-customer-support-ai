
import requests
import re

from _02intent import detect_intent
from _05order_tool import get_order_status
from _07refund_tool import check_refund_eligibility
from _08ticket_tool import create_ticket
from _11rag import get_rag_response


# --------------------------------------------------
# AI response function
# --------------------------------------------------

def get_ai_response(message, intent, order_details=None, refund_result=None):

    system_prompt = f"""
You are an AI customer support assistant.

Customer message:
{message}

Detected intent:
{intent}

Order details:
{order_details}

Refund eligibility result:
{refund_result}

Rules:
1. Give a clear and polite response.
2. Use only the provided order details.
3. Never invent order status or delivery dates.
4. Never promise a refund unless the refund result confirms eligibility.
5. If the order is not eligible for refund, explain the reason.
6. If information is missing, ask the customer for it.
7. Keep the response concise and professional.
"""

    payload = {
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

    try:
        result = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=180
        )

        result.raise_for_status()

        result = result.json()

        return result["message"]["content"]

    except requests.exceptions.RequestException as e:

        print("Ollama connection error:", e)

        return "Sorry, AI support is temporarily unavailable. Please try again."


# --------------------------------------------------
# Support response function
# --------------------------------------------------

def get_support_response(
    message,
    intent,
    order_details=None,
    refund_result=None
):

    # General questions ke liye RAG use hoga
    if intent == "general":

        return get_rag_response(message)

    # Baaki intents ke liye Ollama response
    return get_ai_response(
        message,
        intent,
        order_details,
        refund_result
    )


# --------------------------------------------------
# Main reusable workflow
# --------------------------------------------------

def process_customer_message(customer_message, order_id=None):

    # Step 1: Detect customer intent
    intent = detect_intent(customer_message)

    order_details = None
    refund_result = None
    ticket_id = None

    # Message mein se Order ID extract karne ka pattern
    order_id_pattern = r"ORD\d+"

    # Agar request mein Order ID di gayi hai,
    # toh usko priority denge
    if order_id is None:

        match = re.search(
            order_id_pattern,
            customer_message,
            re.IGNORECASE
        )

        if match:
            order_id = match.group().upper()

    else:
        order_id = order_id.upper().strip()


    # --------------------------------------------------
    # Step 2: Order query
    # --------------------------------------------------

    if intent == "order_query":

        # Order ID missing hai
        if order_id is None:

            return {
                "intent": intent,
                "response": "Please provide your Order ID. For example: ORD102",
                "order_id": None,
                "ticket_id": None
            }

        # Order status check
        order_details = get_order_status(order_id)

        # Invalid Order ID
        if order_details is None:

            return {
                "intent": intent,
                "response": f"Sorry, I could not find order {order_id}. Please check your Order ID.",
                "order_id": order_id,
                "ticket_id": None
            }


    # --------------------------------------------------
    # Step 3: Refund request
    # --------------------------------------------------

    elif intent == "refund":

        # Refund ke liye Order ID required hai
        if order_id is None:

            return {
                "intent": intent,
                "response": "Please provide your Order ID so I can check your refund eligibility.",
                "order_id": None,
                "ticket_id": None
            }

        # Order details retrieve karna
        order_details = get_order_status(order_id)

        # Invalid Order ID
        if order_details is None:

            return {
                "intent": intent,
                "response": f"Sorry, I could not find order {order_id}. Please check your Order ID.",
                "order_id": order_id,
                "ticket_id": None
            }

        # Refund eligibility check
        refund_result = check_refund_eligibility(order_details)


    # --------------------------------------------------
    # Step 4: Product complaint
    # --------------------------------------------------

    elif intent == "product_complaint":

        # Complaint ke liye ticket create karna
        ticket = create_ticket(
            customer_message,
            intent,
            order_id
        )

        # Ticket creation failed
        if ticket is None:

            return {
                "intent": intent,
                "response": "Sorry, I could not create your support ticket. Please try again.",
                "order_id": order_id,
                "ticket_id": None
            }

        # Ticket ID retrieve karna
        if isinstance(ticket, dict):

            ticket_id = ticket.get("ticket_id")

        else:

            ticket_id = ticket


        # Ticket creation ke baad customer ko response
        return {
            "intent": intent,
            "response": f"Sorry for the inconvenience. Your complaint has been registered successfully. Your ticket ID is {ticket_id}. Our support team will review it.",
            "order_id": order_id,
            "ticket_id": ticket_id
        }


    # --------------------------------------------------
    # Step 5: Generate final AI response
    # --------------------------------------------------

    answer = get_support_response(
        customer_message,
        intent,
        order_details,
        refund_result
    )

    # API ko structured response return karna
    return {
        "intent": intent,
        "response": answer,
        "order_id": order_id,
        "ticket_id": ticket_id
    }


# --------------------------------------------------
# Terminal application
# --------------------------------------------------

if __name__ == "__main__":

    customer_message = input("Customer: ")

    result = process_customer_message(customer_message)

    print("\nDetected intent:", result["intent"])

    print("\nAI Assistant:", result["response"])
