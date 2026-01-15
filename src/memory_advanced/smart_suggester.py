"""
Smart Suggester - Provides intelligent command suggestions
"""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SmartSuggester:
    """Provides smart command suggestions based on context and history"""
    
    def __init__(self, pattern_learner, user_preferences):
        """
        Initialize smart suggester
        
        Args:
            pattern_learner: PatternLearner instance
            user_preferences: UserPreferences instance
        """
        self.pattern_learner = pattern_learner
        self.user_preferences = user_preferences
    
    def suggest_for_intent(self, user_intent: str, context: str = 'general') -> List[str]:
        """
        Suggest commands for a given user intent
        
        Args:
            user_intent: User's natural language intent
            context: Current context
            
        Returns:
            List of suggested commands
        """
        suggestions = []
        intent_lower = user_intent.lower()
        
        # Check learned patterns for similar intents
        context_patterns = self.pattern_learner.get_commands_by_context(context)
        
        # Intent-based suggestions
        if 'list' in intent_lower or 'show' in intent_lower:
            if 'process' in intent_lower or 'running' in intent_lower:
                suggestions.append('Get-Process | Sort-Object CPU -Descending | Select-Object -First 10')
            elif 'service' in intent_lower:
                suggestions.append('Get-Service | Where-Object {$_.Status -eq "Running"}')
            elif 'app' in intent_lower or 'install' in intent_lower:
                suggestions.append('list apps')
            elif 'disk' in intent_lower or 'drive' in intent_lower:
                suggestions.append('Get-PSDrive')
        
        elif 'stop' in intent_lower:
            if 'service' in intent_lower:
                suggestions.append('Stop-Service -Name <service_name>')
        
        elif 'disk' in intent_lower or 'space' in intent_lower:
            suggestions.append('Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free')
        
        elif 'memory' in intent_lower or 'ram' in intent_lower:
            suggestions.append('Get-WmiObject Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory')
        
        # Add frequently used commands from context
        for pattern in context_patterns[:3]:
            if pattern.success_rate > 0.7:
                suggestions.append(pattern.command_template)
        
        return suggestions[:5]  # Return top 5
    
    def suggest_after_command(self, last_command: str) -> List[Tuple[str, float]]:
        """
        Suggest next command based on previous command
        
        Args:
            last_command: Last executed command
            
        Returns:
            List of (command, confidence) tuples
        """
        predictions = self.pattern_learner.predict_next_command(last_command)
        return predictions
    
    def suggest_alternatives(self, failed_command: str) -> List[str]:
        """
        Suggest alternative commands after a failure
        
        Args:
            failed_command: Command that failed
            
        Returns:
            List of alternative commands
        """
        alternatives = []
        
        # Get successful similar commands
        successful = self.pattern_learner.get_successful_commands()
        
        # Find commands with similar structure
        cmd_parts = failed_command.split()
        if cmd_parts:
            cmd_name = cmd_parts[0]
            
            for pattern in successful:
                if cmd_name in pattern.command_template:
                    alternatives.append(pattern.command_template)
        
        return alternatives[:3]
    
    def get_personalized_shortcuts(self) -> Dict[str, str]:
        """
        Get personalized command shortcuts based on usage
        
        Returns:
            Dictionary of shortcut to command
        """
        frequent = self.pattern_learner.get_frequent_commands(10)
        
        shortcuts = {}
        for i, pattern in enumerate(frequent, 1):
            # Create shortcut from command
            cmd_name = pattern.command_template.split()[0].lower()
            shortcut = f"quick{i}"
            shortcuts[shortcut] = pattern.command_template
        
        return shortcuts
    
    def suggest_optimizations(self, command: str) -> List[str]:
        """
        Suggest optimizations for a command
        
        Args:
            command: Command to optimize
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Check for common inefficiencies
        if 'Get-ChildItem' in command and '-Recurse' in command:
            if '-Filter' not in command:
                suggestions.append("Add -Filter parameter to improve performance")
        
        if 'Get-Process' in command:
            if 'Select-Object' not in command:
                suggestions.append("Use Select-Object to limit output properties")
        
        if '|' in command:
            # Multiple pipes
            pipe_count = command.count('|')
            if pipe_count > 3:
                suggestions.append("Consider reducing pipeline complexity for better performance")
        
        return suggestions
    
    def format_suggestion(self, suggestion: str, confidence: float = None) -> str:
        """
        Format a suggestion for display
        
        Args:
            suggestion: Suggestion text
            confidence: Optional confidence score
            
        Returns:
            Formatted suggestion
        """
        if confidence is not None:
            return f"💡 {suggestion} (confidence: {confidence:.0%})"
        return f"💡 {suggestion}"
