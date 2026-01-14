"""
Service Inspector - Analyze and manage Windows services
"""

import subprocess
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ServiceInfo:
    """Information about a Windows service"""
    name: str
    display_name: str
    status: str  # 'Running', 'Stopped', etc.
    start_type: str  # 'Auto', 'Manual', 'Disabled'
    description: Optional[str] = None


class ServiceInspector:
    """Inspects and manages Windows services"""
    
    def __init__(self):
        """Initialize service inspector"""
        self.cached_services = []
    
    async def list_all_services(self) -> List[ServiceInfo]:
        """
        List all Windows services
        
        Returns:
            List of ServiceInfo objects
        """
        services = []
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-Service | Select-Object Name, DisplayName, Status, StartType | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                import json
                data = json.loads(result.stdout)
                
                # Handle both single service and multiple services
                if isinstance(data, dict):
                    data = [data]
                
                for svc in data:
                    services.append(ServiceInfo(
                        name=svc.get('Name', ''),
                        display_name=svc.get('DisplayName', ''),
                        status=svc.get('Status', ''),
                        start_type=str(svc.get('StartType', ''))
                    ))
        
        except Exception as e:
            logger.error(f"Error listing services: {e}")
        
        self.cached_services = services
        logger.info(f"Found {len(services)} services")
        return services
    
    async def find_service(self, service_name: str) -> List[ServiceInfo]:
        """
        Find services matching a name
        
        Args:
            service_name: Service name to search
            
        Returns:
            List of matching services
        """
        if not self.cached_services:
            await self.list_all_services()
        
        service_name_lower = service_name.lower()
        matches = [
            svc for svc in self.cached_services
            if service_name_lower in svc.name.lower() or 
               service_name_lower in svc.display_name.lower()
        ]
        
        return matches
    
    async def get_service_details(self, service_name: str) -> Optional[ServiceInfo]:
        """
        Get detailed information about a service
        
        Args:
            service_name: Service name
            
        Returns:
            ServiceInfo or None
        """
        try:
            result = subprocess.run(
                ["powershell", "-Command", 
                 f"Get-Service -Name '{service_name}' | Select-Object Name, DisplayName, Status, StartType | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                import json
                data = json.loads(result.stdout)
                
                return ServiceInfo(
                    name=data.get('Name', ''),
                    display_name=data.get('DisplayName', ''),
                    status=data.get('Status', ''),
                    start_type=str(data.get('StartType', ''))
                )
        
        except Exception as e:
            logger.error(f"Error getting service details: {e}")
        
        return None
    
    async def find_app_services(self, app_name: str) -> List[ServiceInfo]:
        """
        Find services related to an application
        
        Args:
            app_name: Application name
            
        Returns:
            List of related services
        """
        if not self.cached_services:
            await self.list_all_services()
        
        app_name_clean = app_name.lower().replace(' ', '')
        
        matches = [
            svc for svc in self.cached_services
            if app_name_clean in svc.name.lower().replace(' ', '') or
               app_name_clean in svc.display_name.lower().replace(' ', '')
        ]
        
        logger.info(f"Found {len(matches)} services for '{app_name}'")
        return matches
    
    async def get_stop_commands(self, services: List[ServiceInfo]) -> List[str]:
        """
        Generate commands to stop services
        
        Args:
            services: List of services to stop
            
        Returns:
            List of PowerShell commands
        """
        commands = []
        
        for svc in services:
            if svc.status.lower() == 'running':
                commands.append(f"Stop-Service -Name '{svc.name}' -Force")
        
        return commands
    
    async def is_service_blocking(self, service_name: str) -> bool:
        """
        Check if a service might be blocking file operations
        
        Args:
            service_name: Service name
            
        Returns:
            True if service is running
        """
        svc = await self.get_service_details(service_name)
        return svc is not None and svc.status.lower() == 'running'
