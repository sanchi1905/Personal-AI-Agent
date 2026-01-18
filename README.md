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
├── config/                  # User preferences and settings
├── memory/                  # Learned patterns and command history
├── cli_phase3.py           # Phase 3 CLI with advanced safety
├── cli_phase4.py           # Phase 4 CLI with learning & memory
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
- Requires admin privileges

## 🧠 LLM & AI Architecture

### Model Selection Strategy

This agent uses a **hybrid local + cloud approach** for optimal performance:

**Primary Reasoning (Recommended):**
- **Local:** Ollama + LLaMA 3 - Privacy-focused, offline capable, no API costs
- **Cloud:** GPT-4.1 / GPT-4o - Superior reasoning for complex operations
- **Strategy:** Start with local, escalate to cloud for complex tasks

**Safety Validation:**
- Dedicated safety layer validates all commands
- Checks dangerous patterns, protected paths, privilege requirements
- Independent from primary reasoning model

**Planning Engine:**
- Code-capable models (GPT-4.1 or LLaMA 3 Code)
- Transforms intent → structured execution plans
- Predicts changes and estimates risks

**Memory & Learning:**
- Vector embeddings for command similarity
- Pattern recognition across usage history
- Personalized suggestion engine

### Decision Orchestration Pipeline

Every operation flows through explicit validation stages:

```
User Intent
    ↓
Intent Extraction (LLM)
    ↓
Safety Validation (filters dangerous patterns)
    ↓
Privilege Check (admin requirements)
    ↓
Command Planning (generate execution plan)
    ↓
User Confirmation (explicit approval required)
    ↓
Backup Creation (if destructive)
    ↓
Execution (with failure classification)
    ↓
Audit Logging (complete trail)
```

**Key Safety Layers:**

1. **LLM Safety Contract**
   - No malicious command generation
   - Clear warnings for high-risk operations
   - Alternative suggestion for dangerous requests
   - Educational responses for harmful intent

2. **Validation Layer**
   - Sandboxing protects critical paths
   - Pattern matching for dangerous commands
   - Privilege verification before execution
   - Degraded mode when permissions insufficient

3. **Human-in-the-Loop**
   - No silent execution ever
   - Preview all commands before running
   - Explicit approval required
   - Dry-run mode for testing

### Privacy & Data Handling

**Local Mode (Ollama):**
- ✅ Complete privacy - all processing on-device
- ✅ Works offline
- ✅ No external data transmission
- ✅ No API costs

**Cloud Mode (OpenAI/Azure):**
- ⚠️ Commands sent to API for processing
- ⚠️ Review provider's data usage policy
- ✅ Consider Azure OpenAI for enterprise compliance
- ✅ Option to opt-out of training data usage

**Recommendation:** Use local models (Ollama) for sensitive environments, cloud models for maximum capability.

### Abuse Prevention

**What prevents misuse?**
- Local-only execution (no remote command injection)
- User confirmation required for all operations
- Comprehensive audit logging
- Command sandboxing and validation
- Privilege checks prevent unauthorized escalation
- No autonomous background operations

See [docs/SECURITY.md](docs/SECURITY.md) for detailed threat model.

## 🚫 Scope & Limitations

**What this agent will NEVER do:**
- Modify kernel/firmware/bootloader
- Execute commands silently without approval
- Enable remote access/control
- Mine cryptocurrency or hijack resources
- Exfiltrate data to external servers
- Bypass security controls
- Delete audit logs

See [docs/SCOPE_BOUNDARIES.md](docs/SCOPE_BOUNDARIES.md) for complete list.

## 🎙️ Phase 6: Voice Integration

**ElevenLabs Voice Control** - Hands-free system management with natural voice commands

### Features
- **Voice Input**: Speak commands naturally using your microphone
- **Voice Output**: Agent responses read aloud with high-quality TTS
- **Real-time Transcription**: See what you're saying as you speak
- **Voice Toggle**: Easily enable/disable voice responses
- **Multiple Voice Options**: Choose from various AI voices

### Setup

1. **Get ElevenLabs API Key**:
   - Sign up at [ElevenLabs](https://elevenlabs.io/)
   - Navigate to Profile → API Keys
   - Copy your API key

2. **Configure Environment**:
   ```bash
   # Add to your .env file:
   ELEVENLABS_API_KEY=your_api_key_here
   ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL  # Sarah voice (default)
   ```

3. **Choose Your Voice** (optional):
   - Visit [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
   - Find a voice you like
   - Copy the Voice ID and update `ELEVENLABS_VOICE_ID` in `.env`

### Usage

1. Start the application (backend + frontend)
2. Click the **microphone button** in the chat interface
3. Speak your command (e.g., "Show me disk usage")
4. Agent will transcribe, execute, and speak the response
5. Toggle voice responses on/off with the **speaker button**

### Browser Requirements
- Chrome/Edge/Opera (recommended) - Best Web Speech API support
- Firefox - Partial support
- Safari - Limited support

### Troubleshooting

**"Microphone not working"**
- Check browser permissions (click lock icon in address bar)
- Grant microphone access when prompted
- Ensure microphone is not muted/disabled

**"Voice responses not playing"**
- Verify ELEVENLABS_API_KEY is set in .env
- Check browser console for errors
- Try the browser fallback TTS (doesn't require API key)

**"Transcription is inaccurate"**
- Speak clearly and at moderate pace
- Reduce background noise
- Use a quality microphone
- Check browser's speech recognition language settings

- ✅ No silent execution
- ✅ Full audit trail
- ✅ User confirmation required
- ✅ Command preview before execution
- ✅ Rollback support

## 📚 Documentation

- [Security & Threat Model](docs/SECURITY.md)
- [Scope Boundaries & Non-Goals](docs/SCOPE_BOUNDARIES.md)
- [Phase 5 UI README](ui/README.md)

## 📝 License

MIT License - See LICENSE file for details
