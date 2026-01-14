"""
Configuration Management
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    # LLM Settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # Safety Settings
    REQUIRE_CONFIRMATION: bool = True
    ENABLE_LOGGING: bool = True
    DRY_RUN_MODE: bool = False
    
    # Execution Settings
    MAX_COMMAND_LENGTH: int = 500
    COMMAND_TIMEOUT: int = 30
    
    # Database
    DB_PATH: str = "./data/agent_memory.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "./logs/agent.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
