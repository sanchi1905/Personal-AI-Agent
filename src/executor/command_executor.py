"""
Command Executor - Safely executes PowerShell commands with logging
"""

import subprocess
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ExecutionResult:
    """Result of a command execution"""
    
    def __init__(self, success: bool, stdout: str, stderr: str, 
                 return_code: int, execution_time: float):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.execution_time = execution_time
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "return_code": self.return_code,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }


class CommandExecutor:
    """Safely executes PowerShell commands with logging and validation"""
    
    def __init__(self, dry_run: bool = False, log_path: Optional[str] = None):
        """
        Initialize command executor
        
        Args:
            dry_run: If True, only simulate execution
            log_path: Path to save execution logs
        """
        self.dry_run = dry_run
        self.log_path = log_path
        self.execution_history = []
    
    async def execute(self, command: str, timeout: int = 30, 
                     require_admin: bool = False) -> ExecutionResult:
        """
        Execute a PowerShell command
        
        Args:
            command: PowerShell command to execute
            timeout: Maximum execution time in seconds
            require_admin: Whether admin privileges are required
            
        Returns:
            ExecutionResult object
        """
        # Strip any markdown backticks that might be in the command
        command = command.strip('`').strip()
        
        logger.info(f"Executing command: {command}")
        
        if self.dry_run:
            logger.info("DRY RUN MODE - Command not actually executed")
            return ExecutionResult(
                success=True,
                stdout=f"[DRY RUN] Would execute: {command}",
                stderr="",
                return_code=0,
                execution_time=0.0
            )
        
        start_time = datetime.now()
        
        try:
            # Execute PowerShell command
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            exec_result = ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time
            )
            
            # Log execution
            self._log_execution(command, exec_result)
            
            return exec_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                return_code=-1,
                execution_time=timeout
            )
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=0.0
            )
    
    def _log_execution(self, command: str, result: ExecutionResult):
        """
        Log command execution to file
        
        Args:
            command: Executed command
            result: Execution result
        """
        log_entry = {
            "command": command,
            "result": result.to_dict()
        }
        
        self.execution_history.append(log_entry)
        
        if self.log_path:
            try:
                with open(self.log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + '\n')
            except Exception as e:
                logger.error(f"Failed to write log: {e}")
    
    def get_history(self, limit: int = 10) -> list:
        """
        Get recent execution history
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent executions
        """
        return self.execution_history[-limit:]
