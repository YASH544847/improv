import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Use appropriate API based on key type
if OPENAI_API_KEY and OPENAI_API_KEY.startswith("gsk_"):
    OPENAI_URL = "https://api.groq.com/openai/v1/chat/completions"
elif OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-v1"):
    OPENAI_URL = "https://openrouter.ai/api/v1/chat/completions"
else:
    OPENAI_URL = "https://api.openai.com/v1/chat/completions"

def improve_prompt(role, objective, context):
    try:
        if not OPENAI_API_KEY:
            return "⚠ Error: OpenAI API key not found in environment variables"
        
        # Validate inputs
        if not all([role, objective, context]):
            return "⚠ Error: Missing role, objective, or context information"
        
        # Use appropriate model based on API
        if OPENAI_API_KEY and OPENAI_API_KEY.startswith("gsk_"):
            model = "llama-3.1-8b-instant"
        elif OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-v1"):
            model = "meta-llama/llama-3.2-3b-instruct:free"
        else:
            model = "gpt-3.5-turbo"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert AI prompt engineer. Create clear, structured prompts that specify Role, Objective, and Context. Make the prompt actionable and specific."
                },
                {
                    "role": "user",
                    "content": f"""
Create a professional, well-structured prompt using these components:

Role: {role}
Objective: {objective}
Context: {context}

Format the output as a clear, actionable prompt that an AI assistant can follow effectively.
                    """
                }
            ]
        }
        
        # Add parameters based on API type
        if not OPENAI_API_KEY.startswith("gsk_"):
            payload["max_tokens"] = 500
            payload["temperature"] = 0.7

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # Add HTTP-Referer for OpenRouter
        if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-or-v1"):
            headers["HTTP-Referer"] = "http://localhost:8000"

        response = requests.post(
            OPENAI_URL, 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 401:
            return "⚠ Error: Invalid API key. Please check your OpenAI API key."
        elif response.status_code == 429:
            return "⚠ Error: Rate limit exceeded. Please try again in a moment."
        elif response.status_code != 200:
            logger.error(f"API Error {response.status_code}: {response.text}")
            return f"⚠ API Error ({response.status_code}): Please try again later."
        
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            return "⚠ Error: Invalid response from API. Please try again."
        
        if "choices" not in response_data or not response_data["choices"]:
            return "⚠ Error: No response received from API. Please try again."
        
        content = response_data["choices"][0]["message"]["content"]
        
        if not content or len(content.strip()) < 10:
            return "⚠ Error: Received empty response. Please try again."
        
        return content.strip()

    except requests.exceptions.Timeout:
        return "⚠ Error: Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "⚠ Error: Connection failed. Please check your internet connection."
    except Exception as e:
        logger.error(f"Unexpected error in improve_prompt: {str(e)}")
        return f"⚠ Error: An unexpected error occurred. Please try again later."
