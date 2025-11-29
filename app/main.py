from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .models import PromptRequest, PromptResponse
from .classifier import classify_prompt
from .improver import improve_prompt
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Prompt Improver", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files folder
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
def home():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "prompt-improver"}

@app.post("/improve", response_model=PromptResponse)
def improve(req: PromptRequest):
    try:
        if not req.prompt or len(req.prompt.strip()) < 3:
            raise HTTPException(status_code=400, detail="Prompt must be at least 3 characters long")
        
        logger.info(f"Processing prompt: {req.prompt[:50]}...")
        
        # Step 1: classify
        raw_classification = classify_prompt(req.prompt)
        logger.info(f"Classification completed")

        try:
            data = json.loads(raw_classification)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return PromptResponse(
                improved_prompt=f"Error: Invalid response from classifier. Please try again.",
                error="classification_error"
            )

        role = data.get("role", "assistant")
        objective = data.get("objective", "help with request")
        context = data.get("context", "general assistance")
        
        logger.info(f"Extracted - Role: {role}, Objective: {objective}")

        # Step 2: improve
        improved = improve_prompt(role, objective, context)
        logger.info(f"Improvement completed")

        if improved.startswith("⚠"):
            return PromptResponse(
                improved_prompt=improved,
                error="api_error"
            )

        return PromptResponse(improved_prompt=improved)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return PromptResponse(
            improved_prompt=f"Error: An unexpected error occurred. Please try again later.",
            error="internal_error"
        )
