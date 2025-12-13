import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def call_grok(prompt: str):
    if not OPENAI_API_KEY:
        raise Exception("API key not found in environment variables")
    
    # Use OpenRouter API for sk-or-v1 keys
    if OPENAI_API_KEY.startswith("sk-or-v1"):
        url = "https://openrouter.ai/api/v1/chat/completions"
    else:
        url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    # Add HTTP-Referer for OpenRouter
    if OPENAI_API_KEY.startswith("sk-or-v1"):
        headers["HTTP-Referer"] = "http://localhost:8000"

    # Use appropriate model based on API
    if OPENAI_API_KEY.startswith("sk-or-v1"):
        model = "google/gemma-2-9b-it:free"
    else:
        model = "gpt-3.5-turbo"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"OpenAI API Error ({response.status_code}): {response.text}")

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise Exception("Invalid JSON response from OpenAI API")
    
    if "choices" not in data or not data["choices"]:
        raise Exception("No response choices returned from OpenAI API")
    
    return data["choices"][0]["message"]["content"]