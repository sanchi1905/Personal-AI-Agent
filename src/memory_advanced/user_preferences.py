"""
User Preferences - Stores and manages user settings and preferences
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Preference:
    """Individual preference setting"""
    key: str
    value: Any
    category: str
    last_updated: str


class UserPreferences:
    """Manages user preferences and settings"""
    
    def __init__(self, preferences_file: str = "./config/user_preferences.json"):
        """
        Initialize user preferences
        
        Args:
            preferences_file: Path to preferences file
        """
        self.preferences_file = Path(preferences_file)
        self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
        self.preferences: Dict[str, Preference] = self._load_preferences()
        
        # Default preferences
        self._init_defaults()
    
    def _init_defaults(self):
        """Initialize default preferences if not set"""
        defaults = {
            'auto_backup': Preference('auto_backup', True, 'safety', datetime.now().isoformat()),
            'dry_run_mode': Preference('dry_run_mode', False, 'safety', datetime.now().isoformat()),
            'confirmation_required': Preference('confirmation_required', True, 'safety', datetime.now().isoformat()),
            'verbose_explanations': Preference('verbose_explanations', True, 'ui', datetime.now().isoformat()),
            'color_output': Preference('color_output', True, 'ui', datetime.now().isoformat()),
            'save_command_history': Preference('save_command_history', True, 'memory', datetime.now().isoformat()),
            'learn_patterns': Preference('learn_patterns', True, 'memory', datetime.now().isoformat()),
            'smart_suggestions': Preference('smart_suggestions', True, 'memory', datetime.now().isoformat()),
            'max_history_size': Preference('max_history_size', 1000, 'memory', datetime.now().isoformat()),
        }
        
        for key, pref in defaults.items():
            if key not in self.preferences:
                self.preferences[key] = pref
        
        self._save_preferences()
    
    def _load_preferences(self) -> Dict[str, Preference]:
        """Load preferences from disk"""
        if not self.preferences_file.exists():
            return {}
        
        try:
            with open(self.preferences_file, 'r') as f:
                data = json.load(f)
                return {
                    k: Preference(**v) for k, v in data.items()
                }
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
            return {}
    
    def _save_preferences(self):
        """Save preferences to disk"""
        try:
            data = {k: asdict(v) for k, v in self.preferences.items()}
            with open(self.preferences_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get preference value
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value
        """
        if key in self.preferences:
            return self.preferences[key].value
        return default
    
    def set(self, key: str, value: Any, category: str = 'user'):
        """
        Set preference value
        
        Args:
            key: Preference key
            value: Preference value
            category: Preference category
        """
        self.preferences[key] = Preference(
            key=key,
            value=value,
            category=category,
            last_updated=datetime.now().isoformat()
        )
        self._save_preferences()
        logger.info(f"Preference updated: {key} = {value}")
    
    def get_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get all preferences in a category
        
        Args:
            category: Category name
            
        Returns:
            Dictionary of preferences
        """
        return {
            k: v.value for k, v in self.preferences.items()
            if v.category == category
        }
    
    def delete(self, key: str) -> bool:
        """
        Delete a preference
        
        Args:
            key: Preference key
            
        Returns:
            True if deleted
        """
        if key in self.preferences:
            del self.preferences[key]
            self._save_preferences()
            logger.info(f"Preference deleted: {key}")
            return True
        return False
    
    def export_preferences(self) -> Dict[str, Any]:
        """Export all preferences as dictionary"""
        return {k: v.value for k, v in self.preferences.items()}
    
    def import_preferences(self, prefs: Dict[str, Any], category: str = 'imported'):
        """
        Import preferences from dictionary
        
        Args:
            prefs: Dictionary of preferences
            category: Category for imported preferences
        """
        for key, value in prefs.items():
            self.set(key, value, category)
        logger.info(f"Imported {len(prefs)} preferences")
    
    def reset_to_defaults(self):
        """Reset all preferences to defaults"""
        self.preferences.clear()
        self._init_defaults()
        logger.info("Preferences reset to defaults")
    
    def get_categories(self) -> List[str]:
        """Get list of all preference categories"""
        return list(set(p.category for p in self.preferences.values()))
