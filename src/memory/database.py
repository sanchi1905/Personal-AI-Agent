"""
Memory Database - SQLite storage for agent memory
"""

import aiosqlite
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MemoryDatabase:
    """Manages persistent storage of system state and user preferences"""
    
    def __init__(self, db_path: str = "./data/agent_memory.db"):
        """
        Initialize memory database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Create database tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            # System state table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # User preferences table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE NOT NULL,
                    preference_value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Execution history table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    result TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    executed_at TEXT NOT NULL
                )
            """)
            
            # Installed apps cache
            await db.execute("""
                CREATE TABLE IF NOT EXISTS installed_apps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    install_path TEXT,
                    uninstall_command TEXT,
                    detected_at TEXT NOT NULL,
                    last_verified TEXT NOT NULL
                )
            """)
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def set_state(self, key: str, value: Any):
        """
        Set a system state value
        
        Args:
            key: State key
            value: State value (will be JSON serialized)
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO system_state (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), datetime.now().isoformat()))
            await db.commit()
    
    async def get_state(self, key: str) -> Optional[Any]:
        """
        Get a system state value
        
        Args:
            key: State key
            
        Returns:
            State value or None
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT value FROM system_state WHERE key = ?",
                (key,)
            )
            row = await cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            return None
    
    async def set_preference(self, key: str, value: Any):
        """
        Set a user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO user_preferences 
                (preference_key, preference_value, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (key, json.dumps(value), now, now))
            await db.commit()
    
    async def get_preference(self, key: str) -> Optional[Any]:
        """
        Get a user preference
        
        Args:
            key: Preference key
            
        Returns:
            Preference value or None
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT preference_value FROM user_preferences WHERE preference_key = ?",
                (key,)
            )
            row = await cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            return None
    
    async def log_execution(self, command: str, result: Dict[str, Any], success: bool):
        """
        Log a command execution
        
        Args:
            command: Executed command
            result: Execution result
            success: Whether execution succeeded
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO execution_history (command, result, success, executed_at)
                VALUES (?, ?, ?, ?)
            """, (command, json.dumps(result), 1 if success else 0, datetime.now().isoformat()))
            await db.commit()
    
    async def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent execution history
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of execution records
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT command, result, success, executed_at
                FROM execution_history
                ORDER BY executed_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = await cursor.fetchall()
            
            return [
                {
                    "command": row[0],
                    "result": json.loads(row[1]),
                    "success": bool(row[2]),
                    "executed_at": row[3]
                }
                for row in rows
            ]
