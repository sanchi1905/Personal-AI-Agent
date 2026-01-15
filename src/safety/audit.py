"""
Audit Logger - Maintains audit trail of all operations
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """Logs all agent operations for audit trail"""
    
    def __init__(self, audit_log_path: str = "./logs/audit.jsonl"):
        """
        Initialize audit logger
        
        Args:
            audit_log_path: Path to audit log file
        """
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_request(self, user_request: str, session_id: Optional[str] = None):
        """
        Log a user request
        
        Args:
            user_request: The user's natural language request
            session_id: Optional session identifier
        """
        entry = {
            "event": "user_request",
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "request": user_request
        }
        self._write_entry(entry)
    
    def log_cancellation(self, user_request: str, command: str):
        """
        Log a cancelled command
        
        Args:
            user_request: Original user request
            command: Command that was cancelled
        """
        entry = {
            "event": "command_cancelled",
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "command": command
        }
        self._write_entry(entry)
    
    def log_command_generation(self, request: str, command: Dict[str, Any]):
        """
        Log command generation
        
        Args:
            request: Original user request
            command: Generated command details
        """
        entry = {
            "event": "command_generated",
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "command": command
        }
        self._write_entry(entry)
    
    def log_confirmation(self, request_id: str, approved: bool, 
                        user_id: Optional[str] = None):
        """
        Log user confirmation decision
        
        Args:
            request_id: Confirmation request ID
            approved: Whether user approved
            user_id: Optional user identifier
        """
        entry = {
            "event": "confirmation_decision",
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "approved": approved,
            "user_id": user_id
        }
        self._write_entry(entry)
    
    def log_execution(self, user_request: str, command: str, result: Any):
        """
        Log command execution and result
        
        Args:
            user_request: Original user request
            command: Executed command
            result: Execution result
        """
        # Handle both dict and ExecutionResult objects
        result_data = result if isinstance(result, dict) else {
            "success": getattr(result, 'success', False),
            "stdout": getattr(result, 'stdout', ''),
            "stderr": getattr(result, 'stderr', ''),
            "exit_code": getattr(result, 'exit_code', -1)
        }
        
        entry = {
            "event": "command_executed",
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "command": command,
            "result": result_data
        }
        self._write_entry(entry)
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """
        Log an error
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        entry = {
            "event": "error",
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        self._write_entry(entry)
    
    def _write_entry(self, entry: Dict[str, Any]):
        """
        Write an entry to the audit log
        
        Args:
            entry: Log entry dictionary
        """
        try:
            with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def get_recent_entries(self, limit: int = 50) -> list:
        """
        Get recent audit log entries
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of recent entries
        """
        entries = []
        
        if not self.audit_log_path.exists():
            return entries
        
        try:
            with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-limit:]
                
                for line in recent_lines:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
        
        return entries
