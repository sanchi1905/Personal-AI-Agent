# Personal AI Agent

A trustworthy, system-aware AI assistant that safely manages your Windows PC with transparency and control.

## 🎯 Key Features

- **Explain → Confirm → Execute**: See exactly what will happen before any action
- **OS-Aware Intelligence**: Understands Windows registry, services, and app leftovers
- **Advanced Safety**: Automatic backups, rollback scripts, dry-run mode, and Windows restore points
- **Change Tracking**: Complete undo capabilities with detailed change history
- **Command Sandbox**: Protects critical system files with allowlist/denylist validation
- **Persistent Memory**: Learns from your system and preferences

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Ollama installed and running
- Windows OS

### Installation

1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.template` to `.env` and configure:
```bash
copy .env.template .env
```

4. Install and start Ollama:
```bash
# Download from: https://ollama.ai
ollama pull llama3
```

5. Run the agent:
```bash
# Phase 1 & 2: Basic features + OS Intelligence
python cli_enhanced.py

# Phase 3: Full safety features
python cli_phase3.py

# Phase 4: Learning & Memory
python cli_phase4.py

# Phase 5: Desktop UI (recommended) 🎨
# Terminal 1 - Backend API:
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend UI:
cd ui
npm install
npm run dev

# Open browser to http://localhost:3000
```

## 📁 Project Structure

```
personal-ai-agent/
├── src/
│   ├── llm/                 # LLM interaction layer
│   ├── executor/            # Command execution engine
│   ├── safety/              # Safety checks and validation
│   ├── safety_advanced/     # Phase 3: Backups, rollback, dry-run
│   ├── os_intelligence/     # Phase 2: Registry, services, uninstaller
│   ├── memory/              # System memory store
│   ├── memory_advanced/     # Phase 4: Learning, preferences, suggestions
│   └── api/                 # Phase 5: FastAPI backend for UI
├── ui/                      # Phase 5: React Desktop UI
│   ├── src/components/      # React components
│   ├── src/services/        # API client
│   └── src/hooks/           # Custom hooks
├── tests/                   # Unit and integration tests
├── logs/                    # Execution logs
├── backups/                 # Automatic backups before operations
├── ronfig/                  # User preferences and settings
├── memory/                  # Learned patterns and command history
├── cli_phase3.py           # Phase 3 CLI
├── cli_phase4.py           # Phase 4ted rollback PowerShell scripts
├── cli_phase3.py           # Phase 3 CLI (recommended)
### Phase 1 & 2 (Basic Safety)
- ✅ No silent execution
- ✅ Full audit trail
- ✅ User confirmation required
- ✅ Command preview before execution
- ✅ Dangerous command detection

### Phase 3 (Advanced Safety)
- ✅ **Automatic backups** before destructive operations
- ✅ **Rollback scripts** generated for all changes
- ✅ **Dry-run mode** - test commands without executing
- ✅ **Change tracking** with complete undo history
- ✅ **Command sandbox** - protects critical system paths
- ✅ **Windows restore points** integration

### Phase 4 (Learning & Memory)
- ✅ **User preferences** - Personalized settings and configurations
- ✅ **Pattern learning** - Learns from your command usage
- ✅ **Smart suggestions** - Context-aware command recommendations
- ✅ **System context awareness** - Tracks system health and state
- ✅ **Command prediction** - Predicts next likely commands
- ✅ **Performance optimization** - Suggests command improvements
- ✅ **Personalized shortcuts** - Auto-generates shortcuts for frequent commands

### Phase 5 (Desktop UI) ⭐ NEW
- ✅ **ChatGPT-like interface** - Modern conversational UI
- ✅ **Real-time system monitoring** - Live CPU, memory, disk stats
- ✅ **Visual command preview** - See commands before execution
- ✅ **Interactive confirmations** - Beautiful approve/deny dialogs
- ✅ **WebSocket updates** - Real-time status and execution feedback
- ✅ **Professional design** - Dark mode, responsive, accessible
- ✅ **Complete integration** - All Phase 1-4 features in one UI

## 🎮 Usage Examples

### Phase 4 CLI Commands

```bash
# Natural language - just ask!
> list running processes
> show disk space
> what services are running?

# System intelligence
list apps              # Show installed applications
list services          # Show Windows services

# Safety features
dry-run on             # Enable simulation mode
backups                # View all backups
changes                # Show recent system changes

# Learning & Memory (NEW!)
suggestions            # Get smart command recommendations
stats                  # View learning statistics
settings               # Configure preferences
context                # Show system health & context

# Example: Learning in action
> list apps
✅ Command executed and learned

> suggestions
💡 Based on your history, you might want to:
   • Get-Service | Where-Object {$_.Status -eq "Running"}
   • Get-Process | Sort-Object CPU -Descending

> stats
📊 Learning Statistics:
   Commands learned: 15
   Success rate: 93%
   Most used: list apps (5 times)
```

### Phase 3 CLI Commands (Still Available)

```bash
# Toggle dry-run mode (test without executing)
dry-run on
dry-run off

# View all backups
backups

# Restore from backup
restore backup_20240114_123456

# View recent changes
changes

# Create Windows restore point
create restore point

# List Windows restore points
restore points

# Smart uninstall with automatic backup
uninstall "Application Name"
```

## 📋 Phase 3 Features

### 1. Automatic Backups
Before any destructive operation, the system automatically creates backups:
- File deletions backed up
- Registry changes saved
- Service states preserved
- One-click restore capability

### 2. Rollback Engine
Every operation generates a PowerShell rollback script:
- Stored in `rollback_scripts/`
- Human-readable and editable
- Can be executed manually if needed
- Service restart commands included

### 3. Dry-Run Mode
Test commands without making changes:
- Predicts all changes
- Assesses risks
- Estimates execution time
- Checks admin requirements
- Determines reversibility

### 4. Change Tracker
Complete audit trail of all modifications:
- Timestamps for every change
- Before/after states recorded
- Rollback IDs linked
- Query by type or date

### 5. Command Sandbox
Multi-layer protection:
- Protected system paths (Windows, System32, etc.)
- Dangerous pattern detection (format drive, etc.)
- Custom allowlist/denylist support
- High-risk command flagging

### 6. Windows Restore Points
Native Windows integration:
- Create restore points before major operations
- List all available restore points
- System-level rollback capability
- Requires admin privilegestees

- ✅ No silent execution
- ✅ Full audit trail
- ✅ User confirmation required
- ✅ Command preview before execution
- ✅ Rollback support

## 📝 License

MIT License - See LICENSE file for details
