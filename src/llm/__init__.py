"""
LLM Module - Handles interaction with Ollama for natural language processing
"""

from .client import LLMClient
from .prompts import SystemPrompts

__all__ = ["LLMClient", "SystemPrompts"]
