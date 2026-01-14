"""
App Analyzer - Analyze installed applications comprehensively
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from .registry_scanner import RegistryScanner, RegistryApp

logger = logging.getLogger(__name__)


@dataclass
class AppInfo:
    """Comprehensive application information"""
    name: str
    version: Optional[str]
    publisher: Optional[str]
    install_location: Optional[str]
    uninstall_command: Optional[str]
    source: str  # 'registry', 'winget', 'microsoft_store'
    registry_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class AppAnalyzer:
    """Analyzes installed applications on Windows"""
    
    def __init__(self):
        """Initialize app analyzer"""
        self.registry_scanner = RegistryScanner()
        self.cached_apps = []
    
    async def analyze_installed_apps(self) -> List[AppInfo]:
        """
        Analyze all installed applications
        
        Returns:
            List of AppInfo objects
        """
        apps = []
        
        # Scan from registry
        registry_apps = await self.registry_scanner.scan_installed_apps()
        for reg_app in registry_apps:
            apps.append(self._convert_registry_app(reg_app))
        
        self.cached_apps = apps
        logger.info(f"Analyzed {len(apps)} applications")
        return apps
    
    def _convert_registry_app(self, reg_app: RegistryApp) -> AppInfo:
        """
        Convert RegistryApp to AppInfo
        
        Args:
            reg_app: RegistryApp object
            
        Returns:
            AppInfo object
        """
        return AppInfo(
            name=reg_app.name,
            version=reg_app.display_version,
            publisher=reg_app.publisher,
            install_location=reg_app.install_location,
            uninstall_command=reg_app.uninstall_string or reg_app.quiet_uninstall_string,
            source='registry',
            registry_key=reg_app.registry_key
        )
    
    async def find_app(self, app_name: str) -> List[AppInfo]:
        """
        Find applications by name
        
        Args:
            app_name: Application name to search
            
        Returns:
            List of matching applications
        """
        if not self.cached_apps:
            await self.analyze_installed_apps()
        
        app_name_lower = app_name.lower()
        matches = [
            app for app in self.cached_apps
            if app_name_lower in app.name.lower()
        ]
        
        logger.info(f"Found {len(matches)} matches for '{app_name}'")
        return matches
    
    async def get_app_details(self, app_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an application
        
        Args:
            app_name: Application name
            
        Returns:
            Dictionary with app details
        """
        matches = await self.find_app(app_name)
        
        if not matches:
            return None
        
        # Return the best match (first one)
        app = matches[0]
        
        return {
            "app": app.to_dict(),
            "total_matches": len(matches),
            "all_matches": [m.to_dict() for m in matches]
        }
    
    async def check_app_installed(self, app_name: str) -> bool:
        """
        Check if an application is installed
        
        Args:
            app_name: Application name
            
        Returns:
            True if installed
        """
        matches = await self.find_app(app_name)
        return len(matches) > 0
    
    async def get_startup_apps(self) -> List[Dict[str, Any]]:
        """
        Get applications that run on startup
        
        Returns:
            List of startup applications
        """
        # This will be implemented in a future update
        # For now, return empty list
        logger.info("Startup app detection not yet implemented")
        return []
