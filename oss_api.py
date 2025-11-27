import requests
import os

API_KEY = os.getenv("OSS_API_KEY")
BASE_URL = "https://api.openai.com/v1/chat/completions"

def call_oss(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-oss-20b",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"OSS API Error: {response.text}")

    return response.json()['choices'][0]['message']['content']
