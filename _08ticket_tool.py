
import json
from pathlib import Path
from datetime import datetime
import uuid


def create_ticket(message, intent, order_id=None):

    ticket_id = "TKT" + uuid.uuid4().hex[:6].upper()

    ticket = {
        "ticket_id": ticket_id,
        "message": message,
        "intent": intent,
        "order_id": order_id,
        "status": "Open",
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    file_path = Path(__file__).with_name("tickets.json")

    if file_path.exists():
        with open(file_path, "r") as file:
            tickets = json.load(file)
    else:
        tickets = []

    tickets.append(ticket)

    with open(file_path, "w") as file:
        json.dump(tickets, file, indent=4)

    return ticket

if __name__ == "__main__":
    ticket = create_ticket(
        "My product is damaged",
        "product_complaint",
        "ORD102"
    )

    print(ticket)
