"""
LLM Client - Manages communication with Ollama
"""

import ollama
from typing import Dict, Any, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
        self.executor = ThreadPoolExecutor(max_workers=4)
        
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
            
            # Run synchronous Ollama call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: self.client.chat(
                    model=self.model,
                    messages=messages
                )
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
        lines = response.strip().split('\n')
        
        result = {
            "explanation": "",
            "command": "",
            "risks": [],
            "requires_admin": False
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if line.lower().startswith("command:"):
                current_section = "command"
                cmd = line.split(":", 1)[1].strip()
                # Remove any markdown code blocks or backticks
                cmd = cmd.replace('```powershell', '').replace('```', '').strip('`').strip('"').strip("'").strip()
                result["command"] = cmd
            elif line.lower().startswith("explanation:"):
                current_section = "explanation"
                result["explanation"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("risks:"):
                current_section = "risks"
                risk_text = line.split(":", 1)[1].strip()
                if risk_text and risk_text.lower() != 'none':
                    result["risks"].append(risk_text)
            elif line.lower().startswith("requires admin:"):
                current_section = "admin"
                admin_text = line.split(":", 1)[1].strip().lower()
                result["requires_admin"] = admin_text in ['yes', 'true', 'required']
            # Continue multi-line sections
            elif current_section == "explanation" and line:
                result["explanation"] += " " + line
            elif current_section == "risks" and line and not line.lower().startswith("requires"):
                result["risks"].append(line)
        
        # Fallback: if no command found, try to extract it from code blocks
        if not result["command"]:
            import re
            code_block = re.search(r'```(?:powershell)?\s*(.+?)```', response, re.DOTALL)
            if code_block:
                result["command"] = code_block.group(1).strip()
            else:
                # Last resort: assume first non-empty line is the command
                for line in lines:
                    if line.strip() and not line.strip().startswith('#'):
                        result["command"] = line.strip().strip('`').strip()
                        break
        
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
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    async def check_connection(self) -> bool:
        """
        Check connection to Ollama server (async wrapper)
        
        Returns:
            True if connected
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.is_available)
