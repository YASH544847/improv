from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import PromptRequest
from .classifier import classify_prompt
from .improver import improve_prompt
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend running!"}

@app.post("/improve")
def improve(req: PromptRequest):
    try:
        print(f"Received prompt: {req.prompt}")
        
        # Step 1: classify
        raw_classification = classify_prompt(req.prompt)
        print(f"Classification result: {raw_classification}")

        try:
            data = json.loads(raw_classification)
        except json.JSONDecodeError:
            return {"improved_prompt": f"Error: Invalid JSON from classifier: {raw_classification[:100]}..."}

        role = data.get("role", "assistant")
        objective = data.get("objective", "help with request")
        context = data.get("context", "general assistance")
        
        print(f"Parsed - Role: {role}, Objective: {objective}, Context: {context}")

        # Step 2: improve
        improved = improve_prompt(role, objective, context)
        print(f"Improved result: {improved}")

        return {"improved_prompt": improved}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"improved_prompt": f"Error: {str(e)}"}
