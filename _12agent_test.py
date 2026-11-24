
import re
import requests
import json

from _05order_tool import get_order_status
from _07refund_tool import check_refund_eligibility
from _08ticket_tool import create_ticket


# Available tools ki definition
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Check the status of a customer's order using their Order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Customer's order ID, such as ORD102"
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_refund_eligibility",
            "description": "Check whether a customer's order is eligible for a refund. Use the Order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Customer's order ID, such as ORD102"
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a support ticket for damaged products or issues that need human support. Order ID is optional.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The customer's original issue"
                    },
                    "intent": {
                        "type": "string",
                        "description": "Issue category, such as product_complaint or payment_issue"
                    },
                    "order_id": {
                        "type": "string",
                        "description": "Optional order ID, such as ORD102"
                    }
                },
                "required": ["message", "intent"]
            }
        }
    }
]


# Customer ka message
customer_message = "Please check whether my order ORD102 is eligible for a refund."


# First request: AI ko tools aur customer message bhejna yaha se hota h
data = {
    "model": "qwen3:1.7b",

    "messages": [
        {
            "role": "system",
            "content": """
You are a customer support agent for SmartShop.

Rules:
1. If the customer asks about order status, use get_order_status.
2. If the customer asks about refund eligibility, use check_refund_eligibility.
3. Never invent order details.
4. Never claim that a refund has been processed.
5. If an order is not found, clearly tell the customer.
6. Use the tool results to generate your final answer.
7. If the customer reports a damaged or defective product and needs support, use create_ticket.
8. For damaged product complaints, create a support ticket immediately.
9. Do not require an Order ID to create a support ticket.
10. Use the customer's original message and the appropriate issue category.
11. Never claim a ticket was created unless the tool returns a ticket ID.
12. Do not ask for an Order ID before creating a ticket for a damaged product.
"""
        },

        {
            "role": "user",
            "content": customer_message
        }
    ],

    "tools": tools,
    "stream": False
}


# Ollama se first response lena
try:
    response = requests.post(
        "http://localhost:11434/api/chat",
        json=data,
        timeout=180
    )

    response.raise_for_status()

except requests.exceptions.RequestException as e:
    print("Error connecting to Ollama:", e)
    exit()


result = response.json()  # result = Ollama ka complete response


# AI ke response se tool calls nikalna
tool_calls = result["message"].get("tool_calls", [])  # result["message"] = AI ka message,   .get("tool_calls", []) = tool calls milengi, warna empty list


if tool_calls:

    # AI ka tool-call message conversation mein add karna
    data["messages"].append(result["message"]) 

    for tool_call in tool_calls:

        function_name = tool_call["function"]["name"] # AI ne jo tool select kiya, uska naam function_name mein aata hai.
        arguments = tool_call["function"]["arguments"]


        # ---------------------------------
        # TOOL 1: CREATE SUPPORT TICKET
        # ---------------------------------

        if function_name == "create_ticket":

            ticket_message = arguments.get("message")
            intent = arguments.get("intent")
            ticket_order_id = arguments.get("order_id")

            # Customer message validate karna
            if not isinstance(ticket_message, str) or not ticket_message.strip():

                tool_result = "Invalid ticket message."

            # Intent validate karna
            elif not isinstance(intent, str) or not intent.strip():

                tool_result = "Invalid ticket intent."

            # Order ID optional hai.
            # Agar diya gaya hai, tabhi validate karna.
            elif ticket_order_id is not None and (
                not isinstance(ticket_order_id, str)
                or not re.fullmatch(r"ORD\d+", ticket_order_id)
            ):

                tool_result = "Invalid order ID format."

            else:

                # Actual ticket create karna
                ticket = create_ticket(
                    ticket_message,
                    intent,
                    ticket_order_id
                )

                tool_result = ticket


        # ---------------------------------
        # ORDER AUR REFUND TOOLS
        # In tools ke liye Order ID required hai
        # ---------------------------------

        else:

            order_id = arguments.get("order_id")

            # Order ID format validate karna
            if not isinstance(order_id, str) or not re.fullmatch(r"ORD\d+", order_id):

                tool_result = "Invalid order ID format."
    # re.fullmatch(r"ORD\d+", order_id) check karta hai ki Order ID ka format valid hai ya nahi. 
            # ---------------------------------
            # TOOL 2: GET ORDER STATUS
            # ---------------------------------

            elif function_name == "get_order_status":

                tool_result = get_order_status(order_id)

                if tool_result is None:
                    tool_result = "Order not found."


            # ---------------------------------
            # TOOL 3: REFUND ELIGIBILITY
            # ---------------------------------

            elif function_name == "check_refund_eligibility":

                # Pehle order details retrieve karna
                order_details = get_order_status(order_id)

                if order_details is None:

                    tool_result = "Order not found. Refund eligibility cannot be checked."

                else:

                    # Order details mil gayi.
                    # Ab refund eligibility check karna.
                    tool_result = check_refund_eligibility(order_details)


            else:

                tool_result = "Unknown tool requested."


        # ---------------------------------
        # TOOL RESULT KO STRING MEIN CONVERT KARNA
        # ---------------------------------

        if not isinstance(tool_result, str):

            tool_result_text = json.dumps(tool_result)

        else:

            tool_result_text = tool_result


        # Tool result AI conversation mein add karna
        data["messages"].append({
            "role": "tool",
            "content": tool_result_text
        })


    # ---------------------------------
    # SECOND REQUEST: TOOL RESULT AI KO BHEJNA
    # ---------------------------------

    try:

        final_response = requests.post(
            "http://localhost:11434/api/chat",
            json=data,
            timeout=180
        )

        final_response.raise_for_status()

    except requests.exceptions.RequestException as e:

        print("Error connecting to Ollama:", e)
        exit()


    final_result = final_response.json()


    # AI ka final customer-friendly answer
    print("\nAI Assistant:", final_result["message"]["content"])


else:

    # Agar AI ne tool call nahi ki
    # toh normal response print karna
    print("\nAI Assistant:", result["message"]["content"])




# Ab AI customer ke message ke according different tools select kar sakta hai.
# Important: AI tool select karta hai, lekin actual Python function execute tumhara Python code karta hai.