"""
FastAPI Backend for Personal AI Agent Desktop UI
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime
import logging

# Import agent modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm.client import LLMClient
from src.executor.command_executor import CommandExecutor
from src.safety.confirmation import ConfirmationHandler
from src.safety.audit import AuditLogger
from src.memory.database import MemoryDatabase
from src.os_intelligence.registry_scanner import RegistryScanner
from src.os_intelligence.app_analyzer import AppAnalyzer
from src.os_intelligence.service_inspector import ServiceInspector
from src.safety_advanced.backup_manager import BackupManager
from src.safety_advanced.rollback_engine import RollbackEngine
from src.safety_advanced.dry_run import DryRunSimulator
from src.safety_advanced.change_tracker import ChangeTracker
from src.safety_advanced.sandbox import CommandSandbox
from src.memory_advanced.user_preferences import UserPreferences
from src.memory_advanced.pattern_learner import PatternLearner
from src.memory_advanced.smart_suggester import SmartSuggester
from src.memory_advanced.context_manager import SystemContextManager
from src.services.voice_service import ElevenLabsVoiceService

logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Personal AI Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
class AgentInstance:
    def __init__(self):
        self.llm = LLMClient()
        self.executor = CommandExecutor()
        self.audit = AuditLogger()
        self.db = MemoryDatabase()
        
        # OS Intelligence
        self.registry_scanner = RegistryScanner()
        self.app_analyzer = AppAnalyzer()
        self.service_inspector = ServiceInspector()
        
        # Safety
        self.backup_manager = BackupManager()
        self.rollback_engine = RollbackEngine()
        self.dry_run = DryRunSimulator()
        self.change_tracker = ChangeTracker()
        self.sandbox = CommandSandbox()
        
        # Memory & Learning
        self.preferences = UserPreferences()
        self.pattern_learner = PatternLearner()
        self.suggester = SmartSuggester(self.pattern_learner, self.preferences)
        self.context_manager = SystemContextManager()
        
        # Voice Integration
        self.voice_service = ElevenLabsVoiceService()
        
        self.command_history = []
        self.initialized = False
    
    async def initialize(self):
        if not self.initialized:
            await self.db.initialize()
            self.initialized = True

agent = AgentInstance()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = "general"

class CommandRequest(BaseModel):
    command: str
    dry_run: bool = False

class CommandResponse(BaseModel):
    command: str
    explanation: str
    risks: List[str]
    requires_admin: bool
    will_execute: bool

class ExecutionResult(BaseModel):
    success: bool
    output: str
    execution_time: float

class SystemStatus(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    health_status: str
    recommendations: List[str]

# API Routes

@app.on_event("startup")
async def startup():
    """Initialize agent on startup"""
    await agent.initialize()
    logger.info("Personal AI Agent API started")

@app.get("/")
async def root():
    """Health check"""
    return {"status": "online", "service": "Personal AI Agent"}

@app.post("/api/chat")
async def chat(message: ChatMessage) -> Dict[str, Any]:
    """
    Process chat message and generate command
    """
    try:
        # Capture system state
        agent.context_manager.capture_state()
        
        # Infer context
        context = agent.context_manager.infer_context(message.message, agent.command_history)
        
        # Get suggestions if enabled
        suggestions = []
        if agent.preferences.get('smart_suggestions', True) and agent.command_history:
            predictions = agent.suggester.suggest_after_command(agent.command_history[-1])
            suggestions = [{"command": cmd, "confidence": conf} for cmd, conf in predictions[:3]]
        
        # Generate command
        command = await agent.llm.generate_command(message.message)
        
        if not command:
            return {
                "success": False,
                "error": "Could not generate command",
                "suggestions": suggestions
            }
        
        # Parse command (handle dict or string response)
        if isinstance(command, dict):
            cmd_text = command.get('command', '')
            explanation = command.get('explanation', '')
            risks = command.get('risks', [])
            requires_admin = command.get('requires_admin', False)
        else:
            cmd_text = command
            explanation = "Command generated from your request"
            risks = []
            requires_admin = False
        
        # Safety validation
        is_safe, warnings = agent.sandbox.validate_command(cmd_text)
        
        # Get optimization suggestions
        optimizations = agent.suggester.suggest_optimizations(cmd_text)
        
        return {
            "success": True,
            "command": cmd_text,
            "explanation": explanation,
            "risks": risks + warnings,
            "is_safe": is_safe,
            "requires_admin": requires_admin,
            "suggestions": suggestions,
            "optimizations": optimizations,
            "context": context
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/execute")
async def execute_command(request: CommandRequest) -> Dict[str, Any]:
    """
    Execute or simulate command
    """
    try:
        context = agent.context_manager.get_context()
        
        # Broadcast execution start
        await manager.broadcast({
            "type": "execution_start",
            "command": request.command,
            "dry_run": request.dry_run
        })
        
        if request.dry_run:
            # Simulate
            result = await agent.dry_run.simulate_command(request.command, context)
            
            response = {
                "success": True,
                "dry_run": True,
                "will_execute": result.will_execute,
                "risk_level": result.risk_level,
                "predicted_changes": result.predicted_changes,
                "warnings": result.warnings,
                "estimated_time": result.estimated_time
            }
        else:
            # Backup if needed
            auto_backup = agent.preferences.get('auto_backup', True)
            backup_id = None
            
            if auto_backup:
                is_safe, _ = agent.sandbox.validate_command(request.command)
                if not is_safe:
                    backup_id = agent.backup_manager.create_backup(f"Pre-execution: {request.command[:50]}")
            
            # Execute
            result = await agent.executor.execute(request.command)
            
            # Track changes
            if result.success:
                agent.change_tracker.track_command(request.command)
            
            # Log execution
            await agent.audit.log_execution(request.command, request.command, result)
            
            # Learn from execution
            if agent.preferences.get('learn_patterns', True):
                agent.pattern_learner.record_command(
                    request.command,
                    context,
                    result.success,
                    result.execution_time
                )
                
                if agent.command_history:
                    agent.pattern_learner.record_sequence(agent.command_history[-1], request.command)
            
            # Add to history
            agent.command_history.append(request.command)
            
            response = {
                "success": result.success,
                "dry_run": False,
                "output": result.output,
                "execution_time": result.execution_time,
                "backup_id": backup_id
            }
        
        # Broadcast execution complete
        await manager.broadcast({
            "type": "execution_complete",
            "result": response
        })
        
        return response
    
    except Exception as e:
        logger.error(f"Execution error: {e}")
        await manager.broadcast({
            "type": "execution_error",
            "error": str(e)
        })
        return {"success": False, "error": str(e)}

@app.get("/api/system/status")
async def get_system_status() -> SystemStatus:
    """Get current system status"""
    try:
        health = agent.context_manager.get_system_health()
        recommendations = agent.context_manager.get_resource_recommendations()
        
        return SystemStatus(
            cpu_percent=health['cpu']['percent'],
            memory_percent=health['memory']['percent'],
            disk_percent=health['disk']['percent'],
            health_status=health['overall_status'],
            recommendations=recommendations
        )
    except Exception as e:
        logger.error(f"System status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/apps")
async def get_installed_apps():
    """Get list of installed applications"""
    try:
        apps = agent.registry_scanner.scan_installed_apps()
        return {"apps": apps, "count": len(apps)}
    except Exception as e:
        logger.error(f"Apps error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/services")
async def get_services():
    """Get list of Windows services"""
    try:
        services = agent.service_inspector.list_services()
        return {"services": services, "count": len(services)}
    except Exception as e:
        logger.error(f"Services error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backups")
async def get_backups():
    """Get list of backups"""
    try:
        backups = agent.backup_manager.list_backups()
        return {
            "backups": [
                {
                    "id": b.id,
                    "created_at": b.created_at,
                    "description": b.description,
                    "files_count": len(b.files),
                    "total_size": b.total_size
                }
                for b in backups
            ]
        }
    except Exception as e:
        logger.error(f"Backups error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/changes")
async def get_changes():
    """Get recent system changes"""
    try:
        changes = agent.change_tracker.get_recent_changes(limit=50)
        return {
            "changes": [
                {
                    "change_type": c.change_type,
                    "path": c.path,
                    "timestamp": c.timestamp,
                    "command": c.command
                }
                for c in changes
            ]
        }
    except Exception as e:
        logger.error(f"Changes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_learning_stats():
    """Get learning statistics"""
    try:
        stats = agent.pattern_learner.get_statistics()
        frequent = agent.pattern_learner.get_frequent_commands(5)
        
        return {
            "stats": stats,
            "frequent_commands": [
                {
                    "command": p.command_template,
                    "frequency": p.frequency,
                    "success_rate": p.success_rate
                }
                for p in frequent
            ]
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/preferences")
async def get_preferences():
    """Get user preferences"""
    try:
        categories = agent.preferences.get_categories()
        prefs = {}
        for category in categories:
            prefs[category] = agent.preferences.get_by_category(category)
        return {"preferences": prefs}
    except Exception as e:
        logger.error(f"Preferences error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preferences")
async def update_preference(key: str, value: Any):
    """Update a preference"""
    try:
        agent.preferences.set(key, value)
        return {"success": True, "key": key, "value": value}
    except Exception as e:
        logger.error(f"Update preference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Voice API Routes

class VoiceRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    model_id: Optional[str] = "eleven_monolingual_v1"
    stability: Optional[float] = 0.5
    similarity_boost: Optional[float] = 0.75

@app.post("/api/voice/tts")
async def text_to_speech(request: VoiceRequest):
    """
    Convert text to speech using ElevenLabs
    """
    try:
        from fastapi.responses import StreamingResponse
        import io
        
        # Generate speech
        audio_bytes = await asyncio.to_thread(
            agent.voice_service.text_to_speech,
            request.text,
            voice_id=request.voice_id,
            model_id=request.model_id,
            stability=request.stability,
            similarity_boost=request.similarity_boost
        )
        
        # Return audio stream
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voice/voices")
async def get_voices():
    """
    Get available ElevenLabs voices
    """
    try:
        voices = await asyncio.to_thread(agent.voice_service.get_available_voices)
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Get voices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send periodic system updates
            await asyncio.sleep(5)
            
            # Send system status update
            health = agent.context_manager.get_system_health()
            await websocket.send_json({
                "type": "system_update",
                "data": {
                    "cpu": health['cpu']['percent'],
                    "memory": health['memory']['percent'],
                    "disk": health['disk']['percent'],
                    "status": health['overall_status']
                }
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
