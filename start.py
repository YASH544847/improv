#!/usr/bin/env python3
"""
Startup script for the AI Prompt Improver application
"""
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Check if API key is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  WARNING: Please set your OPENAI_API_KEY in the .env file")
        print("📝 Copy .env.example to .env and add your API key")
    
    print("🚀 Starting AI Prompt Improver server...")
    print("📱 Frontend: Open http://127.0.0.1:8000 in your browser")
    print("🔗 Backend API: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0" if os.getenv("RENDER") else "127.0.0.1"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False if os.getenv("RENDER") else True,
        log_level="info"
    )