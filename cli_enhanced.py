"""
Enhanced CLI with OS Intelligence - Phase 2
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
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()


class EnhancedCLIAgent:
    """Enhanced CLI with OS Intelligence capabilities"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.executor = CommandExecutor(log_path="./logs/commands.log")
        self.confirmation_handler = ConfirmationHandler()
        self.audit_logger = AuditLogger()
        
        # OS Intelligence components
        self.smart_uninstaller = SmartUninstaller()
        self.app_analyzer = AppAnalyzer()
        self.service_inspector = ServiceInspector()
        
    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}   Personal AI Agent - Phase 2: OS Intelligence")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Features:{Style.RESET_ALL}")
        print("  ✓ Explain → Confirm → Execute workflow")
        print("  ✓ Safe command execution with validation")
        print("  ✓ Complete audit trail")
        print(f"  {Fore.GREEN}✓ Smart app uninstaller{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}✓ Leftover detection & cleanup{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}✓ Service management{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Special Commands:{Style.RESET_ALL}")
        print("  • 'list apps' - Show installed applications")
        print("  • 'uninstall <app>' - Smart uninstall application")
        print("  • 'services' - List Windows services")
        print("  • 'exit' - Quit\n")
        print(f"{Fore.GREEN}Type your request or a special command{Style.RESET_ALL}\n")
    
    async def handle_special_command(self, user_input: str) -> bool:
        """
        Handle special OS intelligence commands
        
        Args:
            user_input: User's input
            
        Returns:
            True if handled as special command
        """
        user_input_lower = user_input.lower().strip()
        
        # List apps
        if user_input_lower in ['list apps', 'show apps', 'installed apps']:
            await self.list_installed_apps()
            return True
        
        # Uninstall app
        if user_input_lower.startswith('uninstall '):
            app_name = user_input[10:].strip()
            await self.smart_uninstall_app(app_name)
            return True
        
        # List services
        if user_input_lower in ['services', 'list services', 'show services']:
            await self.list_services()
            return True
        
        return False
    
    async def list_installed_apps(self):
        """List all installed applications"""
        print(f"\n{Fore.BLUE}📦 Scanning installed applications...{Style.RESET_ALL}")
        
        apps = await self.app_analyzer.analyze_installed_apps()
        
        print(f"\n{Fore.GREEN}Found {len(apps)} installed applications:{Style.RESET_ALL}\n")
        
        # Show first 20 apps
        for i, app in enumerate(apps[:20], 1):
            version = f"v{app.version}" if app.version else "version unknown"
            print(f"{i}. {app.name} ({version})")
        
        if len(apps) > 20:
            print(f"\n... and {len(apps) - 20} more applications")
        
        print(f"\n{Fore.YELLOW}💡 Tip: Use 'uninstall <app name>' to remove an app{Style.RESET_ALL}\n")
    
    async def smart_uninstall_app(self, app_name: str):
        """
        Smart uninstall an application
        
        Args:
            app_name: Application name
        """
        print(f"\n{Fore.BLUE}🔍 Analyzing '{app_name}' for complete removal...{Style.RESET_ALL}\n")
        
        # Create uninstall plan
        plan = await self.smart_uninstaller.create_uninstall_plan(app_name)
        
        # Display plan
        summary = self.smart_uninstaller.format_plan_summary(plan)
        print(summary)
        
        if not plan.app_found and not plan.leftover_items:
            print(f"\n{Fore.YELLOW}No application or leftovers found.{Style.RESET_ALL}")
            return
        
        # Ask for confirmation
        print(f"\n{Fore.YELLOW}Proceed with this uninstall plan? (yes/no): {Style.RESET_ALL}", end='')
        response = input().strip().lower()
        
        if response in ['yes', 'y']:
            await self.execute_uninstall_plan(plan)
        else:
            print(f"\n{Fore.YELLOW}Uninstall cancelled{Style.RESET_ALL}")
    
    async def execute_uninstall_plan(self, plan):
        """Execute an uninstall plan"""
        print(f"\n{Fore.BLUE}⚙️  Executing uninstall plan...{Style.RESET_ALL}\n")
        
        # Stop services
        for cmd in plan.service_stop_commands:
            print(f"Stopping service: {cmd}")
            result = await self.executor.execute(cmd)
            if not result.success:
                print(f"{Fore.RED}Failed: {result.stderr}{Style.RESET_ALL}")
        
        # Run uninstaller
        if plan.uninstall_command:
            print(f"\nRunning uninstaller...")
            result = await self.executor.execute(plan.uninstall_command)
            if result.success:
                print(f"{Fore.GREEN}✅ Uninstaller completed{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Uninstaller failed: {result.stderr}{Style.RESET_ALL}")
        
        # Clean leftovers
        if plan.cleanup_commands:
            print(f"\nCleaning up {len(plan.cleanup_commands)} leftover items...")
            for i, cmd in enumerate(plan.cleanup_commands[:5], 1):  # Limit to first 5 for safety
                result = await self.executor.execute(cmd)
                if result.success:
                    print(f"  ✓ Cleaned item {i}")
        
        print(f"\n{Fore.GREEN}✅ Uninstall process complete!{Style.RESET_ALL}\n")
    
    async def list_services(self):
        """List Windows services"""
        print(f"\n{Fore.BLUE}⚙️  Loading Windows services...{Style.RESET_ALL}")
        
        services = await self.service_inspector.list_all_services()
        
        # Filter running services
        running = [s for s in services if s.status.lower() == 'running']
        
        print(f"\n{Fore.GREEN}Found {len(running)} running services (out of {len(services)} total):{Style.RESET_ALL}\n")
        
        for i, svc in enumerate(running[:15], 1):
            print(f"{i}. {svc.display_name} ({svc.name}) - {svc.start_type}")
        
        if len(running) > 15:
            print(f"\n... and {len(running) - 15} more running services\n")
    
    async def process_request(self, user_request: str):
        """Process a regular user request (existing Phase 1 logic)"""
        
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
            
            # Validate the command
            is_safe, warnings, risk_level = CommandValidator.validate(command)
            
            if not is_safe:
                print(f"{Fore.RED}🛑 This command is too dangerous to execute:{Style.RESET_ALL}")
                for warning in warnings:
                    print(f"  • {warning}")
                return
            
            # Create confirmation request
            request_id = self.confirmation_handler.create_request(
                operation=user_request,
                command=command,
                explanation=explanation,
                warnings=warnings,
                risk_level=risk_level
            )
            
            # Display confirmation request
            conf_request = self.confirmation_handler.get_request(request_id)
            formatted = self.confirmation_handler.format_for_user(conf_request)
            print(f"\n{formatted}\n")
            
            # Ask for confirmation
            response = input(f"{Fore.YELLOW}Proceed with execution? (yes/no): {Style.RESET_ALL}").strip().lower()
            
            if response in ['yes', 'y']:
                self.confirmation_handler.approve(request_id)
                self.audit_logger.log_confirmation(request_id, True)
                
                print(f"\n{Fore.BLUE}⚙️  Executing command...{Style.RESET_ALL}")
                
                # Execute the command
                result = await self.executor.execute(
                    command=command,
                    timeout=30,
                    require_admin=CommandValidator.requires_admin(command)
                )
                
                # Log execution
                self.audit_logger.log_execution(command, result.to_dict())
                
                # Display result
                if result.success:
                    print(f"\n{Fore.GREEN}✅ Command executed successfully!{Style.RESET_ALL}")
                    if result.stdout:
                        print(f"\n{Fore.WHITE}Output:{Style.RESET_ALL}")
                        print(result.stdout)
                else:
                    print(f"\n{Fore.RED}❌ Command execution failed{Style.RESET_ALL}")
                    if result.stderr:
                        print(f"\n{Fore.RED}Error:{Style.RESET_ALL}")
                        print(result.stderr)
            else:
                self.confirmation_handler.deny(request_id, "User declined")
                self.audit_logger.log_confirmation(request_id, False)
                print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
            self.audit_logger.log_error("processing_error", str(e))
    
    async def run(self):
        """Run the enhanced CLI interface"""
        self.print_banner()
        
        # Check if Ollama is available
        if not self.llm_client.is_available():
            print(f"{Fore.RED}⚠️  Warning: Ollama is not running!{Style.RESET_ALL}")
            print("Please start Ollama and ensure the model is available.")
            print(f"Expected: {self.llm_client.host}\n")
            return
        
        print(f"{Fore.GREEN}✓ Connected to Ollama ({self.llm_client.model}){Style.RESET_ALL}\n")
        
        while True:
            try:
                user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print(f"\n{Fore.CYAN}Goodbye! 👋{Style.RESET_ALL}\n")
                    break
                
                # Check for special commands
                if await self.handle_special_command(user_input):
                    continue
                
                # Process as regular request
                await self.process_request(user_input)
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}Goodbye! 👋{Style.RESET_ALL}\n")
                break
            except Exception as e:
                print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")


async def main():
    """Main entry point"""
    agent = EnhancedCLIAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
