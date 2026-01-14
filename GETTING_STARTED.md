# Getting Started Guide

Welcome to your Personal AI Agent! This guide will help you set up and run the agent.

## Prerequisites

Before you start, make sure you have:
- Python 3.9 or higher installed
- Windows OS (PowerShell required)
- Internet connection for downloading dependencies

## Step 1: Install Ollama

Ollama is required for the AI language model.

1. Download Ollama from: https://ollama.ai
2. Install it on your system
3. Open a command prompt and pull the llama3 model:
   ```
   ollama pull llama3
   ```
4. Verify it's running:
   ```
   ollama list
   ```

## Step 2: Install Python Dependencies

Open a command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install all necessary packages:
- FastAPI (Web framework)
- Ollama (LLM integration)
- Uvicorn (Web server)
- And other dependencies

## Step 3: Verify Environment

Check that your `.env` file exists and contains proper configuration:
- Ollama host and model settings
- Logging paths
- Safety settings

## Step 4: Run the Agent

You have two options:

### Option A: CLI Mode (Recommended for MVP)

Run the command-line interface:

```bash
python cli.py
```

This provides a simple chat interface where you can:
- Type natural language requests
- See what commands will be executed
- Approve or deny each operation
- View full audit trail

### Option B: API Server Mode

Run the FastAPI server:

```bash
python main.py
```

Then visit http://localhost:8000/docs to see the API documentation.

## Example Usage (CLI Mode)

Once you start the CLI, you can try commands like:

```
You: List all running processes
You: Show files in my Documents folder
You: Check disk space
```

For each request:
1. The agent will generate a PowerShell command
2. Show you exactly what it will do
3. Ask for your confirmation
4. Execute only if you approve

## Safety Features

- ✅ No command runs without your approval
- ✅ Every action is logged in `logs/audit.jsonl`
- ✅ Dangerous commands are automatically blocked
- ✅ Full transparency in what will be executed

## Troubleshooting

### "Ollama not available" error
- Make sure Ollama is running
- Check that the model is installed: `ollama list`
- Verify OLLAMA_HOST in `.env` file

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

### Permission errors
- Some commands require Administrator privileges
- The agent will warn you when admin access is needed

## Next Steps

Once you're comfortable with basic usage:
1. Try more complex system management tasks
2. Review the audit logs in `logs/`
3. Explore the API documentation at http://localhost:8000/docs
4. Customize prompts in `src/llm/prompts.py`

## Development Roadmap

This is Phase 1 (MVP). Future phases will add:
- Phase 2: OS Intelligence (registry scanning, leftover detection)
- Phase 3: Enhanced safety with rollback
- Phase 4: System memory and personalization
- Phase 5: Desktop UI (Electron/Tauri)

Enjoy your AI agent! 🚀
