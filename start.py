#!/usr/bin/env python3
"""
Startup script for the AI Prompt Improver application.
Used by Render as the entrypoint.
"""

import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()  # loads .env if present


def main():
    # Render injects the port number into the PORT env variable
    port = int(os.environ.get("PORT", 8000))

    print("🚀 Starting AI Prompt Improver server...")
    print(f"🌐 Listening on 0.0.0.0:{port}")

    uvicorn.run(
        "app.main:app",  # module:variable
        host="0.0.0.0",
        port=port,
        reload=False,     # True only for local dev
        log_level="info",
    )


if __name__ == "__main__":
    main()
