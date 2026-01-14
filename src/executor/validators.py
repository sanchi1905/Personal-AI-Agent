"""
Command Validators - Safety checks for commands before execution
"""

import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class CommandValidator:
    """Validates commands for safety before execution"""
    
    # Dangerous patterns that should be blocked or require extra confirmation
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s+/',
        r'Remove-Item.*-Recurse.*C:\\',
        r'format\s+[a-zA-Z]:',
        r'reg\s+delete.*HKLM',
        r'bcdedit',
        r'diskpart',
        r'cipher\s+/w',
    ]
    
    # Commands that require admin privileges
    ADMIN_REQUIRED_KEYWORDS = [
        'reg delete', 'reg add',
        'sc stop', 'sc delete',
        'net stop', 'net start',
        'Set-Service',
        'Remove-Service'
    ]
    
    # Safe commands that can be executed without confirmation
    SAFE_COMMANDS = [
        'Get-Process', 'Get-Service', 'Get-ChildItem',
        'Test-Path', 'Get-Content', 'Get-Location',
        'Get-Date', 'Get-Help'
    ]
    
    @staticmethod
    def validate(command: str) -> Tuple[bool, List[str], str]:
        """
        Validate a command for safety
        
        Args:
            command: PowerShell command to validate
            
        Returns:
            Tuple of (is_safe, warnings, risk_level)
            - is_safe: Whether command can proceed
            - warnings: List of warnings/concerns
            - risk_level: 'safe', 'caution', 'dangerous'
        """
        warnings = []
        
        # Check for dangerous patterns
        for pattern in CommandValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, ["Command contains dangerous operation"], "dangerous"
        
        # Check if it's a known safe command
        for safe_cmd in CommandValidator.SAFE_COMMANDS:
            if command.strip().startswith(safe_cmd):
                return True, [], "safe"
        
        # Check for admin requirements
        requires_admin = any(
            keyword.lower() in command.lower() 
            for keyword in CommandValidator.ADMIN_REQUIRED_KEYWORDS
        )
        
        if requires_admin:
            warnings.append("Requires administrator privileges")
        
        # Check for file/folder deletions
        if re.search(r'Remove-Item|rm|del\s+', command, re.IGNORECASE):
            warnings.append("This command will delete files/folders")
            return True, warnings, "caution"
        
        # Check for registry modifications
        if 'reg ' in command.lower() or 'registry' in command.lower():
            warnings.append("This command modifies the Windows registry")
            return True, warnings, "caution"
        
        # Default: proceed with caution
        if warnings:
            return True, warnings, "caution"
        
        return True, [], "safe"
    
    @staticmethod
    def requires_admin(command: str) -> bool:
        """
        Check if command requires administrator privileges
        
        Args:
            command: PowerShell command
            
        Returns:
            True if admin required
        """
        return any(
            keyword.lower() in command.lower()
            for keyword in CommandValidator.ADMIN_REQUIRED_KEYWORDS
        )
    
    @staticmethod
    def is_destructive(command: str) -> bool:
        """
        Check if command performs destructive operations
        
        Args:
            command: PowerShell command
            
        Returns:
            True if command is destructive
        """
        destructive_keywords = [
            'remove', 'delete', 'del', 'rm', 'format',
            'clear', 'erase', 'wipe'
        ]
        
        return any(
            keyword in command.lower()
            for keyword in destructive_keywords
        )
