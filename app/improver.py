import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Use OpenRouter API for sk-or-v1 keys
if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-v1"):
    OPENAI_URL = "https://openrouter.ai/api/v1/chat/completions"
else:
    OPENAI_URL = "https://api.openai.com/v1/chat/completions"

def improve_prompt(role, objective, context):
    try:
        if not OPENAI_API_KEY:
            return "⚠ Error: OpenAI API key not found in environment variables"
        
        # Use appropriate model based on API
        if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-v1"):
            model = "openai/gpt-3.5-turbo"
        else:
            model = "gpt-3.5-turbo"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI prompt engineer. Your job is to rewrite the user's prompt clearly using Role, Objective, and Context."
                },
                {
                    "role": "user",
                    "content": f"""
Create a professional prompt using:

Role: {role}
Objective: {objective}
Context: {context}
                    """
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        response = requests.post(OPENAI_URL, json=payload, headers=headers)
        
        if response.status_code != 200:
            return f"⚠ API Error ({response.status_code}): {response.text}"
        
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            return "⚠ Error: Invalid JSON response from API"
        
        if "choices" not in response_data or not response_data["choices"]:
            return "⚠ Error: No response choices returned from API"
        
        return response_data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"⚠ Fallback Mode (OpenAI API error): {str(e)}"
