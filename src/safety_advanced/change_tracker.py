"""
Change Tracker - Monitors and records all system changes
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SystemChange:
    """Represents a system change"""
    change_id: str
    timestamp: str
    change_type: str  # 'file_deleted', 'service_stopped', 'registry_modified', etc.
    target: str
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    rollback_available: bool
    rollback_id: Optional[str]


class ChangeTracker:
    """Tracks all system changes for undo capabilities"""
    
    def __init__(self, history_file: str = "./logs/change_history.json"):
        """
        Initialize change tracker
        
        Args:
            history_file: Path to change history file
        """
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.changes = self._load_history()
    
    def _load_history(self) -> List[SystemChange]:
        """Load change history from disk"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                return [SystemChange(**item) for item in data]
        except Exception as e:
            logger.error(f"Failed to load change history: {e}")
            return []
    
    def _save_history(self):
        """Save change history to disk"""
        try:
            data = [asdict(change) for change in self.changes]
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save change history: {e}")
    
    def record_change(self, change_type: str, target: str,
                     before_state: Optional[Dict[str, Any]] = None,
                     after_state: Optional[Dict[str, Any]] = None,
                     rollback_id: Optional[str] = None) -> SystemChange:
        """
        Record a system change
        
        Args:
            change_type: Type of change
            target: Target of the change
            before_state: State before change
            after_state: State after change
            rollback_id: ID for rollback (e.g., backup ID)
            
        Returns:
            SystemChange object
        """
        change_id = f"change_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        change = SystemChange(
            change_id=change_id,
            timestamp=datetime.now().isoformat(),
            change_type=change_type,
            target=target,
            before_state=before_state,
            after_state=after_state,
            rollback_available=rollback_id is not None,
            rollback_id=rollback_id
        )
        
        self.changes.append(change)
        self._save_history()
        
        logger.info(f"Recorded change: {change_type} on {target}")
        return change
    
    def get_recent_changes(self, limit: int = 10) -> List[SystemChange]:
        """Get recent changes"""
        return self.changes[-limit:]
    
    def get_changes_by_type(self, change_type: str) -> List[SystemChange]:
        """Get all changes of a specific type"""
        return [c for c in self.changes if c.change_type == change_type]
    
    def get_rollbackable_changes(self) -> List[SystemChange]:
        """Get changes that can be rolled back"""
        return [c for c in self.changes if c.rollback_available]
    
    def format_change_summary(self, change: SystemChange) -> str:
        """Format a change for display"""
        return (
            f"[{change.timestamp}] {change.change_type}: {change.target}\n"
            f"  Rollback: {'Available' if change.rollback_available else 'Not Available'}"
        )
