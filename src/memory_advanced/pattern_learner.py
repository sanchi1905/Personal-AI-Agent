"""
Pattern Learner - Learns from user command patterns and behavior
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CommandPattern:
    """Represents a learned command pattern"""
    command_template: str
    frequency: int
    success_rate: float
    avg_execution_time: float
    last_used: str
    contexts: List[str]  # Contexts where this command is used


class PatternLearner:
    """Learns patterns from user command history"""
    
    def __init__(self, patterns_file: str = "./memory/learned_patterns.json"):
        """
        Initialize pattern learner
        
        Args:
            patterns_file: Path to patterns file
        """
        self.patterns_file = Path(patterns_file)
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        self.patterns: Dict[str, CommandPattern] = self._load_patterns()
        
        # Command sequences (what commands follow what)
        self.command_sequences: Dict[str, Counter] = defaultdict(Counter)
        self._load_sequences()
    
    def _load_patterns(self) -> Dict[str, CommandPattern]:
        """Load learned patterns from disk"""
        if not self.patterns_file.exists():
            return {}
        
        try:
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                return {
                    k: CommandPattern(**v) for k, v in data['patterns'].items()
                } if 'patterns' in data else {}
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
            return {}
    
    def _save_patterns(self):
        """Save patterns to disk"""
        try:
            data = {
                'patterns': {k: asdict(v) for k, v in self.patterns.items()},
                'sequences': {
                    k: dict(v) for k, v in self.command_sequences.items()
                }
            }
            with open(self.patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
    
    def _load_sequences(self):
        """Load command sequences"""
        if not self.patterns_file.exists():
            return
        
        try:
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                if 'sequences' in data:
                    for cmd, next_cmds in data['sequences'].items():
                        self.command_sequences[cmd] = Counter(next_cmds)
        except Exception as e:
            logger.error(f"Failed to load sequences: {e}")
    
    def record_command(self, command: str, success: bool, 
                      execution_time: float, context: str = 'general'):
        """
        Record a command execution for learning
        
        Args:
            command: Command that was executed
            success: Whether it succeeded
            execution_time: Time taken to execute
            context: Context in which command was used
        """
        # Normalize command to template
        template = self._normalize_command(command)
        
        if template in self.patterns:
            pattern = self.patterns[template]
            
            # Update frequency
            pattern.frequency += 1
            
            # Update success rate
            total_executions = pattern.frequency
            current_successes = pattern.success_rate * (total_executions - 1)
            new_successes = current_successes + (1 if success else 0)
            pattern.success_rate = new_successes / total_executions
            
            # Update avg execution time
            pattern.avg_execution_time = (
                (pattern.avg_execution_time * (total_executions - 1) + execution_time) 
                / total_executions
            )
            
            # Update last used
            pattern.last_used = datetime.now().isoformat()
            
            # Add context if new
            if context not in pattern.contexts:
                pattern.contexts.append(context)
        else:
            # New pattern
            self.patterns[template] = CommandPattern(
                command_template=template,
                frequency=1,
                success_rate=1.0 if success else 0.0,
                avg_execution_time=execution_time,
                last_used=datetime.now().isoformat(),
                contexts=[context]
            )
        
        self._save_patterns()
    
    def record_sequence(self, previous_command: str, current_command: str):
        """
        Record a command sequence
        
        Args:
            previous_command: Previous command
            current_command: Current command
        """
        prev_template = self._normalize_command(previous_command)
        curr_template = self._normalize_command(current_command)
        
        self.command_sequences[prev_template][curr_template] += 1
        self._save_patterns()
    
    def _normalize_command(self, command: str) -> str:
        """
        Normalize command to a template
        
        Args:
            command: Raw command
            
        Returns:
            Command template
        """
        # Extract command name
        parts = command.split()
        if not parts:
            return command
        
        cmd_name = parts[0]
        
        # Common PowerShell commands
        if cmd_name in ['Get-Process', 'Get-Service', 'Get-ChildItem', 
                       'Stop-Service', 'Start-Service', 'Remove-Item']:
            # Keep command structure, replace specific values with placeholders
            template = cmd_name
            
            # Add key parameters
            if '-Name' in command:
                template += ' -Name <name>'
            if '-Path' in command:
                template += ' -Path <path>'
            if '-Filter' in command:
                template += ' -Filter <filter>'
            
            return template
        
        return cmd_name
    
    def get_frequent_commands(self, limit: int = 10) -> List[CommandPattern]:
        """
        Get most frequently used commands
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of command patterns
        """
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.frequency,
            reverse=True
        )
        return sorted_patterns[:limit]
    
    def get_successful_commands(self, min_success_rate: float = 0.8) -> List[CommandPattern]:
        """
        Get commands with high success rate
        
        Args:
            min_success_rate: Minimum success rate (0-1)
            
        Returns:
            List of command patterns
        """
        return [
            p for p in self.patterns.values()
            if p.success_rate >= min_success_rate and p.frequency >= 3
        ]
    
    def predict_next_command(self, current_command: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Predict likely next commands
        
        Args:
            current_command: Current command
            top_n: Number of predictions
            
        Returns:
            List of (command, probability) tuples
        """
        template = self._normalize_command(current_command)
        
        if template not in self.command_sequences:
            return []
        
        next_cmds = self.command_sequences[template]
        total = sum(next_cmds.values())
        
        predictions = [
            (cmd, count / total)
            for cmd, count in next_cmds.most_common(top_n)
        ]
        
        return predictions
    
    def get_commands_by_context(self, context: str) -> List[CommandPattern]:
        """
        Get commands used in a specific context
        
        Args:
            context: Context name
            
        Returns:
            List of command patterns
        """
        return [
            p for p in self.patterns.values()
            if context in p.contexts
        ]
    
    def get_statistics(self) -> Dict[str, any]:
        """Get learning statistics"""
        if not self.patterns:
            return {
                'total_patterns': 0,
                'total_executions': 0,
                'avg_success_rate': 0.0,
                'most_common': None,
                'most_active_context': 'general'
            }
        
        total_executions = sum(p.frequency for p in self.patterns.values())
        weighted_success = sum(
            p.success_rate * p.frequency for p in self.patterns.values()
        )
        avg_success_rate = weighted_success / total_executions if total_executions > 0 else 0.0
        
        most_common = max(self.patterns.values(), key=lambda p: p.frequency)
        
        # Find most active context
        context_counts = {}
        for pattern in self.patterns.values():
            for ctx in pattern.contexts:
                context_counts[ctx] = context_counts.get(ctx, 0) + pattern.frequency
        
        most_active_context = max(context_counts.items(), key=lambda x: x[1])[0] if context_counts else 'general'
        
        return {
            'total_patterns': len(self.patterns),
            'total_executions': total_executions,
            'avg_success_rate': avg_success_rate,
            'most_common': most_common.command_template,
            'most_active_context': most_active_context
        }
