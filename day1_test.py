# Currently, our code sends a fixed message every time

import requests

url = "http://localhost:11434/api/chat"

data = {
    "model": "qwen3:1.7b",
    "messages": [
        {
            "role": "user",
            "content": "A customer says their order is delayed. Ask for their order ID politely."
        }
    ],
    "stream": False
}

response = requests.post(url, json=data, timeout=180)

response.raise_for_status()

result = response.json()

print(result["message"]["content"])
