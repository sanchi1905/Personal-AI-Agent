"""
Personal AI Agent - Phase 4: System Memory & Learning
Enhanced CLI with pattern learning and smart suggestions
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm.client import LLMClient
from executor.command_executor import CommandExecutor
from safety.confirmation import ConfirmationHandler
from safety.audit import AuditLogger
from memory.database import MemoryDatabase
from os_intelligence.registry_scanner import RegistryScanner
from os_intelligence.app_analyzer import AppAnalyzer
from os_intelligence.leftover_detector import LeftoverDetector
from os_intelligence.service_inspector import ServiceInspector
from os_intelligence.smart_uninstaller import SmartUninstaller
from safety_advanced.backup_manager import BackupManager
from safety_advanced.rollback_engine import RollbackEngine
from safety_advanced.dry_run import DryRunSimulator
from safety_advanced.change_tracker import ChangeTracker
from safety_advanced.sandbox import CommandSandbox
from safety_advanced.restore_point import RestorePointManager
from memory_advanced.user_preferences import UserPreferences
from memory_advanced.pattern_learner import PatternLearner
from memory_advanced.smart_suggester import SmartSuggester
from memory_advanced.context_manager import SystemContextManager


class PersonalAIAgent:
    """Main AI Agent with learning capabilities"""
    
    def __init__(self):
        """Initialize agent components"""
        self.llm = LLMClient()
        self.executor = CommandExecutor()
        self.confirmation = ConfirmationHandler()
        self.audit = AuditLogger()
        self.db = MemoryDatabase()
        
        # OS Intelligence
        self.registry_scanner = RegistryScanner()
        self.app_analyzer = AppAnalyzer()
        self.leftover_detector = LeftoverDetector()
        self.service_inspector = ServiceInspector()
        self.uninstaller = SmartUninstaller()
        
        # Advanced Safety
        self.backup_manager = BackupManager()
        self.rollback_engine = RollbackEngine()
        self.dry_run = DryRunSimulator()
        self.change_tracker = ChangeTracker()
        self.sandbox = CommandSandbox()
        self.restore_point_manager = RestorePointManager()
        self.dry_run_enabled = False
        
        # Memory & Learning (Phase 4)
        self.preferences = UserPreferences()
        self.pattern_learner = PatternLearner()
        self.suggester = SmartSuggester(self.pattern_learner, self.preferences)
        self.context_manager = SystemContextManager()
        
        # Command history
        self.command_history = []
    
    async def initialize(self):
        """Initialize async components"""
        await self.db.initialize()
        
        # Apply saved preferences
        self.dry_run_enabled = self.preferences.get('dry_run_mode', False)
        
        print("✅ Personal AI Agent initialized (Phase 4: Learning & Memory)")
        print("=" * 60)
    
    async def show_welcome(self):
        """Show welcome message"""
        # Check system health
        health = self.context_manager.get_system_health()
        recommendations = self.context_manager.get_resource_recommendations()
        
        print("\n🤖 Personal AI Agent - Your Intelligent Windows Assistant")
        print("=" * 60)
        
        # Show system health
        print(f"\n📊 System Health: {health['overall_status'].upper()}")
        print(f"   CPU: {health['cpu']['percent']:.1f}% | Memory: {health['memory']['percent']:.1f}% | Disk: {health['disk']['percent']:.1f}%")
        
        if recommendations:
            print("\n⚠️ Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        
        # Show learning stats
        stats = self.pattern_learner.get_statistics()
        if stats['total_executions'] > 0:
            print(f"\n📚 Learning Stats:")
            print(f"   Commands learned: {stats['total_executions']}")
            print(f"   Unique patterns: {stats['total_patterns']}")
            print(f"   Success rate: {stats['avg_success_rate']:.1%}")
        
        # Show preferences
        verbose = self.preferences.get('verbose_explanations', True)
        learn = self.preferences.get('learn_patterns', True)
        suggestions = self.preferences.get('smart_suggestions', True)
        
        print(f"\n⚙️  Active Features:")
        print(f"   Dry-run mode: {'ON' if self.dry_run_enabled else 'OFF'}")
        print(f"   Verbose mode: {'ON' if verbose else 'OFF'}")
        print(f"   Pattern learning: {'ON' if learn else 'OFF'}")
        print(f"   Smart suggestions: {'ON' if suggestions else 'OFF'}")
        
        print("\n💡 Tips:")
        print("   • Type 'help' for all commands")
        print("   • Type 'settings' to configure preferences")
        print("   • Type 'suggestions' to see smart recommendations")
        print("   • Type 'stats' to see learning statistics")
        print("=" * 60)
    
    async def handle_special_command(self, user_input: str) -> bool:
        """Handle special CLI commands"""
        cmd_lower = user_input.lower().strip()
        
        # Dry-run control
        if cmd_lower in ['dry-run on', 'dry run on', 'dryrun on', 'enable dry-run']:
            self.dry_run_enabled = True
            self.preferences.set('dry_run_mode', True)
            print("✅ Dry-run mode enabled - commands will be simulated")
            return True
        
        if cmd_lower in ['dry-run off', 'dry run off', 'dryrun off', 'disable dry-run']:
            self.dry_run_enabled = False
            self.preferences.set('dry_run_mode', False)
            print("✅ Dry-run mode disabled - commands will execute normally")
            return True
        
        # List apps
        if cmd_lower in ['list apps', 'show apps', 'apps']:
            print("\n🔍 Scanning installed applications...")
            apps = self.registry_scanner.scan_installed_apps()
            
            if apps:
                print(f"\n📦 Found {len(apps)} installed applications:\n")
                for app in sorted(apps, key=lambda x: x.get('display_name', '').lower()):
                    name = app.get('display_name', 'Unknown')
                    version = app.get('version', 'N/A')
                    print(f"  • {name} (v{version})")
            else:
                print("⚠️ No applications found")
            return True
        
        # List services
        if cmd_lower in ['list services', 'show services', 'services']:
            print("\n🔍 Inspecting Windows services...")
            services = self.service_inspector.list_services()
            
            if services:
                running = [s for s in services if s['status'] == 'Running']
                print(f"\n🔧 Found {len(services)} services ({len(running)} running):\n")
                
                for svc in sorted(services, key=lambda x: x['display_name'].lower())[:20]:
                    status_icon = "🟢" if svc['status'] == 'Running' else "🔴"
                    print(f"  {status_icon} {svc['display_name']} ({svc['name']})")
                
                if len(services) > 20:
                    print(f"\n  ... and {len(services) - 20} more services")
            else:
                print("⚠️ No services found")
            return True
        
        # Backups
        if cmd_lower in ['list backups', 'show backups', 'backups']:
            backups = self.backup_manager.list_backups()
            if backups:
                print(f"\n💾 Available backups ({len(backups)}):\n")
                for backup in sorted(backups, key=lambda x: x.created_at, reverse=True):
                    print(f"  • {backup.id}")
                    print(f"    Created: {backup.created_at}")
                    print(f"    Files: {len(backup.files)}")
                    print(f"    Size: {self.backup_manager.format_size(backup.total_size)}")
                    print()
            else:
                print("ℹ️ No backups found")
            return True
        
        # Changes
        if cmd_lower in ['list changes', 'show changes', 'changes']:
            changes = self.change_tracker.get_recent_changes(limit=10)
            if changes:
                print(f"\n📝 Recent changes ({len(changes)}):\n")
                for change in changes:
                    print(f"  • {change.change_type}: {change.path}")
                    print(f"    Time: {change.timestamp}")
                    print()
            else:
                print("ℹ️ No recent changes tracked")
            return True
        
        # Suggestions (Phase 4)
        if cmd_lower in ['suggestions', 'suggest', 'recommend']:
            await self.show_suggestions()
            return True
        
        # Stats (Phase 4)
        if cmd_lower in ['stats', 'statistics', 'learning']:
            await self.show_learning_stats()
            return True
        
        # Settings (Phase 4)
        if cmd_lower in ['settings', 'preferences', 'config']:
            await self.show_settings()
            return True
        
        # Context info (Phase 4)
        if cmd_lower in ['context', 'status']:
            self.show_context_info()
            return True
        
        # Help
        if cmd_lower in ['help', '?']:
            self.show_help()
            return True
        
        # Exit
        if cmd_lower in ['exit', 'quit', 'bye']:
            print("\n👋 Goodbye! Stay safe!")
            return True
        
        return False
    
    async def show_suggestions(self):
        """Show smart suggestions"""
        print("\n💡 Smart Suggestions\n")
        
        # Suggestions based on current context
        context = self.context_manager.get_context()
        print(f"📍 Current context: {context}\n")
        
        # Get suggestions for current context
        if self.command_history:
            predictions = self.suggester.suggest_after_command(self.command_history[-1])
            if predictions:
                print("🔮 Predicted next commands:")
                for cmd, confidence in predictions[:5]:
                    print(f"   {self.suggester.format_suggestion(cmd, confidence)}")
                print()
        
        # Personalized shortcuts
        shortcuts = self.suggester.get_personalized_shortcuts()
        if shortcuts:
            print("⚡ Your personalized shortcuts:")
            for shortcut, cmd in list(shortcuts.items())[:5]:
                print(f"   {shortcut}: {cmd}")
            print()
    
    async def show_learning_stats(self):
        """Show learning statistics"""
        stats = self.pattern_learner.get_statistics()
        
        print("\n📊 Learning Statistics\n")
        print(f"Total commands executed: {stats['total_executions']}")
        print(f"Unique command patterns: {stats['total_patterns']}")
        print(f"Average success rate: {stats['avg_success_rate']:.1%}")
        print(f"Most active context: {stats['most_active_context']}")
        print()
        
        # Top commands
        frequent = self.pattern_learner.get_frequent_commands(5)
        if frequent:
            print("🔥 Most frequently used commands:")
            for i, pattern in enumerate(frequent, 1):
                print(f"   {i}. {pattern.command_template}")
                print(f"      Used {pattern.frequency} times, {pattern.success_rate:.0%} success")
            print()
        
        # Success rate by context
        print("📈 Context performance:")
        contexts = {}
        for pattern in self.pattern_learner.patterns.values():
            for ctx in pattern.contexts:
                if ctx not in contexts:
                    contexts[ctx] = {'total': 0, 'success': 0}
                contexts[ctx]['total'] += pattern.frequency
                contexts[ctx]['success'] += int(pattern.frequency * pattern.success_rate)
        
        for ctx, data in sorted(contexts.items(), key=lambda x: x[1]['total'], reverse=True)[:5]:
            success_rate = (data['success'] / data['total']) if data['total'] > 0 else 0
            print(f"   {ctx}: {data['total']} commands, {success_rate:.0%} success")
    
    async def show_settings(self):
        """Show and allow editing settings"""
        print("\n⚙️  User Preferences\n")
        
        categories = self.preferences.get_categories()
        for category in categories:
            prefs = self.preferences.get_by_category(category)
            if prefs:
                print(f"{category.upper()}:")
                for key, value in prefs.items():
                    print(f"   {key}: {value}")
                print()
        
        print("💡 To change a setting, type: set <key> <value>")
        print("   Example: set dry_run_mode true")
    
    def show_context_info(self):
        """Show context information"""
        info = self.context_manager.get_context_info()
        
        print("\n📍 Context Information\n")
        print(f"Current context: {info['current_context']}")
        print(f"System health: {info['system_health']}")
        print(f"State snapshots: {info['snapshots_count']}")
        
        if info['context_history']:
            print(f"\nRecent context history:")
            for ctx in info['context_history']:
                print(f"   • {ctx}")
    
    def show_help(self):
        """Show help message"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║         Personal AI Agent - Phase 4 Commands                 ║
