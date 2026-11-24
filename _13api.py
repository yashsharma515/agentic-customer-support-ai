
from fastapi import FastAPI
from pydantic import BaseModel

from _06integrated_support import process_customer_message


app = FastAPI()


# Customer request ka format
class ChatRequest(BaseModel):

    message: str

    # Order ID optional hai
    order_id: str | None = None


# Home endpoint
@app.get("/")
def home():

    return {
        "message": "Agentic Customer Support AI is running!"
    }


# Chat endpoint
@app.post("/chat")
def chat(request: ChatRequest):

    # Actual support workflow execute hoga
    result = process_customer_message(
        request.message,
        request.order_id
    )

    return result
