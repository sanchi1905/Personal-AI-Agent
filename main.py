"""
Main Application - Personal AI Agent
Entry point for the FastAPI server
"""

import logging
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.routes import router
from src.memory.database import MemoryDatabase
from src.llm.client import LLMClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Personal AI Agent",
    description="A trustworthy, system-aware AI assistant for Windows PC management",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Personal AI Agent...")
    
    # Create necessary directories
    Path("./logs").mkdir(exist_ok=True)
    Path("./data").mkdir(exist_ok=True)
    
    # Initialize database
    db = MemoryDatabase()
    await db.initialize()
    logger.info("Database initialized")
    
    # Check Ollama connection
    try:
        llm_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        llm_model = os.getenv("OLLAMA_MODEL", "llama3")
        llm_client = LLMClient(model=llm_model, host=llm_host)
        
        if llm_client.is_available():
            logger.info(f"Ollama connected successfully (Model: {llm_model})")
        else:
            logger.warning("Ollama not available. Please ensure Ollama is running.")
    except Exception as e:
        logger.warning(f"Could not connect to Ollama: {e}")
    
    logger.info("Personal AI Agent started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Personal AI Agent...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Personal AI Agent",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
