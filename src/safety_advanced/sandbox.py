"""
Command Sandbox - Allowlist/denylist for command validation
"""

import re
import logging
from typing import List, Set, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CommandSandbox:
    """Validates commands against allowlist and denylist"""
    
    # Critical system paths that should never be modified
    PROTECTED_PATHS = {
        r"C:\Windows\System32",
        r"C:\Windows\SysWOW64",
        r"C:\Windows\WinSxS",
        r"C:\Program Files\WindowsApps",
        r"C:\Windows\Boot",
    }
    
    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        r"format\s+[a-z]:",  # Format drive
        r"cipher\s+/w",  # Wipe free space
        r"takeown\s+/f.*\\windows",  # Take ownership of Windows files
        r"icacls.*\\windows.*\/grant",  # Modify Windows permissions
        r"reg\s+delete.*\\windows",  # Delete Windows registry keys
        r"Remove-Item.*-Recurse.*C:\\\\Windows",  # Delete Windows folder
        r"rm\s+-rf\s+/",  # Linux-style dangerous delete
        r"del\s+/[fqs]\s+C:\\\\Windows",  # Delete Windows via cmd
        r"rd\s+/s\s+/q.*C:\\\\Windows",  # Remove Windows directory
    ]
    
    # Safe read-only commands that are always allowed
    SAFE_COMMANDS = {
        'get-location',
        'get-childitem',
        'get-content',
        'get-process',
        'get-service',
        'get-computerinfo',
        'get-date',
        'get-help',
        'get-item',
        'get-itemproperty',
        'select-object',
        'where-object',
        'format-table',
        'format-list',
        'measure-object',
        'sort-object',
        'test-path',
        'get-appxpackage',
        'get-wmiobject',
        'systeminfo',
        'ipconfig',
        'netstat',
        'tasklist',
    }
    
    # Commands that require explicit user approval
    HIGH_RISK_COMMANDS = {
        'format-volume',
        'clear-disk',
        'initialize-disk',
        'remove-partition',
        'disable-windowsupdate',
        'set-executionpolicy unrestricted',
    }
    
    def __init__(self, config_file: str = "./config/sandbox.json"):
        """
        Initialize command sandbox
        
        Args:
            config_file: Path to sandbox configuration
        """
        self.config_file = Path(config_file)
        self.custom_denylist: Set[str] = set()
        self.custom_allowlist: Set[str] = set()
        self._load_config()
    
    def _load_config(self):
        """Load sandbox configuration"""
        if not self.config_file.exists():
            return
        
        try:
            import json
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.custom_denylist = set(config.get('denylist', []))
                self.custom_allowlist = set(config.get('allowlist', []))
        except Exception as e:
            logger.error(f"Failed to load sandbox config: {e}")
    
    def validate_command(self, command: str) -> Dict[str, Any]:
        """
        Validate command against sandbox rules
        
        Args:
            command: Command to validate
            
        Returns:
            Validation result with status and details
        """
        command_lower = command.lower().strip()
        
        # Extract the first cmdlet/command name
        first_word = command_lower.split()[0] if command_lower.split() else ""
        
        # Check if it's a known safe command
        is_safe_cmd = any(safe_cmd in first_word for safe_cmd in self.SAFE_COMMANDS)
        
        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command_lower):
                return {
                    'allowed': False,
                    'reason': 'Matches dangerous pattern - this command could cause severe system damage',
                    'risk_level': 'CRITICAL',
                    'pattern': pattern,
                    'recommendation': 'Command blocked for safety. Please verify your intent.'
                }
        
        # Check protected paths
        for path in self.PROTECTED_PATHS:
            if path.lower() in command_lower:
                # Check if it's a destructive operation
                if any(word in command_lower for word in ['remove', 'delete', 'del ', 'rd ', 'rm ']):
                    return {
                        'allowed': False,
                        'reason': 'Targets protected system path with destructive operation',
                        'risk_level': 'CRITICAL',
                        'path': path,
                        'recommendation': 'Do not modify critical system directories'
                    }
        
        # Check custom denylist
        for denied_cmd in self.custom_denylist:
            if denied_cmd.lower() in command_lower:
                return {
                    'allowed': False,
                    'reason': 'Command in user denylist',
                    'risk_level': 'HIGH',
                    'command': denied_cmd
                }
        
        # Check high-risk commands
        for high_risk in self.HIGH_RISK_COMMANDS:
            if high_risk in command_lower:
                return {
                    'allowed': True,
                    'reason': 'High-risk command requires explicit approval',
                    'risk_level': 'HIGH',
                    'requires_extra_confirmation': True,
                    'command': high_risk
                }
        
        # If it's a known safe command, mark as low risk
        if is_safe_cmd:
            return {
                'allowed': True,
                'reason': 'Safe read-only command',
                'risk_level': 'LOW'
            }
        
        # Unknown command - medium risk by default
        return {
            'allowed': True,
            'reason': 'Command passed safety checks but is not in safe list',
            'risk_level': 'MEDIUM',
            'recommendation': 'Review command carefully before executing'
        }
    
    def add_to_denylist(self, pattern: str) -> bool:
        """
        Add pattern to custom denylist
        
        Args:
            pattern: Pattern to deny
            
        Returns:
            True if successful
        """
        self.custom_denylist.add(pattern)
        return self._save_config()
    
    def add_to_allowlist(self, pattern: str) -> bool:
        """
        Add pattern to custom allowlist
        
        Args:
            pattern: Pattern to allow
            
        Returns:
            True if successful
        """
        self.custom_allowlist.add(pattern)
        return self._save_config()
    
    def _save_config(self) -> bool:
        """Save sandbox configuration"""
        try:
            import json
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'denylist': list(self.custom_denylist),
                'allowlist': list(self.custom_allowlist)
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save sandbox config: {e}")
            return False
    
    def get_risk_explanation(self, risk_level: str) -> str:
        """Get explanation for risk level"""
        explanations = {
            'LOW': "✓ This operation is safe and can proceed",
            'MEDIUM': "⚠️ This operation may make system changes. Review carefully.",
            'HIGH': "⚠️⚠️ This operation is risky. Ensure you have backups.",
            'CRITICAL': "🔴 This operation is extremely dangerous and is blocked for safety."
        }
        return explanations.get(risk_level, "Unknown risk level")
