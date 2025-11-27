from .grok_api import call_grok
import json

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
