"""
LLM Client - Manages communication with Ollama
"""

import ollama
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        """
        Initialize LLM client
        
        Args:
            model: Ollama model name (default: llama3)
            host: Ollama server host
        """
        self.model = model
        self.host = host
        self.client = ollama.Client(host=host)
        
    async def chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a chat message to the LLM
        
        Args:
            user_message: User's input message
            system_prompt: Optional system prompt for context
            
        Returns:
            LLM response text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            response = self.client.chat(
                model=self.model,
                messages=messages
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error communicating with LLM: {e}")
            raise
    
    async def generate_command(self, user_request: str) -> Dict[str, Any]:
        """
        Generate PowerShell command from natural language request
        
        Args:
            user_request: User's natural language request
            
        Returns:
            Dictionary with command details
        """
        from .prompts import SystemPrompts
        
        prompt = SystemPrompts.COMMAND_GENERATION.format(user_request=user_request)
        
        response = await self.chat(prompt)
        
        # Parse response to extract command details
        return self._parse_command_response(response)
    
    def _parse_command_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response to extract command information
        
        Args:
            response: Raw LLM response
            
        Returns:
            Structured command data
        """
        # Simple parsing - can be enhanced with JSON mode in future
        lines = response.strip().split('\n')
        
        result = {
            "explanation": "",
            "command": "",
            "risks": [],
            "requires_admin": False
        }
        
        for line in lines:
            if line.startswith("Command:"):
                # Strip "Command:" prefix, whitespace, and any backticks
                cmd = line.replace("Command:", "").strip()
                result["command"] = cmd.strip('`').strip()
            elif line.startswith("Explanation:"):
                result["explanation"] = line.replace("Explanation:", "").strip()
            elif line.startswith("Risks:"):
                result["risks"] = [line.replace("Risks:", "").strip()]
            elif "admin" in line.lower() or "administrator" in line.lower():
                result["requires_admin"] = True
        
        return result
    
    def is_available(self) -> bool:
        """
        Check if Ollama server is available
        
        Returns:
            True if server is reachable
        """
        try:
            self.client.list()
            return True
        except Exception:
            return False
