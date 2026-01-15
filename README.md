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

# Phase 3: Full safety features (recommended)
python cli_phase3.py
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
│   └── api/                 # FastAPI routes
├── tests/                   # Unit and integration tests
├── logs/                    # Execution logs
├── backups/                 # Automatic backups before operations
├── rollback_scripts/        # Generated rollback PowerShell scripts
├── cli_phase3.py           # Phase 3 CLI (recommended)
### Phase 1 & 2 (Basic Safety)
- ✅ No silent execution
- ✅ Full audit trail
- ✅ User confirmation required
- ✅ Command preview before execution
- ✅ Dangerous command detection

### Phase 3 (Advanced Safety) ⭐ NEW
- ✅ **Automatic backups** before destructive operations
- ✅ **Rollback scripts** generated for all changes
- ✅ **Dry-run mode** - test commands without executing
- ✅ **Change tracking** with complete undo history
- ✅ **Command sandbox** - protects critical system paths
- ✅ **Windows restore points** integration

## 🎮 Usage Examples

### Phase 3 CLI Commands

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
