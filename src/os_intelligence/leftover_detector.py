"""
Leftover Detector - Find application leftovers after uninstall
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LeftoverItem:
    """Represents a leftover file or folder"""
    path: str
    item_type: str  # 'file' or 'folder'
    size_bytes: int
    location: str  # 'AppData', 'ProgramData', 'Temp', etc.


class LeftoverDetector:
    """Detects application leftovers in common locations"""
    
    # Common locations where apps leave files
    COMMON_LOCATIONS = {
        'AppData_Roaming': os.path.expandvars(r'%APPDATA%'),
        'AppData_Local': os.path.expandvars(r'%LOCALAPPDATA%'),
        'ProgramData': os.path.expandvars(r'%PROGRAMDATA%'),
        'Temp': os.path.expandvars(r'%TEMP%'),
        'LocalTemp': os.path.expandvars(r'%LOCALAPPDATA%\Temp'),
    }
    
    def __init__(self):
        """Initialize leftover detector"""
        pass
    
    async def find_leftovers(self, app_name: str) -> List[LeftoverItem]:
        """
        Find leftover files and folders for an application
        
        Args:
            app_name: Application name to search for
            
        Returns:
            List of LeftoverItem objects
        """
        leftovers = []
        
        for location_name, location_path in self.COMMON_LOCATIONS.items():
            try:
                items = await self._scan_location(location_path, app_name, location_name)
                leftovers.extend(items)
            except Exception as e:
                logger.warning(f"Could not scan {location_name}: {e}")
        
        logger.info(f"Found {len(leftovers)} potential leftovers for '{app_name}'")
        return leftovers
    
    async def _scan_location(self, location_path: str, app_name: str, 
                            location_name: str) -> List[LeftoverItem]:
        """
        Scan a specific location for app-related items
        
        Args:
            location_path: Path to scan
            app_name: Application name
            location_name: Name of the location
            
        Returns:
            List of leftover items
        """
        leftovers = []
        
        if not os.path.exists(location_path):
            return leftovers
        
        try:
            # Search for folders/files matching app name
            app_name_clean = app_name.lower().replace(' ', '')
            
            for item in os.listdir(location_path):
                item_lower = item.lower().replace(' ', '')
                
                # Check if item name contains app name
                if app_name_clean in item_lower or item_lower in app_name_clean:
                    item_path = os.path.join(location_path, item)
                    
                    try:
                        if os.path.isdir(item_path):
                            size = self._get_folder_size(item_path)
                            leftovers.append(LeftoverItem(
                                path=item_path,
                                item_type='folder',
                                size_bytes=size,
                                location=location_name
                            ))
                        elif os.path.isfile(item_path):
                            size = os.path.getsize(item_path)
                            leftovers.append(LeftoverItem(
                                path=item_path,
                                item_type='file',
                                size_bytes=size,
                                location=location_name
                            ))
                    except Exception as e:
                        logger.debug(f"Could not analyze {item_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error scanning {location_path}: {e}")
        
        return leftovers
    
    def _get_folder_size(self, folder_path: str) -> int:
        """
        Calculate total size of a folder
        
        Args:
            folder_path: Path to folder
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        pass
        except:
            pass
        
        return total_size
    
    def format_size(self, size_bytes: int) -> str:
        """
        Format size in human-readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    async def get_cleanup_commands(self, leftovers: List[LeftoverItem]) -> List[str]:
        """
        Generate PowerShell commands to remove leftovers
        
        Args:
            leftovers: List of leftover items
            
        Returns:
            List of PowerShell commands
        """
        commands = []
        
        for item in leftovers:
            if item.item_type == 'folder':
                commands.append(f'Remove-Item -Path "{item.path}" -Recurse -Force')
            else:
                commands.append(f'Remove-Item -Path "{item.path}" -Force')
        
        return commands
