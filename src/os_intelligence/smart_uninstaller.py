"""
Smart Uninstaller - Comprehensive application removal system
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from .app_analyzer import AppAnalyzer
from .leftover_detector import LeftoverDetector
from .service_inspector import ServiceInspector

logger = logging.getLogger(__name__)


@dataclass
class UninstallPlan:
    """Complete plan for uninstalling an application"""
    app_name: str
    app_found: bool
    app_details: Optional[Dict[str, Any]]
    
    # Services to stop
    related_services: List[Dict[str, Any]]
    service_stop_commands: List[str]
    
    # Official uninstall
    uninstall_command: Optional[str]
    
    # Leftovers to clean
    leftover_items: List[Dict[str, Any]]
    cleanup_commands: List[str]
    total_cleanup_size: str
    
    # Execution steps
    execution_steps: List[str]
    warnings: List[str]
    requires_admin: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class SmartUninstaller:
    """
    Intelligent application uninstaller that:
    1. Finds the app in registry
    2. Stops related services
    3. Runs official uninstaller
    4. Cleans up leftovers
    5. Provides rollback information
    """
    
    def __init__(self):
        """Initialize smart uninstaller"""
        self.app_analyzer = AppAnalyzer()
        self.leftover_detector = LeftoverDetector()
        self.service_inspector = ServiceInspector()
    
    async def create_uninstall_plan(self, app_name: str) -> UninstallPlan:
        """
        Create a comprehensive uninstall plan
        
        Args:
            app_name: Application name
            
        Returns:
            UninstallPlan object
        """
        logger.info(f"Creating uninstall plan for '{app_name}'")
        
        # Step 1: Find the app
        app_details = await self.app_analyzer.get_app_details(app_name)
        app_found = app_details is not None
        
        # Step 2: Find related services
        related_services = []
        service_stop_commands = []
        if app_found:
            services = await self.service_inspector.find_app_services(app_name)
            related_services = [
                {
                    "name": svc.name,
                    "display_name": svc.display_name,
                    "status": svc.status
                }
                for svc in services
            ]
            service_stop_commands = await self.service_inspector.get_stop_commands(services)
        
        # Step 3: Get official uninstall command
        uninstall_command = None
        if app_found and app_details['app'].get('uninstall_command'):
            uninstall_command = app_details['app']['uninstall_command']
        
        # Step 4: Find leftovers
        leftovers = await self.leftover_detector.find_leftovers(app_name)
        leftover_items = [
            {
                "path": item.path,
                "type": item.item_type,
                "size": self.leftover_detector.format_size(item.size_bytes),
                "location": item.location
            }
            for item in leftovers
        ]
        cleanup_commands = await self.leftover_detector.get_cleanup_commands(leftovers)
        
        # Calculate total cleanup size
        total_size = sum(item.size_bytes for item in leftovers)
        total_cleanup_size = self.leftover_detector.format_size(total_size)
        
        # Step 5: Create execution steps
        execution_steps = self._create_execution_steps(
            service_stop_commands,
            uninstall_command,
            cleanup_commands
        )
        
        # Step 6: Identify warnings
        warnings = self._identify_warnings(
            app_found,
            related_services,
            leftovers
        )
        
        # Step 7: Determine if admin required
        requires_admin = len(service_stop_commands) > 0 or uninstall_command is not None
        
        plan = UninstallPlan(
            app_name=app_name,
            app_found=app_found,
            app_details=app_details,
            related_services=related_services,
            service_stop_commands=service_stop_commands,
            uninstall_command=uninstall_command,
            leftover_items=leftover_items,
            cleanup_commands=cleanup_commands,
            total_cleanup_size=total_cleanup_size,
            execution_steps=execution_steps,
            warnings=warnings,
            requires_admin=requires_admin
        )
        
        logger.info(f"Uninstall plan created: {len(execution_steps)} steps, {len(warnings)} warnings")
        return plan
    
    def _create_execution_steps(self, service_commands: List[str],
                                uninstall_cmd: Optional[str],
                                cleanup_commands: List[str]) -> List[str]:
        """
        Create ordered execution steps
        
        Args:
            service_commands: Commands to stop services
            uninstall_cmd: Official uninstall command
            cleanup_commands: Leftover cleanup commands
            
        Returns:
            List of execution steps
        """
        steps = []
        step_num = 1
        
        # Stop services first
        if service_commands:
            steps.append(f"Step {step_num}: Stop related services")
            for cmd in service_commands:
                steps.append(f"  → {cmd}")
            step_num += 1
        
        # Run official uninstaller
        if uninstall_cmd:
            steps.append(f"Step {step_num}: Run official uninstaller")
            steps.append(f"  → {uninstall_cmd}")
            step_num += 1
        
        # Clean up leftovers
        if cleanup_commands:
            steps.append(f"Step {step_num}: Clean up leftovers ({len(cleanup_commands)} items)")
            # Only show first 3 commands to avoid clutter
            for cmd in cleanup_commands[:3]:
                steps.append(f"  → {cmd}")
            if len(cleanup_commands) > 3:
                steps.append(f"  → ... and {len(cleanup_commands) - 3} more items")
        
        return steps
    
    def _identify_warnings(self, app_found: bool, services: List[Dict],
                          leftovers: List) -> List[str]:
        """
        Identify potential issues and warnings
        
        Args:
            app_found: Whether app was found in registry
            services: Related services
            leftovers: Leftover items
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        if not app_found:
            warnings.append("Application not found in registry - may already be uninstalled")
        
        if services:
            running = [s for s in services if s['status'].lower() == 'running']
            if running:
                warnings.append(f"{len(running)} related service(s) currently running")
        
        if len(leftovers) > 20:
            warnings.append(f"Large number of leftovers found ({len(leftovers)} items) - review carefully")
        
        return warnings
    
    def format_plan_summary(self, plan: UninstallPlan) -> str:
        """
        Format uninstall plan for user display
        
        Args:
            plan: UninstallPlan object
            
        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"🗑️  Uninstall Plan for: {plan.app_name}")
        lines.append("")
        
        if not plan.app_found:
            lines.append("❌ Application not found in system")
            if plan.leftover_items:
                lines.append(f"ℹ️  Found {len(plan.leftover_items)} potential leftovers")
        else:
            lines.append("✅ Application found")
            if plan.app_details:
                app = plan.app_details['app']
                lines.append(f"   Version: {app.get('version', 'Unknown')}")
                lines.append(f"   Publisher: {app.get('publisher', 'Unknown')}")
        
        lines.append("")
        lines.append("📋 Execution Plan:")
        for step in plan.execution_steps:
            lines.append(f"  {step}")
        
        if plan.warnings:
            lines.append("")
            lines.append("⚠️  Warnings:")
            for warning in plan.warnings:
                lines.append(f"  • {warning}")
        
        lines.append("")
        lines.append(f"💾 Total cleanup size: {plan.total_cleanup_size}")
        lines.append(f"🔐 Requires admin: {'Yes' if plan.requires_admin else 'No'}")
        
        return "\n".join(lines)
