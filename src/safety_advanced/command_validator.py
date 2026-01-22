"""
Command Validator - Validates PowerShell commands before execution
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CommandValidator:
    """Validates PowerShell command syntax and structure"""
    
    # Common PowerShell cmdlets with their typical parameters
    VALID_CMDLETS = {
        'Get-ChildItem': ['-Path', '-Filter', '-Recurse', '-File', '-Directory', '-Force', '-Name'],
        'Get-Location': [],
        'Set-Location': ['-Path'],
        'Get-Process': ['-Name', '-Id', '-ComputerName'],
        'Get-Service': ['-Name', '-DisplayName', '-ComputerName'],
        'Get-Content': ['-Path', '-TotalCount', '-Tail', '-Wait'],
        'Get-Item': ['-Path', '-Force'],
        'Get-ItemProperty': ['-Path', '-Name'],
        'Get-ComputerInfo': ['-Property'],
        'Get-AppxPackage': ['-Name', '-AllUsers', '-PackageTypeFilter'],
        'Get-WmiObject': ['-Class', '-ComputerName', '-Filter', '-Property'],
        'Select-Object': ['-Property', '-First', '-Last', '-Skip', '-Unique'],
        'Where-Object': ['-Property', '-Value', '-FilterScript'],
        'Format-Table': ['-Property', '-AutoSize', '-Wrap'],
        'Format-List': ['-Property'],
        'Sort-Object': ['-Property', '-Descending', '-Unique'],
        'Measure-Object': ['-Property', '-Sum', '-Average', '-Maximum', '-Minimum'],
        'Test-Path': ['-Path', '-PathType'],
    }
    
    def validate_syntax(self, command: str) -> Dict[str, Any]:
        """
        Validate PowerShell command syntax
        
        Args:
            command: Command to validate
            
        Returns:
            Validation result with suggestions
        """
        command = command.strip()
        
        if not command:
            return {
                'valid': False,
                'error': 'Empty command',
                'suggestions': ['Provide a valid PowerShell command']
            }
        
        # Check for common syntax errors
        errors = []
        suggestions = []
        
        # Check for balanced quotes
        if command.count('"') % 2 != 0:
            errors.append('Unbalanced double quotes')
            suggestions.append('Ensure all quotes are properly closed')
        
        if command.count("'") % 2 != 0:
            errors.append('Unbalanced single quotes')
            suggestions.append('Ensure all quotes are properly closed')
        
        # Check for balanced parentheses
        if command.count('(') != command.count(')'):
            errors.append('Unbalanced parentheses')
            suggestions.append('Check opening and closing parentheses')
        
        # Check for balanced braces
        if command.count('{') != command.count('}'):
            errors.append('Unbalanced curly braces')
            suggestions.append('Check opening and closing braces')
        
        # Extract cmdlet name
        parts = command.split()
        if parts:
            cmdlet = parts[0]
            
            # Check if it's a known cmdlet
            if '-' in cmdlet and cmdlet not in self.VALID_CMDLETS:
                # Check for common misspellings
                similar = self._find_similar_cmdlet(cmdlet)
                if similar:
                    suggestions.append(f'Did you mean: {similar}?')
            
            # Validate parameters
            param_errors = self._validate_parameters(command, cmdlet)
            errors.extend(param_errors)
        
        if errors:
            return {
                'valid': False,
                'errors': errors,
                'suggestions': suggestions
            }
        
        return {
            'valid': True,
            'warnings': self._get_warnings(command)
        }
    
    def _validate_parameters(self, command: str, cmdlet: str) -> List[str]:
        """Validate command parameters"""
        errors = []
        
        if cmdlet not in self.VALID_CMDLETS:
            return errors
        
        # Extract parameters from command
        param_pattern = r'-(\w+)'
        params = re.findall(param_pattern, command)
        
        valid_params = self.VALID_CMDLETS[cmdlet]
        
        for param in params:
            param_with_dash = f'-{param}'
            if valid_params and param_with_dash not in valid_params:
                # Check if it's a common parameter (available for all cmdlets)
                common_params = ['-ErrorAction', '-WarningAction', '-Verbose', '-Debug', '-OutVariable']
                if param_with_dash not in common_params:
                    errors.append(f'Unknown parameter -{param} for {cmdlet}')
        
        return errors
    
    def _find_similar_cmdlet(self, cmdlet: str) -> str:
        """Find similar cmdlet for typo suggestions"""
        cmdlet_lower = cmdlet.lower()
        
        # Simple similarity check
        for valid_cmdlet in self.VALID_CMDLETS.keys():
            if cmdlet_lower in valid_cmdlet.lower() or valid_cmdlet.lower() in cmdlet_lower:
                return valid_cmdlet
        
        return ""
    
    def _get_warnings(self, command: str) -> List[str]:
        """Get warnings for potentially problematic commands"""
        warnings = []
        
        command_lower = command.lower()
        
        # Check for wildcard usage
        if '*' in command and 'remove' in command_lower:
            warnings.append('Using wildcards with Remove commands can be dangerous')
        
        # Check for -Force parameter
        if '-force' in command_lower:
            warnings.append('Using -Force will suppress confirmations')
        
        # Check for -Recurse with destructive operations
        if '-recurse' in command_lower and any(op in command_lower for op in ['remove', 'delete']):
            warnings.append('Recursive deletion can affect many files')
        
        return warnings
    
    def suggest_improvements(self, command: str) -> List[str]:
        """Suggest improvements for the command"""
        suggestions = []
        
        command_lower = command.lower()
        
        # Suggest Format-Table for readability
        if 'get-' in command_lower and 'format-' not in command_lower:
            suggestions.append('Consider adding | Format-Table for better readability')
        
        # Suggest ErrorAction for safer execution
        if 'get-' in command_lower and '-erroraction' not in command_lower:
            suggestions.append('Consider adding -ErrorAction SilentlyContinue for safer execution')
        
        # Suggest proper cmdlet usage over aliases
        aliases = {
            'dir': 'Get-ChildItem',
            'ls': 'Get-ChildItem',
            'cd': 'Set-Location',
            'pwd': 'Get-Location',
            'cat': 'Get-Content',
            'type': 'Get-Content',
        }
        
        first_word = command.split()[0] if command.split() else ""
        if first_word.lower() in aliases:
            suggestions.append(f'Use {aliases[first_word.lower()]} instead of {first_word}')
        
        return suggestions


def get_validator() -> CommandValidator:
    """Get singleton validator instance"""
    global _validator_instance
    if '_validator_instance' not in globals():
        _validator_instance = CommandValidator()
    return _validator_instance
