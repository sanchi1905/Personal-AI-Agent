"""
Command Executor - Safely executes PowerShell commands with logging
"""

import subprocess
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.privilege_manager import get_privilege_manager, PrivilegeCheck
from utils.failure_classifier import get_failure_classifier, FailureAnalysis

logger = logging.getLogger(__name__)


class ExecutionResult:
    """Result of a command execution"""
    
    def __init__(self, success: bool, stdout: str, stderr: str, 
                 return_code: int, execution_time: float, 
                 failure_analysis: Optional[FailureAnalysis] = None):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.execution_time = execution_time
        self.timestamp = datetime.now().isoformat()
        self.failure_analysis = failure_analysis
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "return_code": self.return_code,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }
        
        if self.failure_analysis:
            result["failure_analysis"] = {
                "type": self.failure_analysis.failure_type.value,
                "diagnosis": self.failure_analysis.diagnosis,
                "severity": self.failure_analysis.severity,
                "recoverable": self.failure_analysis.is_recoverable,
                "recovery_steps": self.failure_analysis.recovery_steps,
                "prevention_tips": self.failure_analysis.prevention_tips
            }
        
        return result


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
        self.privilege_manager = get_privilege_manager()
        self.failure_classifier = get_failure_classifier()
    
    async def execute(self, command: str, timeout: int = 30, 
                     operation_type: str = 'general',
                     operation_name: str = "") -> ExecutionResult:
        """
        Execute a PowerShell command with privilege checking
        
        Args:
            command: PowerShell command to execute
            timeout: Maximum execution time in seconds
            operation_type: Type of operation (for privilege checking)
            operation_name: Human-readable operation name
            
        Returns:
            ExecutionResult object
        """
        # Strip any markdown backticks that might be in the command
        command = command.strip('`').strip()
        
        # Check privileges
        priv_check = self.privilege_manager.check_operation(operation_type, operation_name)
        
        if not priv_check.can_proceed:
            logger.warning(f"Insufficient privileges for: {operation_name}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=priv_check.message + "\n\nSuggestions:\n" + "\n".join(f"  • {s}" for s in priv_check.suggestions),
                return_code=-2,
                execution_time=0.0
            )
        
        if priv_check.degraded_mode:
            logger.info(f"Running in degraded mode: {priv_check.message}")
        
        logger.info(f"Executing command: {command}")
        
        if self.dry_run:
            logger.info("DRY RUN MODE - Command not actually executed")
            priv_msg = f"\n[Privilege Status: {priv_check.message}]" if priv_check.degraded_mode else ""
            return ExecutionResult(
                success=True,
                stdout=f"[DRY RUN] Would execute: {command}{priv_msg}",
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
            
            # Analyze failures
            failure_analysis = None
            if result.returncode != 0:
                failure_analysis = self.failure_classifier.classify(
                    error_message=result.stderr or result.stdout,
                    return_code=result.returncode,
                    operation_type=operation_type
                )
                logger.error(f"Command failed: {failure_analysis.diagnosis}")
            
            exec_result = ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                failure_analysis=failure_analysis
            )
            
            # Log execution
            self._log_execution(command, exec_result)
            
            return exec_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds")
            timeout_analysis = self.failure_classifier.classify(
                error_message=f"Command timed out after {timeout} seconds",
                return_code=-1,
                operation_type=operation_type
            )
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                return_code=-1,
                execution_time=timeout,
                failure_analysis=timeout_analysis
            )
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            exception_analysis = self.failure_classifier.classify(
                error_message=str(e),
                return_code=-1,
                operation_type=operation_type
            )
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=0.0,
                failure_analysis=exception_analysis
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
