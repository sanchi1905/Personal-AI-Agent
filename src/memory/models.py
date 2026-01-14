"""
Data Models - Pydantic models for memory storage
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class SystemState(BaseModel):
    """Represents a system state entry"""
    key: str
    value: Any
    updated_at: datetime = Field(default_factory=datetime.now)


class UserPreference(BaseModel):
    """Represents a user preference"""
    preference_key: str
    preference_value: Any
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ExecutionRecord(BaseModel):
    """Represents a command execution record"""
    command: str
    result: Dict[str, Any]
    success: bool
    executed_at: datetime = Field(default_factory=datetime.now)


class InstalledApp(BaseModel):
    """Represents an installed application"""
    app_name: str
    install_path: Optional[str] = None
    uninstall_command: Optional[str] = None
    detected_at: datetime = Field(default_factory=datetime.now)
    last_verified: datetime = Field(default_factory=datetime.now)
