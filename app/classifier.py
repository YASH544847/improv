import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def call_grok(prompt: str):
    if not OPENAI_API_KEY:
        raise Exception("API key not found in environment variables")
    
    if OPENAI_API_KEY.startswith("gsk_"):
        url = "https://api.groq.com/openai/v1/chat/completions"
        model = "llama-3.1-8b-instant"
    elif OPENAI_API_KEY.startswith("sk-or-v1"):
        url = "https://openrouter.ai/api/v1/chat/completions"
        model = "openai/gpt-3.5-turbo"
    else:
        url = "https://api.openai.com/v1/chat/completions"
        model = "gpt-3.5-turbo"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API Error ({response.status_code}): {response.text}")

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        raise Exception("Invalid JSON response from API")
    
    if "choices" not in data or not data["choices"]:
        raise Exception("No response choices returned from API")
    
    return data["choices"][0]["message"]["content"]

def classify_prompt(user_prompt: str):
    """
    This function uses the Grok LLM to classify the user prompt
    into role, objective and context.
    """
    try:
        classification_prompt = f"""
You are a prompt analysis system. You MUST respond with valid JSON only.

Analyze this prompt and extract:
- Role (who the AI should act as)
- Objective (what the user wants)  
- Context (additional details)

Respond with ONLY this JSON format (no other text):
{{"role": "...", "objective": "...", "context": "..."}}

User prompt: {user_prompt}
"""

        result = call_grok(classification_prompt).strip()
        
        # Extract JSON if wrapped in markdown or other text
        if '```' in result:
            start = result.find('{') 
            end = result.rfind('}') + 1
            if start != -1 and end != 0:
                result = result[start:end]
        
        # Validate JSON
        json.loads(result)
        return result
    
    except Exception:
        return '{"role": "assistant", "objective": "help with the request", "context": "general assistance"}'
