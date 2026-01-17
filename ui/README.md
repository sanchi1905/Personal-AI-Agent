# Personal AI Agent - Desktop UI

Modern desktop interface for the Personal AI Agent built with React and Vite.

## 🎨 Features

- **ChatGPT-like Interface** - Conversational UI for natural interaction
- **Real-time System Monitoring** - Live CPU, memory, and disk usage
- **Command Preview** - See exactly what will execute before confirming
- **Interactive Confirmations** - Visual approve/deny dialogs
- **WebSocket Updates** - Real-time status and execution feedback
- **Safety Indicators** - Visual risk assessment for each command
- **Dark Mode UI** - Professional, eye-friendly design

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+ with backend running
- Ollama with llama3

### Installation

1. Install dependencies:
```bash
cd ui
npm install
```

2. Start the backend API (in a separate terminal):
```bash
cd ..
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

3. Start the frontend dev server:
```bash
npm run dev
```

4. Open browser to http://localhost:3000

## 📁 Project Structure

```
ui/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx      # Main chat UI
│   │   ├── CommandPreview.jsx     # Command details panel
│   │   ├── ConfirmationModal.jsx  # Execution confirmation
│   │   ├── SystemStatus.jsx       # System health dashboard
│   │   └── Sidebar.jsx            # Navigation sidebar
│   ├── services/
│   │   └── api.js                 # API client
│   ├── hooks/
│   │   └── useWebSocket.js        # WebSocket hook
│   ├── App.jsx                    # Main app component
│   └── main.jsx                   # Entry point
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🔧 Configuration

The UI automatically connects to:
- API: `http://localhost:8000/api`
- WebSocket: `ws://localhost:8000/ws`

To change these, set environment variables:
```bash
VITE_API_URL=http://your-api-url
VITE_WS_URL=ws://your-api-url/ws
```

## 🎯 Usage

1. **Type a request** in the chat input (e.g., "list running processes")
2. **Review the command** in the right panel
3. **Check warnings** and safety indicators
4. **Click "Review & Execute"** to open confirmation modal
5. **Choose action**:
   - **Dry Run** - Simulate without executing
   - **Execute** - Run the command
   - **Cancel** - Abort operation

## 🛡️ Safety Features

- **Visual Risk Indicators** - Color-coded safety status
- **Warning Display** - All potential risks shown upfront
- **Dry Run Mode** - Test commands without execution
- **Confirmation Required** - No silent execution
- **Execution Logging** - Full audit trail

## 🌐 API Endpoints

- `POST /api/chat` - Process chat messages
- `POST /api/execute` - Execute commands
- `GET /api/system/status` - Get system health
- `GET /api/apps` - List installed apps
- `GET /api/services` - List Windows services
- `GET /api/backups` - List backups
- `GET /api/changes` - Get recent changes
- `GET /api/stats` - Learning statistics
- `GET /api/preferences` - User preferences
- `WS /ws` - WebSocket for real-time updates

## 🎨 Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Headless UI** - Accessible components
- **Heroicons** - Icon library
- **Axios** - HTTP client
- **WebSocket API** - Real-time communication

## 📦 Build for Production

```bash
npm run build
```

The optimized build will be in `dist/` directory.

## 🔍 Development

- `npm run dev` - Start dev server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🐛 Troubleshooting

**UI not connecting to backend?**
- Ensure backend is running on port 8000
- Check CORS settings in `src/api/main.py`
- Verify WebSocket connection in browser console

**Commands not executing?**
- Check if Ollama is running
- Verify Python backend logs
- Ensure all dependencies are installed

## 📄 License

Part of the Personal AI Agent project
