"""
CLI Interface - Command-line interface for the agent (MVP version)
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
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()


class CLIAgent:
    """Command-line interface for the AI agent"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.executor = CommandExecutor(log_path="./logs/commands.log")
        self.confirmation_handler = ConfirmationHandler()
        self.audit_logger = AuditLogger()
        
    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}   Personal AI Agent - Your Trustworthy System Assistant")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Features:{Style.RESET_ALL}")
        print("  ✓ Explain → Confirm → Execute workflow")
        print("  ✓ Safe command execution with validation")
        print("  ✓ Complete audit trail\n")
        print(f"{Fore.GREEN}Type your request or 'exit' to quit{Style.RESET_ALL}\n")
    
    async def process_request(self, user_request: str):
        """Process a user request"""
        
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
        """Run the CLI interface"""
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
                
                await self.process_request(user_input)
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}Goodbye! 👋{Style.RESET_ALL}\n")
                break
            except Exception as e:
                print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")


async def main():
    """Main entry point"""
    agent = CLIAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
