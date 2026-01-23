"""
System Context Manager - Tracks and maintains system state context
"""

import logging
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """Snapshot of system state"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    running_processes: int
    active_services: int
    network_connections: int


class SystemContextManager:
    """Manages system context and state awareness"""
    
    def __init__(self):
        """Initialize system context manager"""
        self.current_context = 'general'
        self.context_history: List[str] = []
        self.state_snapshots: List[SystemState] = []
        self.max_snapshots = 100
    
    def capture_state(self) -> SystemState:
        """
        Capture current system state
        
        Returns:
            SystemState snapshot
        """
        try:
            import platform
            disk_path = 'C:\\' if platform.system() == 'Windows' else '/'
            
            state = SystemState(
                timestamp=datetime.now().isoformat(),
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=psutil.virtual_memory().percent,
                disk_usage_percent=psutil.disk_usage(disk_path).percent,
                running_processes=len(psutil.pids()),
                active_services=0,  # Would need Windows-specific API
                network_connections=len(psutil.net_connections())
            )
            
            # Store snapshot
            self.state_snapshots.append(state)
            
            # Keep only recent snapshots
            if len(self.state_snapshots) > self.max_snapshots:
                self.state_snapshots = self.state_snapshots[-self.max_snapshots:]
            
            return state
        
        except Exception as e:
            logger.error(f"Failed to capture system state: {e}")
            return None
    
    def infer_context(self, user_input: str, last_commands: List[str] = None) -> str:
        """
        Infer current context from user input and history
        
        Args:
            user_input: User's current input
            last_commands: Recent command history
            
        Returns:
            Inferred context
        """
        input_lower = user_input.lower()
        
        # Context keywords
        contexts = {
            'uninstall': ['uninstall', 'remove app', 'delete app'],
            'service_management': ['service', 'start service', 'stop service'],
            'system_monitoring': ['cpu', 'memory', 'disk', 'performance'],
            'file_management': ['file', 'folder', 'directory', 'copy', 'move'],
            'network': ['network', 'connection', 'ip', 'ping'],
            'troubleshooting': ['error', 'fix', 'problem', 'issue', 'debug'],
            'backup_restore': ['backup', 'restore', 'rollback'],
        }
        
        # Check for context keywords
        for context, keywords in contexts.items():
            if any(keyword in input_lower for keyword in keywords):
                self.set_context(context)
                return context
        
        # Check last commands for context continuity
        if last_commands:
            last_cmd = last_commands[-1].lower()
            for context, keywords in contexts.items():
                if any(keyword in last_cmd for keyword in keywords):
                    return context
        
        return 'general'
    
    def set_context(self, context: str):
        """
        Set current context
        
        Args:
            context: Context name
        """
        if context != self.current_context:
            self.context_history.append(self.current_context)
            self.current_context = context
            logger.info(f"Context changed to: {context}")
    
    def get_context(self) -> str:
        """Get current context"""
        return self.current_context
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get current system health summary
        
        Returns:
            System health metrics
        """
        try:
            import platform
            
            cpu = psutil.cpu_percent(interval=0.1)  # Reduced from 1s to 0.1s for faster response
            memory = psutil.virtual_memory()
            
            # Use platform-appropriate disk path
            disk_path = 'C:\\' if platform.system() == 'Windows' else '/'
            disk = psutil.disk_usage(disk_path)
            
            health = {
                'cpu': {
                    'percent': cpu,
                    'status': 'healthy' if cpu < 80 else 'warning' if cpu < 95 else 'critical'
                },
                'memory': {
                    'percent': memory.percent,
                    'available_gb': memory.available / (1024**3),
                    'status': 'healthy' if memory.percent < 80 else 'warning' if memory.percent < 95 else 'critical'
                },
                'disk': {
                    'percent': disk.percent,
                    'free_gb': disk.free / (1024**3),
                    'status': 'healthy' if disk.percent < 80 else 'warning' if disk.percent < 95 else 'critical'
                },
                'overall_status': 'healthy'
            }
            
            # Determine overall status
            statuses = [health['cpu']['status'], health['memory']['status'], health['disk']['status']]
            if 'critical' in statuses:
                health['overall_status'] = 'critical'
            elif 'warning' in statuses:
                health['overall_status'] = 'warning'
            
            return health
        
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            # Return safe default structure
            return {
                'cpu': {'percent': 0.0, 'status': 'unknown'},
                'memory': {'percent': 0.0, 'available_gb': 0.0, 'status': 'unknown'},
                'disk': {'percent': 0.0, 'free_gb': 0.0, 'status': 'unknown'},
                'overall_status': 'unknown'
            }
    
    def get_resource_recommendations(self) -> List[str]:
        """
        Get recommendations based on resource usage
        
        Returns:
            List of recommendations
        """
        recommendations = []
        health = self.get_system_health()
        
        if health['memory']['status'] in ['warning', 'critical']:
            recommendations.append(
                f"⚠️ High memory usage ({health['memory']['percent']:.1f}%). "
                "Consider closing unused applications."
            )
        
        if health['cpu']['status'] in ['warning', 'critical']:
            recommendations.append(
                f"⚠️ High CPU usage ({health['cpu']['percent']:.1f}%). "
                "Check for resource-intensive processes."
            )
        
        if health['disk']['status'] in ['warning', 'critical']:
            recommendations.append(
                f"⚠️ Low disk space ({health['disk']['free_gb']:.1f} GB free). "
                "Consider cleaning up old files or backups."
            )
        
        return recommendations
    
    def analyze_trends(self) -> Dict[str, Any]:
        """
        Analyze system state trends
        
        Returns:
            Trend analysis
        """
        if len(self.state_snapshots) < 10:
            return {'status': 'insufficient_data'}
        
        recent = self.state_snapshots[-10:]
        
        avg_cpu = sum(s.cpu_percent for s in recent) / len(recent)
        avg_memory = sum(s.memory_percent for s in recent) / len(recent)
        
        # Check for increasing trends
        cpu_trend = 'increasing' if recent[-1].cpu_percent > avg_cpu + 10 else 'stable'
        memory_trend = 'increasing' if recent[-1].memory_percent > avg_memory + 10 else 'stable'
        
        return {
            'status': 'analyzed',
            'cpu_trend': cpu_trend,
            'memory_trend': memory_trend,
            'avg_cpu': avg_cpu,
            'avg_memory': avg_memory
        }
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get information about current context"""
        return {
            'current_context': self.current_context,
            'context_history': self.context_history[-5:],
            'snapshots_count': len(self.state_snapshots),
            'system_health': self.get_system_health()['overall_status']
        }
