"""
Privilege & Permission Management System

Detects admin privileges, handles graceful degradation,
and provides clear UX messaging for permission-related issues.
"""

import ctypes
import os
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class PrivilegeLevel(Enum):
    """System privilege levels"""
    ADMIN = "admin"
    STANDARD_USER = "user"
    UNKNOWN = "unknown"


class OperationRequirement(Enum):
    """Operation privilege requirements"""
    REQUIRES_ADMIN = "requires_admin"
    PREFERS_ADMIN = "prefers_admin"
    NO_ADMIN_NEEDED = "no_admin_needed"


@dataclass
class PrivilegeCheck:
    """Result of privilege check"""
    has_privilege: bool
    current_level: PrivilegeLevel
    required_level: OperationRequirement
    can_proceed: bool
    degraded_mode: bool
    message: str
    suggestions: List[str]


class PrivilegeManager:
    """
    Manages privilege detection and graceful degradation.
    
    Provides:
    - Admin privilege detection
    - Graceful degradation for restricted operations
    - Clear UX messaging for permission issues
    - Operation compatibility checking
    """
    
    def __init__(self):
        self.current_privilege = self._detect_privilege()
        self.admin_only_operations = {
            'registry_write',
            'service_control',
            'system_restore',
            'driver_management',
            'scheduled_task_create',
            'windows_update',
        }
        self.admin_preferred_operations = {
            'app_uninstall',
            'disk_cleanup',
            'network_config',
            'firewall_config',
        }
    
    def _detect_privilege(self) -> PrivilegeLevel:
        """Detect current privilege level"""
        try:
            # Check if running as administrator on Windows
            if os.name == 'nt':
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                return PrivilegeLevel.ADMIN if is_admin else PrivilegeLevel.STANDARD_USER
            else:
                # Unix-like systems
                is_root = os.geteuid() == 0
                return PrivilegeLevel.ADMIN if is_root else PrivilegeLevel.STANDARD_USER
        except Exception:
            return PrivilegeLevel.UNKNOWN
    
    def is_admin(self) -> bool:
        """Check if running with admin privileges"""
        return self.current_privilege == PrivilegeLevel.ADMIN
    
    def check_operation(self, operation_type: str, operation_name: str = "") -> PrivilegeCheck:
        """
        Check if current privilege level is sufficient for operation.
        
        Args:
            operation_type: Type of operation (e.g., 'registry_write', 'app_uninstall')
            operation_name: Human-readable operation name for messaging
        
        Returns:
            PrivilegeCheck object with detailed permission information
        """
        is_admin = self.is_admin()
        op_name = operation_name or operation_type.replace('_', ' ').title()
        
        # Determine requirement level
        if operation_type in self.admin_only_operations:
            requirement = OperationRequirement.REQUIRES_ADMIN
        elif operation_type in self.admin_preferred_operations:
            requirement = OperationRequirement.PREFERS_ADMIN
        else:
            requirement = OperationRequirement.NO_ADMIN_NEEDED
        
        # Check compatibility
        if requirement == OperationRequirement.REQUIRES_ADMIN:
            if is_admin:
                return PrivilegeCheck(
                    has_privilege=True,
                    current_level=self.current_privilege,
                    required_level=requirement,
                    can_proceed=True,
                    degraded_mode=False,
                    message=f"✅ Admin privileges detected. Ready to execute: {op_name}",
                    suggestions=[]
                )
            else:
                return PrivilegeCheck(
                    has_privilege=False,
                    current_level=self.current_privilege,
                    required_level=requirement,
                    can_proceed=False,
                    degraded_mode=True,
                    message=f"⚠️ {op_name} requires administrator privileges. Running in analysis-only mode.",
                    suggestions=[
                        "Restart the application as Administrator",
                        "Right-click → 'Run as Administrator'",
                        "Use PowerShell: Start-Process -Verb RunAs"
                    ]
                )
        
        elif requirement == OperationRequirement.PREFERS_ADMIN:
            if is_admin:
                return PrivilegeCheck(
                    has_privilege=True,
                    current_level=self.current_privilege,
                    required_level=requirement,
                    can_proceed=True,
                    degraded_mode=False,
                    message=f"✅ Admin privileges detected. Full capabilities enabled for: {op_name}",
                    suggestions=[]
                )
            else:
                return PrivilegeCheck(
                    has_privilege=False,
                    current_level=self.current_privilege,
                    required_level=requirement,
                    can_proceed=True,
                    degraded_mode=True,
                    message=f"⚠️ {op_name} works better with admin privileges. Some features may be limited.",
                    suggestions=[
                        "For full capabilities, restart as Administrator",
                        "Current mode: Limited user permissions",
                        "Some system changes may be restricted"
                    ]
                )
        
        else:  # NO_ADMIN_NEEDED
            return PrivilegeCheck(
                has_privilege=True,
                current_level=self.current_privilege,
                required_level=requirement,
                can_proceed=True,
                degraded_mode=False,
                message=f"✅ Ready to execute: {op_name}",
                suggestions=[]
            )
    
    def get_degraded_alternatives(self, operation_type: str) -> List[str]:
        """
        Get alternative approaches when admin privileges are unavailable.
        
        Args:
            operation_type: Type of operation
        
        Returns:
            List of alternative suggestions
        """
        alternatives = {
            'registry_write': [
                "View registry values (read-only)",
                "Generate registry script for later admin execution",
                "Export current values for comparison"
            ],
            'service_control': [
                "View service status (read-only)",
                "Identify service dependencies",
                "Generate service control script for admin execution"
            ],
            'app_uninstall': [
                "Scan for leftover files and registry entries",
                "Generate uninstall report",
                "Identify uninstall command for manual execution"
            ],
            'system_restore': [
                "View available restore points (read-only)",
                "Check system restore status",
                "Document recommended restore point"
            ],
            'disk_cleanup': [
                "Analyze disk space usage",
                "Identify large files and temp directories",
                "Generate cleanup script for admin execution"
            ],
        }
        
        return alternatives.get(operation_type, [
            "Operation analysis available",
            "Read-only information gathering",
            "Generate script for later admin execution"
        ])
    
    def format_privilege_message(self, check: PrivilegeCheck) -> Dict[str, any]:
        """
        Format privilege check result for UI display.
        
        Args:
            check: PrivilegeCheck result
        
        Returns:
            Formatted message dictionary
        """
        return {
            'status': 'success' if check.can_proceed else 'warning',
            'level': check.current_level.value,
            'required': check.required_level.value,
            'can_proceed': check.can_proceed,
            'degraded': check.degraded_mode,
            'message': check.message,
            'suggestions': check.suggestions,
            'icon': '✅' if check.can_proceed and not check.degraded_mode else '⚠️'
        }
    
    def get_elevation_instructions(self) -> Dict[str, List[str]]:
        """Get platform-specific instructions for privilege elevation"""
        if os.name == 'nt':
            return {
                'windows': [
                    "Method 1: Right-click the application → 'Run as administrator'",
                    "Method 2: Search for app in Start Menu → Right-click → 'Run as administrator'",
                    "Method 3: Use PowerShell: Start-Process -FilePath 'path\\to\\app.exe' -Verb RunAs",
                    "Method 4: Create a shortcut → Properties → Advanced → 'Run as administrator'"
                ]
            }
        else:
            return {
                'linux': [
                    "Method 1: Use sudo: sudo python script.py",
                    "Method 2: Switch to root: su - then run application",
                    "Method 3: Configure sudoers for passwordless execution (advanced)"
                ]
            }


# Global instance
_privilege_manager = None

def get_privilege_manager() -> PrivilegeManager:
    """Get or create global PrivilegeManager instance"""
    global _privilege_manager
    if _privilege_manager is None:
        _privilege_manager = PrivilegeManager()
    return _privilege_manager
