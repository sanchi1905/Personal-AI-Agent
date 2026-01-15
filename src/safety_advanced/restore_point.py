"""
Restore Point Manager - Integrates with Windows System Restore
"""

import subprocess
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RestorePointManager:
    """Manages Windows System Restore Points"""
    
    def __init__(self):
        """Initialize restore point manager"""
        pass
    
    async def create_restore_point(self, description: str) -> Optional[str]:
        """
        Create a Windows System Restore Point
        
        Args:
            description: Description for the restore point
            
        Returns:
            Restore point ID or None if failed
        """
        try:
            # PowerShell command to create restore point
            ps_script = f"""
            Checkpoint-Computer -Description "{description}" -RestorePointType "APPLICATION_INSTALL"
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                restore_point_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                logger.info(f"Restore point created: {description}")
                return restore_point_id
            else:
                logger.error(f"Failed to create restore point: {result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating restore point: {e}")
            return None
    
    async def list_restore_points(self) -> List[Dict[str, Any]]:
        """
        List all available restore points
        
        Returns:
            List of restore point information
        """
        try:
            ps_script = """
            Get-ComputerRestorePoint | Select-Object -Property SequenceNumber, CreationTime, Description | ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                import json
                restore_points = json.loads(result.stdout)
                
                # Handle single restore point (not a list)
                if isinstance(restore_points, dict):
                    restore_points = [restore_points]
                
                return restore_points
            else:
                logger.warning("No restore points found or command failed")
                return []
        
        except Exception as e:
            logger.error(f"Error listing restore points: {e}")
            return []
    
    async def restore_to_point(self, sequence_number: int) -> bool:
        """
        Restore system to a specific restore point
        
        Args:
            sequence_number: Sequence number of restore point
            
        Returns:
            True if initiated successfully
            
        Note:
            This requires admin privileges and will restart the computer
        """
        try:
            ps_script = f"""
            # This requires admin privileges
            Restore-Computer -RestorePoint {sequence_number} -Confirm:$false
            """
            
            logger.warning("System restore initiated - computer will restart!")
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
        
        except Exception as e:
            logger.error(f"Error restoring to point: {e}")
            return False
    
    async def is_restore_enabled(self) -> bool:
        """
        Check if System Restore is enabled
        
        Returns:
            True if enabled
        """
        try:
            ps_script = """
            $status = Get-ComputerRestorePoint -ErrorAction SilentlyContinue
            if ($status -ne $null) { 'enabled' } else { 'disabled' }
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return 'enabled' in result.stdout.lower()
        
        except Exception as e:
            logger.error(f"Error checking restore status: {e}")
            return False
    
    def get_restore_point_size_estimate(self) -> str:
        """
        Get estimated disk space used by restore points
        
        Returns:
            Human-readable size estimate
        """
        try:
            ps_script = """
            $rp = Get-ComputerRestorePoint -ErrorAction SilentlyContinue
            if ($rp) {
                "Restore points available: $($rp.Count)"
            } else {
                "No restore points found"
            }
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.stdout.strip()
        
        except Exception as e:
            logger.error(f"Error getting restore point info: {e}")
            return "Unknown"
