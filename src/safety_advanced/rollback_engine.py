"""
Rollback Engine - Generates and executes rollback scripts
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RollbackAction:
    """Represents a single rollback action"""
    action_type: str  # 'restore_file', 'restore_registry', 'start_service', etc.
    target: str
    original_value: Optional[str]
    rollback_command: str


class RollbackEngine:
    """Generates rollback plans and executes them"""
    
    def __init__(self):
        """Initialize rollback engine"""
        self.rollback_history = []
    
    def create_file_deletion_rollback(self, file_paths: List[str], 
                                     backup_id: str) -> List[RollbackAction]:
        """
        Create rollback plan for file deletion
        
        Args:
            file_paths: Files that will be deleted
            backup_id: ID of backup containing these files
            
        Returns:
            List of rollback actions
        """
        actions = []
        
        for file_path in file_paths:
            actions.append(RollbackAction(
                action_type='restore_file',
                target=file_path,
                original_value=backup_id,
                rollback_command=f"Restore from backup {backup_id}"
            ))
        
        return actions
    
    def create_service_stop_rollback(self, services: List[Dict[str, Any]]) -> List[RollbackAction]:
        """
        Create rollback plan for stopping services
        
        Args:
            services: List of services that will be stopped
            
        Returns:
            List of rollback actions
        """
        actions = []
        
        for svc in services:
            if svc.get('status', '').lower() == 'running':
                actions.append(RollbackAction(
                    action_type='start_service',
                    target=svc['name'],
                    original_value='running',
                    rollback_command=f"Start-Service -Name '{svc['name']}'"
                ))
        
        return actions
    
    def create_registry_deletion_rollback(self, registry_keys: List[str]) -> List[RollbackAction]:
        """
        Create rollback plan for registry key deletion
        
        Args:
            registry_keys: Registry keys that will be deleted
            
        Returns:
            List of rollback actions
        """
        actions = []
        
        for key in registry_keys:
            actions.append(RollbackAction(
                action_type='restore_registry',
                target=key,
                original_value=None,
                rollback_command=f"Manual restoration required for {key}"
            ))
        
        return actions
    
    def generate_rollback_script(self, actions: List[RollbackAction]) -> str:
        """
        Generate PowerShell script for rollback
        
        Args:
            actions: List of rollback actions
            
        Returns:
            PowerShell script content
        """
        script_lines = [
            "# Rollback Script",
            f"# Generated: {datetime.now().isoformat()}",
            "# WARNING: Review this script before execution",
            "",
            "Write-Host 'Starting rollback operations...'",
            ""
        ]
        
        for i, action in enumerate(actions, 1):
            script_lines.append(f"# Step {i}: {action.action_type}")
            script_lines.append(f"Write-Host 'Step {i}: {action.action_type} - {action.target}'")
            
            if action.action_type == 'start_service':
                script_lines.append(f"try {{")
                script_lines.append(f"    {action.rollback_command}")
                script_lines.append(f"    Write-Host '  Success'")
                script_lines.append(f"}} catch {{")
                script_lines.append(f"    Write-Host '  Failed: ' + $_.Exception.Message")
                script_lines.append(f"}}")
            else:
                script_lines.append(f"# {action.rollback_command}")
            
            script_lines.append("")
        
        script_lines.append("Write-Host 'Rollback complete'")
        
        return "\n".join(script_lines)
    
    def save_rollback_plan(self, actions: List[RollbackAction], 
                          operation_id: str, filepath: str = None) -> str:
        """
        Save rollback plan to file
        
        Args:
            actions: Rollback actions
            operation_id: ID of the operation
            filepath: Optional custom filepath
            
        Returns:
            Path to saved rollback script
        """
        if filepath is None:
            from pathlib import Path
            rollback_dir = Path("./rollback_scripts")
            rollback_dir.mkdir(exist_ok=True)
            filepath = str(rollback_dir / f"rollback_{operation_id}.ps1")
        
        script = self.generate_rollback_script(actions)
        
        try:
            with open(filepath, 'w') as f:
                f.write(script)
            
            logger.info(f"Rollback script saved: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Failed to save rollback script: {e}")
            return None
    
    def get_rollback_summary(self, actions: List[RollbackAction]) -> str:
        """
        Get human-readable summary of rollback plan
        
        Args:
            actions: Rollback actions
            
        Returns:
            Formatted summary
        """
        lines = [
            "🔄 Rollback Plan:",
            ""
        ]
        
        action_counts = {}
        for action in actions:
            action_counts[action.action_type] = action_counts.get(action.action_type, 0) + 1
        
        for action_type, count in action_counts.items():
            lines.append(f"  • {action_type.replace('_', ' ').title()}: {count} item(s)")
        
        lines.append("")
        lines.append("This rollback plan will:")
        for i, action in enumerate(actions[:5], 1):
            lines.append(f"  {i}. {action.action_type.replace('_', ' ').title()}: {action.target}")
        
        if len(actions) > 5:
            lines.append(f"  ... and {len(actions) - 5} more actions")
        
        return "\n".join(lines)
