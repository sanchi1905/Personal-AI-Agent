"""
CLI with Phase 3 Safety Features - Rollback, Backups, Dry-run
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.llm.client import LLMClient
from src.executor.command_executor import CommandExecutor
from src.executor.validators import CommandValidator
from src.safety.confirmation import ConfirmationHandler
from src.safety.audit import AuditLogger
from src.os_intelligence.smart_uninstaller import SmartUninstaller
from src.os_intelligence.app_analyzer import AppAnalyzer
from src.os_intelligence.service_inspector import ServiceInspector

# Phase 3: Advanced Safety
from src.safety_advanced.backup_manager import BackupManager
from src.safety_advanced.rollback_engine import RollbackEngine
from src.safety_advanced.change_tracker import ChangeTracker
from src.safety_advanced.restore_point import RestorePointManager
from src.safety_advanced.dry_run import DryRunSimulator
from src.safety_advanced.sandbox import CommandSandbox

from colorama import init, Fore, Style

# Initialize colorama for Windows
init()


class Phase3CLIAgent:
    """CLI with advanced safety features - Phase 3"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.executor = CommandExecutor(log_path="./logs/commands.log")
        self.confirmation_handler = ConfirmationHandler()
        self.audit_logger = AuditLogger()
        
        # OS Intelligence components (Phase 2)
        self.smart_uninstaller = SmartUninstaller()
        self.app_analyzer = AppAnalyzer()
        self.service_inspector = ServiceInspector()
        
        # Advanced Safety components (Phase 3)
        self.backup_manager = BackupManager()
        self.rollback_engine = RollbackEngine()
        self.change_tracker = ChangeTracker()
        self.restore_point_manager = RestorePointManager()
        self.dry_run_simulator = DryRunSimulator()
        self.sandbox = CommandSandbox()
        
        # Mode flags
        self.dry_run_mode = False
        self.auto_backup = True
        
    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}   Personal AI Agent - Phase 3: Enhanced Safety & Rollback")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Features:{Style.RESET_ALL}")
        print("  ✓ Explain → Confirm → Execute workflow")
        print("  ✓ Safe command execution with validation")
        print("  ✓ Complete audit trail")
        print(f"  ✓ Smart app uninstaller")
        print(f"  ✓ Leftover detection & cleanup")
        print(f"  ✓ Service management")
        print(f"  {Fore.GREEN}✓ Automatic backups before operations{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}✓ Rollback scripts for all changes{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}✓ Dry-run mode (test without executing){Style.RESET_ALL}")
        print(f"  {Fore.GREEN}✓ Change tracking & undo{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}✓ Windows Restore Point integration{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Special Commands:{Style.RESET_ALL}")
        print("  • 'list apps' - Show installed applications")
        print("  • 'uninstall <app>' - Smart uninstall application")
        print("  • 'services' - List Windows services")
        print(f"  {Fore.GREEN}• 'dry run on/off' - Toggle dry-run mode{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• 'backups' - List all backups{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• 'restore <backup_id>' - Restore from backup{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• 'changes' - Show recent changes{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}• 'create restore point' - Create Windows restore point{Style.RESET_ALL}")
        print("  • 'help' - Show all commands")
        print("  • 'exit' - Quit\n")
        
        mode_status = f"{Fore.YELLOW}DRY-RUN{Style.RESET_ALL}" if self.dry_run_mode else f"{Fore.GREEN}LIVE{Style.RESET_ALL}"
        backup_status = f"{Fore.GREEN}ON{Style.RESET_ALL}" if self.auto_backup else f"{Fore.RED}OFF{Style.RESET_ALL}"
        
        print(f"Mode: {mode_status} | Auto-backup: {backup_status}")
        print(f"{Fore.GREEN}Type your request or a special command (type 'help' for list){Style.RESET_ALL}\n")
    
    def print_help(self):
        """Print detailed help"""
        print(f"\n{Fore.CYAN}📚 Available Commands:{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Application Management:{Style.RESET_ALL}")
        print("  • list apps, show apps         - List installed applications")
        print("  • uninstall <name>             - Smart uninstall with cleanup")
        print()
        print(f"{Fore.YELLOW}System Information:{Style.RESET_ALL}")
        print("  • services                     - List Windows services")
        print()
        print(f"{Fore.YELLOW}Safety & Backup:{Style.RESET_ALL}")
        print("  • dry run on/off               - Toggle simulation mode")
        print("  • backups, list backups        - Show all backups")
        print("  • restore <backup_id>          - Restore from backup")
        print("  • changes, history             - Show recent changes")
        print("  • create restore point         - Make Windows restore point")
        print("  • restore points               - List restore points")
        print()
        print(f"{Fore.YELLOW}Natural Language:{Style.RESET_ALL}")
        print("  • Any request in plain English - e.g., 'check disk space'")
        print()
        print(f"{Fore.YELLOW}Other:{Style.RESET_ALL}")
        print("  • help, commands               - Show this help")
        print("  • exit                         - Quit the agent")
        print()
    
    async def handle_special_command(self, user_input: str) -> bool:
        """
        Handle special commands
        
        Args:
            user_input: User's input
            
        Returns:
            True if handled as special command
        """
        user_input_lower = user_input.lower().strip()
        
        # Existing Phase 2 commands
        if user_input_lower in ['list apps', 'show apps', 'installed apps']:
            await self.list_installed_apps()
            return True
        
        if user_input_lower.startswith('uninstall '):
            app_name = user_input[10:].strip()
            await self.smart_uninstall_app(app_name)
            return True
        
        if user_input_lower in ['services', 'list services', 'show services']:
            await self.list_services()
            return True
        
        # Phase 3: Safety commands
        # Flexible matching for dry-run (with or without hyphen)
        if user_input_lower in ['dry-run on', 'dry run on', 'dryrun on', 'enable dry-run', 'enable dry run']:
            self.dry_run_mode = True
            print(f"\n{Fore.YELLOW}🔍 DRY-RUN MODE ENABLED - Commands will be simulated, not executed{Style.RESET_ALL}\n")
            return True
        
        if user_input_lower in ['dry-run off', 'dry run off', 'dryrun off', 'disable dry-run', 'disable dry run']:
            self.dry_run_mode = False
            print(f"\n{Fore.GREEN}⚡ LIVE MODE ENABLED - Commands will be executed{Style.RESET_ALL}\n")
            return True
        
        if user_input_lower in ['backups', 'list backups']:
            await self.list_backups()
            return True
        
        if user_input_lower.startswith('restore '):
            backup_id = user_input[8:].strip()
            await self.restore_from_backup(backup_id)
            return True
        
        if user_input_lower in ['changes', 'history', 'recent changes']:
            await self.show_recent_changes()
            return True
        
        if user_input_lower in ['create restore point', 'make restore point', 'new restore point']:
            await self.create_system_restore_point()
            return True
        
        if user_input_lower in ['restore points', 'list restore points', 'show restore points']:
            await self.list_restore_points()
            return True
        
        # Help command
        if user_input_lower in ['help', 'commands', 'what can you do']:
            self.print_help()
            return True
        
        return False
    
    async def list_backups(self):
        """List all available backups"""
        print(f"\n{Fore.BLUE}📦 Available Backups:{Style.RESET_ALL}\n")
        
        backups = self.backup_manager.list_backups()
        
        if not backups:
            print(f"{Fore.YELLOW}No backups found{Style.RESET_ALL}\n")
            return
        
        for i, backup in enumerate(reversed(backups[-10:]), 1):
            timestamp = backup.timestamp.split('T')[0] + ' ' + backup.timestamp.split('T')[1][:8]
            size = self.backup_manager.format_size(backup.size_bytes)
            print(f"{i}. {backup.backup_id}")
            print(f"   Time: {timestamp}")
            print(f"   Operation: {backup.operation}")
            print(f"   Items: {len(backup.items_backed_up)}")
            print(f"   Size: {size}")
            print(f"   Can restore: {Fore.GREEN if backup.can_restore else Fore.RED}{'Yes' if backup.can_restore else 'No'}{Style.RESET_ALL}")
            print()
        
        print(f"{Fore.YELLOW}💡 Use 'restore <backup_id>' to restore a backup{Style.RESET_ALL}\n")
    
    async def restore_from_backup(self, backup_id: str):
        """Restore from a backup"""
        print(f"\n{Fore.BLUE}🔄 Restoring from backup: {backup_id}...{Style.RESET_ALL}\n")
        
        success = await self.backup_manager.restore_backup(backup_id)
        
        if success:
            print(f"\n{Fore.GREEN}✅ Backup restored successfully!{Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.RED}❌ Failed to restore backup{Style.RESET_ALL}\n")
    
    async def show_recent_changes(self):
        """Show recent system changes"""
        print(f"\n{Fore.BLUE}📝 Recent Changes:{Style.RESET_ALL}\n")
        
        changes = self.change_tracker.get_recent_changes(10)
        
        if not changes:
            print(f"{Fore.YELLOW}No changes recorded{Style.RESET_ALL}\n")
            return
        
        for i, change in enumerate(reversed(changes), 1):
            timestamp = change.timestamp.split('T')[0] + ' ' + change.timestamp.split('T')[1][:8]
            rollback = f"{Fore.GREEN}Yes{Style.RESET_ALL}" if change.rollback_available else f"{Fore.RED}No{Style.RESET_ALL}"
            
            print(f"{i}. [{timestamp}] {change.change_type}")
            print(f"   Target: {change.target}")
            print(f"   Rollback: {rollback}")
            print()
    
    async def create_system_restore_point(self):
        """Create a Windows System Restore Point"""
        print(f"\n{Fore.BLUE}📍 Creating Windows System Restore Point...{Style.RESET_ALL}\n")
        
        description = f"Personal AI Agent - {Path.cwd().name}"
        restore_id = await self.restore_point_manager.create_restore_point(description)
        
        if restore_id:
            print(f"{Fore.GREEN}✅ Restore point created successfully!{Style.RESET_ALL}")
            print(f"Description: {description}\n")
        else:
            print(f"{Fore.RED}❌ Failed to create restore point{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Note: Requires administrator privileges{Style.RESET_ALL}\n")
    
    async def list_restore_points(self):
        """List Windows restore points"""
        print(f"\n{Fore.BLUE}📍 Windows System Restore Points:{Style.RESET_ALL}\n")
        
        points = await self.restore_point_manager.list_restore_points()
        
        if not points:
            print(f"{Fore.YELLOW}No restore points found{Style.RESET_ALL}\n")
            return
        
        for i, point in enumerate(reversed(points[-10:]), 1):
            seq = point.get('SequenceNumber', 'N/A')
            time = point.get('CreationTime', 'N/A')
            desc = point.get('Description', 'N/A')
            
            print(f"{i}. Sequence #{seq}")
            print(f"   Time: {time}")
            print(f"   Description: {desc}")
            print()
    
    async def list_installed_apps(self):
        """List all installed applications"""
        print(f"\n{Fore.BLUE}📦 Scanning installed applications...{Style.RESET_ALL}")
        
        apps = await self.app_analyzer.analyze_installed_apps()
        
        print(f"\n{Fore.GREEN}Found {len(apps)} installed applications:{Style.RESET_ALL}\n")
        
        for i, app in enumerate(apps[:20], 1):
            version = f"v{app.version}" if app.version else "version unknown"
            print(f"{i}. {app.name} ({version})")
        
        if len(apps) > 20:
            print(f"\n... and {len(apps) - 20} more applications")
        
        print(f"\n{Fore.YELLOW}💡 Tip: Use 'uninstall <app name>' to remove an app{Style.RESET_ALL}\n")
    
    async def smart_uninstall_app(self, app_name: str):
        """Smart uninstall with backup and rollback"""
        print(f"\n{Fore.BLUE}🔍 Analyzing '{app_name}' for complete removal...{Style.RESET_ALL}\n")
        
        # Create uninstall plan
        plan = await self.smart_uninstaller.create_uninstall_plan(app_name)
        
        # Display plan
        summary = self.smart_uninstaller.format_plan_summary(plan)
        print(summary)
        
        if not plan.app_found and not plan.leftover_items:
            print(f"\n{Fore.YELLOW}No application or leftovers found.{Style.RESET_ALL}")
            return
        
        # Create rollback plan
        rollback_actions = []
        if plan.related_services:
            rollback_actions.extend(
                self.rollback_engine.create_service_stop_rollback(plan.related_services)
            )
        
        if rollback_actions:
            print(f"\n{Fore.CYAN}🔄 Rollback Plan:{Style.RESET_ALL}")
            rollback_summary = self.rollback_engine.get_rollback_summary(rollback_actions)
            print(rollback_summary)
        
        # Confirm
        print(f"\n{Fore.YELLOW}Proceed with this uninstall? (yes/no): {Style.RESET_ALL}", end='')
        response = input().strip().lower()
        
        if response not in ['yes', 'y']:
            print(f"\n{Fore.YELLOW}Uninstall cancelled{Style.RESET_ALL}")
            return
        
        # Create backup if enabled
        backup_id = None
        if self.auto_backup and plan.leftover_items:
            print(f"\n{Fore.BLUE}💾 Creating backup...{Style.RESET_ALL}")
            backup_info = await self.backup_manager.create_backup(
                [str(item.path) for item in plan.leftover_items[:10]],
                f"Uninstall {app_name}"
            )
            if backup_info:
                backup_id = backup_info.backup_id
                print(f"{Fore.GREEN}✅ Backup created: {backup_id}{Style.RESET_ALL}")
        
        # Execute uninstall
        await self.execute_uninstall_plan(plan, backup_id)
        
        # Save rollback script
        if rollback_actions:
            operation_id = f"uninstall_{app_name.replace(' ', '_')}"
            script_path = self.rollback_engine.save_rollback_plan(rollback_actions, operation_id)
            if script_path:
                print(f"\n{Fore.CYAN}💾 Rollback script saved: {script_path}{Style.RESET_ALL}")
    
    async def execute_uninstall_plan(self, plan, backup_id=None):
        """Execute an uninstall plan"""
        print(f"\n{Fore.BLUE}⚙️  Executing uninstall plan...{Style.RESET_ALL}\n")
        
        # Stop services
        for cmd in plan.service_stop_commands:
            print(f"Stopping service: {cmd}")
            result = await self.executor.execute(cmd)
            if not result.success:
                print(f"{Fore.RED}Failed: {result.stderr}{Style.RESET_ALL}")
            else:
                # Track change
                self.change_tracker.record_change(
                    'service_stopped', cmd, rollback_id=backup_id
                )
        
        # Run uninstaller
        if plan.uninstall_command:
            print(f"\nRunning uninstaller...")
            result = await self.executor.execute(plan.uninstall_command)
            if result.success:
                print(f"{Fore.GREEN}✅ Uninstaller completed{Style.RESET_ALL}")
                # Track change
                self.change_tracker.record_change(
                    'app_uninstalled', plan.uninstall_command, rollback_id=backup_id
                )
            else:
                print(f"{Fore.RED}❌ Uninstaller failed: {result.stderr}{Style.RESET_ALL}")
        
        # Clean leftovers
        if plan.cleanup_commands:
            print(f"\nCleaning up {len(plan.cleanup_commands)} leftover items...")
            for i, cmd in enumerate(plan.cleanup_commands[:5], 1):
                result = await self.executor.execute(cmd)
                if result.success:
                    print(f"  ✓ Cleaned item {i}")
                    # Track change
                    self.change_tracker.record_change(
                        'file_deleted', cmd, rollback_id=backup_id
                    )
        
        print(f"\n{Fore.GREEN}✅ Uninstall process complete!{Style.RESET_ALL}\n")
    
    async def list_services(self):
        """List Windows services"""
        print(f"\n{Fore.BLUE}⚙️  Loading Windows services...{Style.RESET_ALL}")
        
        services = await self.service_inspector.list_all_services()
        running = [s for s in services if s.status.lower() == 'running']
        
        print(f"\n{Fore.GREEN}Found {len(running)} running services (out of {len(services)} total):{Style.RESET_ALL}\n")
        
        for i, svc in enumerate(running[:15], 1):
            print(f"{i}. {svc.display_name} ({svc.name}) - {svc.start_type}")
        
        if len(running) > 15:
            print(f"\n... and {len(running) - 15} more running services\n")
    
    async def process_request(self, user_request: str):
        """Process a user request with Phase 3 safety features"""
        
        # Log the request
        self.audit_logger.log_request(user_request)
        
        print(f"\n{Fore.BLUE}🤔 Analyzing your request...{Style.RESET_ALL}")
        
        try:
            # Generate command using LLM
            command_data = await self.llm_client.generate_command(user_request)
            
            command = command_data.get("command", "")
            explanation = command_data.get("explanation", "No explanation provided")
            
            if not command:
                print(f"{Fore.RED}❌ Could not generate a command for this request{Style.RESET_ALL}")
                return
            
            # Sandbox validation
            validation = self.sandbox.validate_command(command)
            
            if not validation['allowed']:
                print(f"\n{Fore.RED}🛑 COMMAND BLOCKED BY SANDBOX{Style.RESET_ALL}")
                print(f"Reason: {validation['reason']}")
                print(f"Risk Level: {validation['risk_level']}")
                print(f"{self.sandbox.get_risk_explanation(validation['risk_level'])}\n")
                return
            
            # Check for high-risk
            if validation.get('requires_extra_confirmation'):
                print(f"\n{Fore.YELLOW}⚠️ HIGH-RISK COMMAND DETECTED{Style.RESET_ALL}")
                print(f"Risk Level: {validation['risk_level']}\n")
            
            # Dry-run mode
            if self.dry_run_mode:
                dry_run_result = await self.dry_run_simulator.simulate_command(command)
                report = self.dry_run_simulator.format_dry_run_report(dry_run_result)
                print(f"\n{report}\n")
                return
            
            # Display explanation
            print(f"\n{Fore.YELLOW}💡 Explanation:{Style.RESET_ALL}")
            print(f"{explanation}\n")
            
            print(f"{Fore.CYAN}📋 Command:{Style.RESET_ALL}")
            print(f"{command}\n")
            
            # Confirmation
            print(f"{Fore.YELLOW}Execute this command? (yes/no): {Style.RESET_ALL}", end='')
            response = input().strip().lower()
            
            if response not in ['yes', 'y']:
                print(f"\n{Fore.YELLOW}Command cancelled{Style.RESET_ALL}")
                self.audit_logger.log_cancellation(user_request, command)
                return
            
            # Execute
            print(f"\n{Fore.BLUE}⚙️  Executing...{Style.RESET_ALL}\n")
            
            result = await self.executor.execute(command)
            
            # Display result
            if result.success:
                print(f"{Fore.GREEN}✅ Success!{Style.RESET_ALL}\n")
                if result.stdout:
                    print(f"{Fore.WHITE}{result.stdout}{Style.RESET_ALL}")
                
                # Track change
                self.change_tracker.record_change(
                    'command_executed', command,
                    before_state={'request': user_request},
                    after_state={'stdout': result.stdout[:200]}
                )
                
                self.audit_logger.log_execution(user_request, command, result)
            else:
                print(f"{Fore.RED}❌ Failed!{Style.RESET_ALL}\n")
                if result.stderr:
                    print(f"{Fore.RED}{result.stderr}{Style.RESET_ALL}")
                
                self.audit_logger.log_execution(user_request, command, result)
        
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}\n")
    
    async def run(self):
        """Main CLI loop"""
        self.print_banner()
        
        # Check Ollama connection
        if not await self.llm_client.check_connection():
            print(f"{Fore.RED}❌ Cannot connect to Ollama. Make sure it's running.{Style.RESET_ALL}\n")
            return
        
        print(f"{Fore.GREEN}✓ Connected to Ollama (llama3){Style.RESET_ALL}\n")
        
        while True:
            try:
                # Get user input
                user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}\n")
                    break
                
                # Check for special commands
                is_special = await self.handle_special_command(user_input)
                
                # Process regular request
                if not is_special:
                    await self.process_request(user_input)
            
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Interrupted. Type 'exit' to quit.{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    agent = Phase3CLIAgent()
    asyncio.run(agent.run())
