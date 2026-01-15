"""
Backup Manager - Creates backups before destructive operations
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class BackupInfo:
    """Information about a backup"""
    backup_id: str
    timestamp: str
    operation: str
    items_backed_up: List[str]
    backup_location: str
    can_restore: bool
    size_bytes: int


class BackupManager:
    """Manages backups before destructive operations"""
    
    def __init__(self, backup_root: str = "./backups"):
        """
        Initialize backup manager
        
        Args:
            backup_root: Root directory for backups
        """
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.backup_index_file = self.backup_root / "backup_index.json"
        self.backups = self._load_backup_index()
    
    def _load_backup_index(self) -> Dict[str, BackupInfo]:
        """Load backup index from disk"""
        if not self.backup_index_file.exists():
            return {}
        
        try:
            with open(self.backup_index_file, 'r') as f:
                data = json.load(f)
                return {
                    k: BackupInfo(**v) for k, v in data.items()
                }
        except Exception as e:
            logger.error(f"Failed to load backup index: {e}")
            return {}
    
    def _save_backup_index(self):
        """Save backup index to disk"""
        try:
            data = {k: asdict(v) for k, v in self.backups.items()}
            with open(self.backup_index_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save backup index: {e}")
    
    async def create_backup(self, items: List[str], operation: str) -> Optional[BackupInfo]:
        """
        Create backup of files/folders before operation
        
        Args:
            items: List of file/folder paths to backup
            operation: Description of the operation
            
        Returns:
            BackupInfo object or None if failed
        """
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = self.backup_root / backup_id
        
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backed_up_items = []
            total_size = 0
            
            for item_path in items:
                if not os.path.exists(item_path):
                    logger.warning(f"Item not found, skipping: {item_path}")
                    continue
                
                try:
                    # Create relative path structure
                    item_name = Path(item_path).name
                    backup_path = backup_dir / item_name
                    
                    if os.path.isfile(item_path):
                        shutil.copy2(item_path, backup_path)
                        total_size += os.path.getsize(item_path)
                    elif os.path.isdir(item_path):
                        shutil.copytree(item_path, backup_path)
                        total_size += self._get_dir_size(item_path)
                    
                    backed_up_items.append(item_path)
                    logger.info(f"Backed up: {item_path}")
                
                except Exception as e:
                    logger.error(f"Failed to backup {item_path}: {e}")
            
            if not backed_up_items:
                logger.warning("No items were backed up")
                shutil.rmtree(backup_dir)
                return None
            
            # Create backup metadata
            metadata = {
                "original_paths": backed_up_items,
                "operation": operation,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(backup_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=datetime.now().isoformat(),
                operation=operation,
                items_backed_up=backed_up_items,
                backup_location=str(backup_dir),
                can_restore=True,
                size_bytes=total_size
            )
            
            self.backups[backup_id] = backup_info
            self._save_backup_index()
            
            logger.info(f"Backup created: {backup_id} ({len(backed_up_items)} items)")
            return backup_info
        
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            return None
    
    async def restore_backup(self, backup_id: str) -> bool:
        """
        Restore files from a backup
        
        Args:
            backup_id: Backup ID to restore
            
        Returns:
            True if successful
        """
        if backup_id not in self.backups:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        backup_info = self.backups[backup_id]
        backup_dir = Path(backup_info.backup_location)
        
        if not backup_dir.exists():
            logger.error(f"Backup directory not found: {backup_dir}")
            return False
        
        try:
            # Load metadata
            with open(backup_dir / "metadata.json", 'r') as f:
                metadata = json.load(f)
            
            original_paths = metadata['original_paths']
            
            # Restore each item
            for original_path in original_paths:
                item_name = Path(original_path).name
                backup_path = backup_dir / item_name
                
                if not backup_path.exists():
                    logger.warning(f"Backup item not found: {backup_path}")
                    continue
                
                try:
                    # Remove existing item if present
                    if os.path.exists(original_path):
                        if os.path.isfile(original_path):
                            os.remove(original_path)
                        elif os.path.isdir(original_path):
                            shutil.rmtree(original_path)
                    
                    # Restore from backup
                    if backup_path.is_file():
                        shutil.copy2(backup_path, original_path)
                    elif backup_path.is_dir():
                        shutil.copytree(backup_path, original_path)
                    
                    logger.info(f"Restored: {original_path}")
                
                except Exception as e:
                    logger.error(f"Failed to restore {original_path}: {e}")
            
            logger.info(f"Backup restored: {backup_id}")
            return True
        
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        """Get list of all backups"""
        return list(self.backups.values())
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup
        
        Args:
            backup_id: Backup ID to delete
            
        Returns:
            True if successful
        """
        if backup_id not in self.backups:
            return False
        
        backup_info = self.backups[backup_id]
        backup_dir = Path(backup_info.backup_location)
        
        try:
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            
            del self.backups[backup_id]
            self._save_backup_index()
            
            logger.info(f"Backup deleted: {backup_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False
    
    def _get_dir_size(self, directory: str) -> int:
        """Calculate total size of directory"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        except Exception as e:
            logger.error(f"Error calculating directory size: {e}")
        return total
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