╚══════════════════════════════════════════════════════════════╝

🎯 NATURAL LANGUAGE
   Just type what you want to do!
   Examples:
   • "list running processes"
   • "show disk space"
   • "stop Chrome service"

🔧 SYSTEM INTELLIGENCE
   list apps              - Show installed applications
   list services          - Show Windows services
   services               - Alias for list services
   apps                   - Alias for list apps

🛡️  SAFETY & ROLLBACK
   dry-run on/off         - Enable/disable simulation mode
   list backups           - Show available backups
   list changes           - Show recent system changes
   create restore point   - Create Windows restore point

💡 LEARNING & MEMORY (NEW!)
   suggestions            - Show smart command suggestions
   stats                  - View learning statistics
   settings               - View/edit preferences
   context                - Show current context & system status

❓ GENERAL
   help                   - Show this help
   exit                   - Quit the agent

═══════════════════════════════════════════════════════════════
        """)
    
    async def process_request(self, user_input: str):
        """Process user request with learning"""
        # Capture system state
        self.context_manager.capture_state()
        
        # Infer context
        context = self.context_manager.infer_context(user_input, self.command_history)
        
        # Check if smart suggestions are enabled
        suggestions_enabled = self.preferences.get('smart_suggestions', True)
        
        # Show suggestions if enabled
        if suggestions_enabled and self.command_history:
            predictions = self.suggester.suggest_after_command(self.command_history[-1])
            if predictions and predictions[0][1] > 0.5:  # High confidence
                print(f"\n💡 Suggestion: {predictions[0][0]} (confidence: {predictions[0][1]:.0%})")
        
        # Generate command
        verbose = self.preferences.get('verbose_explanations', True)
        
        print(f"\n🤖 Generating command for: {user_input}")
        command = await self.llm.generate_command(user_input)
        
        if not command:
            print("❌ Could not generate command")
            return
        
        if verbose:
            print(f"📝 Generated command: {command}")
        
        # Check for optimizations
        optimizations = self.suggester.suggest_optimizations(command)
        if optimizations:
            print("\n💡 Optimization suggestions:")
            for opt in optimizations:
                print(f"   • {opt}")
        
        # Safety validation
        is_safe, warnings = self.sandbox.validate_command(command)
        
        if not is_safe:
            print(f"\n⚠️ Safety concerns detected:")
            for warning in warnings:
                print(f"   • {warning}")
        
        # Confirmation (if required)
        confirmation_required = self.preferences.get('confirmation_required', True)
        
        if confirmation_required:
            confirmed = await self.confirmation.confirm_command(command)
            if not confirmed:
                await self.audit.log_cancellation(user_input, command, "User cancelled")
                print("❌ Command cancelled")
                return
        
        # Backup (if enabled and command is risky)
        auto_backup = self.preferences.get('auto_backup', True)
        if auto_backup and not is_safe:
            print("\n💾 Creating safety backup...")
            backup_id = self.backup_manager.create_backup(f"Pre-execution: {user_input[:50]}")
            if backup_id:
                print(f"✅ Backup created: {backup_id}")
        
        # Execute or simulate
        if self.dry_run_enabled:
            print(f"\n🔍 DRY RUN MODE - Simulating command...")
            result = await self.dry_run.simulate_command(command, context)
            
            print(f"\n📊 Simulation Results:")
            print(f"   Will execute: {result.will_execute}")
            print(f"   Risk level: {result.risk_level}")
            
            if result.predicted_changes:
                print(f"   Predicted changes:")
                for change in result.predicted_changes:
                    print(f"      • {change}")
            
            if result.warnings:
                print(f"   ⚠️ Warnings:")
                for warning in result.warnings:
                    print(f"      • {warning}")
        else:
            # Real execution
            print(f"\n⚡ Executing...")
            result = await self.executor.execute(command)
            
            # Track changes
            if result.success:
                self.change_tracker.track_command(command)
            
            # Log execution
            await self.audit.log_execution(user_input, command, result)
            
            # Learn from execution (if enabled)
            learn_patterns = self.preferences.get('learn_patterns', True)
            if learn_patterns:
                self.pattern_learner.record_command(
                    command,
                    context,
                    result.success,
                    result.execution_time
                )
                
                # Record sequence
                if self.command_history:
                    self.pattern_learner.record_sequence(self.command_history[-1], command)
            
            # Add to history
            self.command_history.append(command)
            
            # Show result
            if result.success:
                print(f"\n✅ Success!")
                if result.output:
                    print(f"\n{result.output}")
            else:
                print(f"\n❌ Execution failed")
                if result.output:
                    print(f"Error: {result.output}")
                
                # Suggest alternatives
                alternatives = self.suggester.suggest_alternatives(command)
                if alternatives:
                    print("\n💡 Try these alternatives:")
                    for alt in alternatives:
                        print(f"   • {alt}")
    
    async def run(self):
        """Main agent loop"""
        await self.initialize()
        await self.show_welcome()
        
        print("\n💬 What would you like me to help you with?")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                is_special = await self.handle_special_command(user_input)
                
                if is_special:
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        break
                    continue
                
                # Process normal request
                await self.process_request(user_input)
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()


async def main():
    """Entry point"""
    agent = PersonalAIAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
