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
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # /improv
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prompt_improver")

# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------
app = FastAPI(
    title="AI Prompt Improver",
    version="1.0.0",
)

# CORS (allow everything – you can tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Static files + frontend
# -----------------------------------------------------------------------------
# /static/... will serve files from /improv/static
try:
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )
    logger.info(f"Mounted static files from: {STATIC_DIR}")
except Exception as e:
    logger.warning(f"Failed to mount {STATIC_DIR}, trying 'static': {e}")
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static",
    )

# Root route → serve index.html
@app.get("/")
def serve_frontend():
    logger.info(f"Looking for index.html at: {INDEX_FILE}")
    logger.info(f"Static directory: {STATIC_DIR}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    if not INDEX_FILE.exists():
        logger.error(f"index.html not found at {INDEX_FILE}")
        # Try alternative path for deployment
        alt_path = Path("static/index.html")
        if alt_path.exists():
            logger.info(f"Found index.html at alternative path: {alt_path}")
            return FileResponse(str(alt_path))
        raise HTTPException(status_code=500, detail=f"Frontend not found. Checked: {INDEX_FILE} and {alt_path}")

    return FileResponse(str(INDEX_FILE))


# Simple health check for Render / uptime checks
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "prompt-improver",
        "version": "1.0.0",
    }

# -----------------------------------------------------------------------------
# Main API endpoint
# -----------------------------------------------------------------------------
@app.post("/improve", response_model=PromptResponse)
def improve(req: PromptRequest):
    """
    Takes a prompt, classifies it, then generates an improved prompt.
    """
    try:
        if not req.prompt or len(req.prompt.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Prompt must be at least 3 characters long.",
            )

        prompt_text = req.prompt.strip()
        logger.info(f"Received prompt: {prompt_text[:80]}...")

        # Step 1: classify the prompt
        raw_classification = classify_prompt(prompt_text)
        logger.info("Classification completed.")

        try:
            data = json.loads(raw_classification)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in classifier output: {e}")
            return PromptResponse(
                improved_prompt="Error: Invalid response from classifier. Please try again.",
                error="classification_error",
            )

        role = data.get("role", "assistant")
        objective = data.get("objective", "help with request")
        context = data.get("context", "general assistance")

        logger.info(f"Extracted – role={role}, objective={objective}")

        # Step 2: improve the prompt
        improved = improve_prompt(role, objective, context)
        logger.info("Improvement completed.")

        # If your improver returns an error message starting with ⚠
        if isinstance(improved, str) and improved.startswith("⚠"):
            return PromptResponse(
                improved_prompt=improved,
                error="api_error",
            )

        return PromptResponse(
            improved_prompt=improved,
            error=None,
        )

    except HTTPException:
        # Re-throw explicit HTTP errors
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return PromptResponse(
            improved_prompt="Error: An unexpected error occurred. Please try again later.",
            error="internal_error",
        )
