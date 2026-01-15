"""
Dry-Run Mode - Test commands without execution
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DryRunResult:
    """Result of dry-run simulation"""
    command: str
    would_execute: bool
    predicted_changes: List[str]
    potential_risks: List[str]
    estimated_time: str
    requires_admin: bool
    reversible: bool


class DryRunSimulator:
    """Simulates command execution without making changes"""
    
    def __init__(self):
        """Initialize dry-run simulator"""
        self.destructive_patterns = [
            'remove', 'delete', 'uninstall', 'stop-service',
            'disable', 'format', 'clear', 'reset'
        ]
    
    async def simulate_command(self, command: str) -> DryRunResult:
        """
        Simulate command execution
        
        Args:
            command: Command to simulate
            
        Returns:
            DryRunResult with predictions
        """
        command_lower = command.lower()
        
        # Analyze command
        predicted_changes = self._predict_changes(command)
        potential_risks = self._assess_risks(command)
        requires_admin = self._requires_admin(command)
        reversible = self._is_reversible(command)
        
        # Estimate execution time
        estimated_time = "< 1 second"
        if 'uninstall' in command_lower:
            estimated_time = "30 seconds - 2 minutes"
        elif 'stop-service' in command_lower:
            estimated_time = "1-5 seconds"
        
        return DryRunResult(
            command=command,
            would_execute=True,
            predicted_changes=predicted_changes,
            potential_risks=potential_risks,
            estimated_time=estimated_time,
            requires_admin=requires_admin,
            reversible=reversible
        )
    
    def _predict_changes(self, command: str) -> List[str]:
        """Predict what changes the command will make"""
        changes = []
        command_lower = command.lower()
        
        if 'uninstall' in command_lower or 'msiexec' in command_lower:
            changes.append("Application will be removed")
            changes.append("Registry entries will be deleted")
            changes.append("Program files will be removed")
        
        if 'stop-service' in command_lower:
            changes.append("Service will be stopped")
        
        if 'remove-item' in command_lower or 'del ' in command_lower:
            changes.append("Files or folders will be deleted")
        
        if 'set-service' in command_lower and 'disabled' in command_lower:
            changes.append("Service startup type will be changed")
        
        if not changes:
            changes.append("System state will be queried (read-only)")
        
        return changes
    
    def _assess_risks(self, command: str) -> List[str]:
        """Assess potential risks of the command"""
        risks = []
        command_lower = command.lower()
        
        # Check for destructive operations
        is_destructive = any(pattern in command_lower for pattern in self.destructive_patterns)
        
        if is_destructive:
            risks.append("⚠️ Destructive operation - changes may be irreversible")
        
        if 'system32' in command_lower or 'windows' in command_lower:
            risks.append("🔴 Affects system files - high risk")
        
        if 'stop-service' in command_lower:
            service_name = self._extract_service_name(command)
            if service_name:
                risks.append(f"Stopping '{service_name}' may affect dependent services")
        
        if 'msiexec' in command_lower and '/x' in command_lower:
            risks.append("Uninstallation may remove shared components")
        
        if not risks:
            risks.append("✓ Low risk - read-only or safe operation")
        
        return risks
    
    def _requires_admin(self, command: str) -> bool:
        """Check if command requires admin privileges"""
        command_lower = command.lower()
        
        admin_patterns = [
            'stop-service', 'start-service', 'set-service',
            'msiexec', 'checkpoint-computer', 'restore-computer',
            'disable-', 'enable-'
        ]
        
        return any(pattern in command_lower for pattern in admin_patterns)
    
    def _is_reversible(self, command: str) -> bool:
        """Check if command effects are reversible"""
        command_lower = command.lower()
        
        # Read-only commands are always reversible (nothing to reverse)
        if not any(pattern in command_lower for pattern in self.destructive_patterns):
            return True
        
        # Service operations are reversible
        if 'stop-service' in command_lower:
            return True
        
        # File deletions are not easily reversible
        if 'remove-item' in command_lower or 'del ' in command_lower:
            return False
        
        # Uninstalls are typically not reversible
        if 'uninstall' in command_lower or 'msiexec' in command_lower:
            return False
        
        return True
    
    def _extract_service_name(self, command: str) -> Optional[str]:
        """Extract service name from command"""
        import re
        
        # Look for -Name 'ServiceName' pattern
        match = re.search(r"-Name\s+['\"]?([^'\"]+)['\"]?", command, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def format_dry_run_report(self, result: DryRunResult) -> str:
        """Format dry-run result for display"""
        lines = [
            "🔍 DRY-RUN MODE - No changes will be made",
            "",
            f"Command: {result.command}",
            "",
            "Predicted Changes:",
        ]
        
        for change in result.predicted_changes:
            lines.append(f"  • {change}")
        
        lines.append("")
        lines.append("Risk Assessment:")
        for risk in result.potential_risks:
            lines.append(f"  {risk}")
        
        lines.append("")
        lines.append(f"Estimated Time: {result.estimated_time}")
        lines.append(f"Requires Admin: {'Yes' if result.requires_admin else 'No'}")
        lines.append(f"Reversible: {'Yes' if result.reversible else 'No'}")
        
        return "\n".join(lines)
