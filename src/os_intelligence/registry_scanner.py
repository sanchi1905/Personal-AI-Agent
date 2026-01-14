"""
Registry Scanner - Read Windows registry for application information
"""

import subprocess
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RegistryApp:
    """Represents an application found in registry"""
    name: str
    display_version: Optional[str]
    publisher: Optional[str]
    install_location: Optional[str]
    uninstall_string: Optional[str]
    quiet_uninstall_string: Optional[str]
    registry_key: str


class RegistryScanner:
    """Scans Windows registry for installed applications"""
    
    # Common registry paths for installed apps
    UNINSTALL_KEYS = [
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    def __init__(self):
        """Initialize registry scanner"""
        self.cached_apps = []
    
    async def scan_installed_apps(self) -> List[RegistryApp]:
        """
        Scan registry for all installed applications
        
        Returns:
            List of RegistryApp objects
        """
        apps = []
        
        # Scan each registry path separately for better error handling
        registry_paths = [
            r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
            r"HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
            r"HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
        ]
        
        for reg_path in registry_paths:
            try:
                # Simpler approach: get CSV output instead of JSON
                ps_command = f"Get-ItemProperty '{reg_path}' -ErrorAction SilentlyContinue | Where-Object {{ $_.DisplayName }} | Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation, UninstallString, QuietUninstallString | ConvertTo-Csv -NoTypeInformation"
                
                result = subprocess.run(
                    ["powershell", "-Command", ps_command],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    # Parse CSV output
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        for line in lines[1:]:
                            try:
                                # Simple CSV parsing
                                parts = line.strip('"').split('","')
                                if len(parts) >= 1 and parts[0]:
                                    name = parts[0]
                                    # Filter out system components
                                    if name and len(name) > 2 and 'KB' not in name and 'Hotfix' not in name:
                                        apps.append(RegistryApp(
                                            name=name,
                                            display_version=parts[1] if len(parts) > 1 else None,
                                            publisher=parts[2] if len(parts) > 2 else None,
                                            install_location=parts[3] if len(parts) > 3 else None,
                                            uninstall_string=parts[4] if len(parts) > 4 else None,
                                            quiet_uninstall_string=parts[5] if len(parts) > 5 else None,
                                            registry_key=reg_path
                                        ))
                            except:
                                continue
            
            except Exception as e:
                logger.warning(f"Could not scan {reg_path}: {e}")
        
        self.cached_apps = apps
        logger.info(f"Found {len(apps)} applications in registry")
        return apps
    
    async def _scan_registry_key(self, key_path: str) -> List[RegistryApp]:
        """
        Scan a specific registry key for applications
        
        Args:
            key_path: Registry key path
            
        Returns:
            List of applications found
        """
        apps = []
        
        try:
            # List all subkeys - using /s flag is too slow, so we query the key first
            result = subprocess.run(
                ["powershell", "-Command", f"Get-ChildItem -Path 'Registry::{key_path}' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name"],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                return apps
            
            # Parse subkeys - PowerShell returns full paths
            lines = result.stdout.strip().split('\n')
            subkeys = [line.strip() for line in lines if line.strip()]
            
            # Query each subkey for app details (limit to first 50 to avoid slowness)
            for subkey in subkeys[:50]:
                # Convert PowerShell registry path to reg.exe format
                reg_path = subkey.replace('HKEY_LOCAL_MACHINE\\', 'HKLM\\').replace('HKEY_CURRENT_USER\\', 'HKCU\\')
                app = await self._get_app_info(reg_path)
                if app and app.name and app.name.strip():
                    apps.append(app)
        
        except Exception as e:
            logger.error(f"Error scanning registry key {key_path}: {e}")
        
        return apps
    
    async def _get_app_info(self, subkey: str) -> Optional[RegistryApp]:
        """
        Get application information from a registry subkey
        
        Args:
            subkey: Registry subkey path
            
        Returns:
            RegistryApp or None
        """
        try:
            # Use PowerShell to query registry values
            ps_path = subkey.replace('HKLM\\', 'HKLM:').replace('HKCU\\', 'HKCU:')
            
            result = subprocess.run(
                ["powershell", "-Command", 
                 f"Get-ItemProperty -Path 'Registry::{ps_path}' -ErrorAction SilentlyContinue | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                return None
            
            # Parse JSON output
            import json
            try:
                values = json.loads(result.stdout)
            except:
                return None
            
            # Create RegistryApp if DisplayName exists
            if 'DisplayName' not in values or not values['DisplayName']:
                return None
            
            # Skip system components and updates
            display_name = values.get('DisplayName', '')
            if 'KB' in display_name or 'Hotfix' in display_name or len(display_name) < 3:
                return None
            
            return RegistryApp(
                name=display_name,
                display_version=values.get('DisplayVersion'),
                publisher=values.get('Publisher'),
                install_location=values.get('InstallLocation'),
                uninstall_string=values.get('UninstallString'),
                quiet_uninstall_string=values.get('QuietUninstallString'),
                registry_key=subkey
            )
        
        except Exception as e:
            logger.debug(f"Could not parse app info from {subkey}: {e}")
            return None
    
    async def find_app(self, app_name: str) -> List[RegistryApp]:
        """
        Find applications matching a name
        
        Args:
            app_name: Application name to search for
            
        Returns:
            List of matching applications
        """
        if not self.cached_apps:
            await self.scan_installed_apps()
        
        app_name_lower = app_name.lower()
        matches = [
            app for app in self.cached_apps
            if app_name_lower in app.name.lower()
        ]
        
        return matches
    
    async def get_uninstall_command(self, app: RegistryApp) -> Optional[str]:
        """
        Get the best uninstall command for an application
        
        Args:
            app: RegistryApp object
            
        Returns:
            Uninstall command string or None
        """
        # Prefer quiet uninstall if available
        if app.quiet_uninstall_string:
            return app.quiet_uninstall_string
        
        if app.uninstall_string:
            return app.uninstall_string
        
        return None
