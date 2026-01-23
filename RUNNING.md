# How to Run the Personal AI Agent

## Important: Backend Must Run in Separate Window

The backend server **MUST** be started in a separate PowerShell window to avoid shutdown issues.

## Option 1: Use the Startup Script (Recommended)

```powershell
.\start.ps1
```

This will automatically:
1. Clean up old processes
2. Start backend in a new window
3. Start frontend in the current window

## Option 2: Manual Start

### Step 1: Start Backend (in NEW PowerShell window)

```powershell
cd "c:\Users\Asus\Downloads\Personal AI Agent\personal-ai-agent"
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

**Important:** Do NOT run backend in VS Code terminal - it will shut down when other commands run.

### Step 2: Start Frontend (in separate window)

```powershell
cd "c:\Users\Asus\Downloads\Personal AI Agent\personal-ai-agent\ui"
npm run dev
```

## Verifying Services

Backend: http://localhost:8000
Frontend: http://localhost:3000

### Test Backend
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
```

Should return: `{"status":"online","service":"Personal AI Agent"}`

## Recent Fixes

1. **Fixed disk path bug** - Changed `psutil.disk_usage('/')` to use `'C:\\'` on Windows
2. **Fixed startup isolation** - Backend now runs in separate window to avoid signal interference

## Troubleshooting

- If backend shuts down immediately: Make sure it's running in a **separate PowerShell window**
- If voice input not working: Check microphone permissions in browser
- If commands not executing: Check backend logs in the separate window
