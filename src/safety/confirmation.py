"""
Confirmation Handler - Manages user confirmations for operations
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConfirmationRequest:
    """Represents a request for user confirmation"""
    
    def __init__(self, operation: str, command: str, explanation: str,
                 warnings: list, risk_level: str):
        self.operation = operation
        self.command = command
        self.explanation = explanation
        self.warnings = warnings
        self.risk_level = risk_level
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "operation": self.operation,
            "command": self.command,
            "explanation": self.explanation,
            "warnings": self.warnings,
            "risk_level": self.risk_level,
            "timestamp": self.timestamp.isoformat()
        }


class ConfirmationHandler:
    """Handles the 'Explain → Confirm → Execute' flow"""
    
    def __init__(self, require_confirmation: bool = True):
        """
        Initialize confirmation handler
        
        Args:
            require_confirmation: Whether to require user confirmation
        """
        self.require_confirmation = require_confirmation
        self.pending_confirmations = {}
    
    def create_request(self, operation: str, command: str, 
                       explanation: str, warnings: list = None,
                       risk_level: str = "safe") -> str:
        """
        Create a confirmation request
        
        Args:
            operation: Description of the operation
            command: The actual command to execute
            explanation: Detailed explanation of what will happen
            warnings: List of warnings
            risk_level: Risk level (safe/caution/dangerous)
            
        Returns:
            Request ID for tracking
        """
        request_id = f"req_{datetime.now().timestamp()}"
        
        request = ConfirmationRequest(
            operation=operation,
            command=command,
            explanation=explanation,
            warnings=warnings or [],
            risk_level=risk_level
        )
        
        self.pending_confirmations[request_id] = request
        
        logger.info(f"Created confirmation request {request_id}")
        return request_id
    
    def get_request(self, request_id: str) -> Optional[ConfirmationRequest]:
        """
        Get a pending confirmation request
        
        Args:
            request_id: Request ID
            
        Returns:
            ConfirmationRequest or None
        """
        return self.pending_confirmations.get(request_id)
    
    def approve(self, request_id: str) -> bool:
        """
        Approve a confirmation request
        
        Args:
            request_id: Request ID
            
        Returns:
            True if approved successfully
        """
        if request_id in self.pending_confirmations:
            logger.info(f"Request {request_id} approved")
            # Keep in dict for audit trail
            return True
        return False
    
    def deny(self, request_id: str, reason: str = "User declined"):
        """
        Deny a confirmation request
        
        Args:
            request_id: Request ID
            reason: Reason for denial
        """
        if request_id in self.pending_confirmations:
            logger.info(f"Request {request_id} denied: {reason}")
            del self.pending_confirmations[request_id]
    
    def format_for_user(self, request: ConfirmationRequest) -> str:
        """
        Format a confirmation request for user display
        
        Args:
            request: ConfirmationRequest object
            
        Returns:
            Formatted string for display
        """
        # Strip any backticks from the command for display
        clean_command = request.command.strip('`').strip()
        
        output = []
        output.append(f"🔍 Operation: {request.operation}")
        output.append(f"\n📝 Explanation:\n{request.explanation}")
        output.append(f"\n💻 Command to execute:\n{clean_command}")
        
        if request.warnings:
            output.append(f"\n⚠️  Warnings:")
            for warning in request.warnings:
                output.append(f"  • {warning}")
        
        risk_emoji = {
            "safe": "✅",
            "caution": "⚠️",
            "dangerous": "🛑"
        }
        output.append(f"\n{risk_emoji.get(request.risk_level, '❓')} Risk Level: {request.risk_level.upper()}")
        
        return "\n".join(output)
