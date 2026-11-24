# Understand the purpose:
# - detect_intent() receives the customer's message.
# - lower() makes matching case-insensitive.
# - strip() removes unnecessary spaces.
# - Conditions identify the customer's likely intention.
# - return gives the detected category back to the application.
#This is a simple baseline using keyword rules. Later, we'll improve it with the LLM and use LangGraph to manage the actual agent workflow.
#


def detect_intent(message):

    message = message.lower().strip()
    # Policy-related questions should use RAG
    if any(word in message for word in [
        "refund policy",
        "return policy",
        "refund rules",
        "how do refunds work"
    ]):
        return "general"


    # Refund and return queries
    if any(word in message for word in [
        "refund", "return", "money back",
        "return my payment", "get my money"
    ]):
        return "refund"

    # Order related queries
    elif any(word in message for word in [
        "order", "tracking", "delivery", "shipment",
        "not received", "didnt receive"
    ]):
        return "order_query"

    # Product complaints
    elif any(word in message for word in [
        "damaged", "broken", "defective",
        "poor quality", "cheap product"
    ]):
        return "product_complaint"

    # Payment related queries
    elif any(word in message for word in [
        "payment", "paid", "transaction"
    ]):
        return "payment_issue"

    elif any(word in message for word in ["hello", "hi"]):
        return "greeting"

    else:
        return "general"



# Test the function
# customer_message = input("Customer: ")

# intent = detect_intent(customer_message)

# print("Detected intent:", intent)
