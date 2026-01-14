# Personal AI Agent

A trustworthy, system-aware AI assistant that safely manages your Windows PC with transparency and control.

## 🎯 Key Features

- **Explain → Confirm → Execute**: See exactly what will happen before any action
- **OS-Aware Intelligence**: Understands Windows registry, services, and app leftovers
- **Persistent Memory**: Learns from your system and preferences
- **Safety First**: Rollback plans, audit trails, and user confirmation

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
python main.py
```

## 📁 Project Structure

```
personal-ai-agent/
├── src/
│   ├── llm/          # LLM interaction layer
│   ├── executor/     # Command execution engine
│   ├── safety/       # Safety checks and validation
│   ├── memory/       # System memory store
│   └── api/          # FastAPI routes
├── tests/            # Unit and integration tests
├── logs/             # Execution logs
└── main.py          # Application entry point
```

## 🛡️ Safety Guarantees

- ✅ No silent execution
- ✅ Full audit trail
- ✅ User confirmation required
- ✅ Command preview before execution
- ✅ Rollback support

## 📝 License

MIT License - See LICENSE file for details
