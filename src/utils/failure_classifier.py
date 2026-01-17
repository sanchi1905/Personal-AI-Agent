"""
Failure Classification & Recovery System

Classifies execution failures into specific types and provides
targeted recovery suggestions for each failure category.
"""

from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass
import re


class FailureType(Enum):
    """Types of execution failures"""
    PERMISSION_DENIED = "permission_denied"
    LOCKED_FILE = "locked_file"
    SERVICE_DEPENDENCY = "service_dependency"
    CORRUPT_UNINSTALL = "corrupt_uninstall"
    RESOURCE_IN_USE = "resource_in_use"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"
    INVALID_SYNTAX = "invalid_syntax"
    INSUFFICIENT_PRIVILEGES = "insufficient_privileges"
    DISK_SPACE = "disk_space"
    UNKNOWN = "unknown"


@dataclass
class FailureAnalysis:
    """Detailed failure analysis result"""
    failure_type: FailureType
    original_error: str
    diagnosis: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    is_recoverable: bool
    recovery_steps: List[str]
    prevention_tips: List[str]
    related_docs: List[str]


class FailureClassifier:
    """
    Classifies failures and provides recovery guidance.
    
    Analyzes error messages, return codes, and context to determine
    failure type and suggest appropriate recovery actions.
    """
    
    def __init__(self):
        # Error patterns for classification
        self.patterns = {
            FailureType.PERMISSION_DENIED: [
                r'access.*denied',
                r'permission.*denied',
                r'unauthorized',
                r'forbidden',
                r'not.*allowed',
                r'requires.*administrator',
            ],
            FailureType.LOCKED_FILE: [
                r'file.*in use',
                r'cannot.*access.*file',
                r'being used by another process',
                r'file.*locked',
                r'sharing violation',
            ],
            FailureType.SERVICE_DEPENDENCY: [
                r'service.*not.*running',
                r'dependency.*failed',
                r'requires.*service',
                r'dependent.*service',
                r'cannot.*start.*service',
            ],
            FailureType.CORRUPT_UNINSTALL: [
                r'uninstall.*failed',
                r'corrupt.*install',
                r'registry.*corrupt',
                r'msi.*error',
                r'package.*corrupt',
            ],
            FailureType.RESOURCE_IN_USE: [
                r'resource.*in use',
                r'port.*in use',
                r'address.*in use',
                r'already.*running',
            ],
            FailureType.NETWORK_ERROR: [
                r'network.*error',
                r'connection.*failed',
                r'timeout.*connect',
                r'host.*unreachable',
                r'dns.*failed',
            ],
            FailureType.TIMEOUT: [
                r'timeout',
                r'timed out',
                r'operation.*too.*long',
            ],
            FailureType.NOT_FOUND: [
                r'not found',
                r'does not exist',
                r'cannot find',
                r'no such',
                r'missing',
            ],
            FailureType.INVALID_SYNTAX: [
                r'syntax.*error',
                r'invalid.*command',
                r'parse.*error',
                r'unexpected.*token',
            ],
            FailureType.INSUFFICIENT_PRIVILEGES: [
                r'requires elevation',
                r'run as administrator',
                r'admin.*required',
                r'elevated.*privileges',
            ],
            FailureType.DISK_SPACE: [
                r'disk.*full',
                r'not enough space',
                r'insufficient.*space',
                r'out of.*space',
            ],
        }
    
    def classify(self, error_message: str, return_code: int = -1, 
                 operation_type: str = "") -> FailureAnalysis:
        """
        Classify a failure and provide recovery guidance.
        
        Args:
            error_message: Error message from failed operation
            return_code: Process return code
            operation_type: Type of operation that failed
        
        Returns:
            FailureAnalysis with diagnosis and recovery steps
        """
        # Detect failure type
        failure_type = self._detect_failure_type(error_message, return_code)
        
        # Get recovery information
        recovery_info = self._get_recovery_info(failure_type, operation_type)
        
        return FailureAnalysis(
            failure_type=failure_type,
            original_error=error_message,
            diagnosis=recovery_info['diagnosis'],
            severity=recovery_info['severity'],
            is_recoverable=recovery_info['recoverable'],
            recovery_steps=recovery_info['steps'],
            prevention_tips=recovery_info['prevention'],
            related_docs=recovery_info['docs']
        )
    
    def _detect_failure_type(self, error_message: str, return_code: int) -> FailureType:
        """Detect failure type from error message"""
        error_lower = error_message.lower()
        
        # Check each pattern
        for failure_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_lower, re.IGNORECASE):
                    return failure_type
        
        # Check return codes
        if return_code == 5:
            return FailureType.PERMISSION_DENIED
        elif return_code == 32:
            return FailureType.LOCKED_FILE
        elif return_code == 2:
            return FailureType.NOT_FOUND
        
        return FailureType.UNKNOWN
    
    def _get_recovery_info(self, failure_type: FailureType, 
                          operation_type: str) -> Dict:
        """Get recovery information for failure type"""
        
        recovery_guides = {
            FailureType.PERMISSION_DENIED: {
                'diagnosis': 'Access denied due to insufficient permissions',
                'severity': 'high',
                'recoverable': True,
                'steps': [
                    'Restart the application as Administrator',
                    'Right-click → "Run as Administrator"',
                    'Check file/folder permissions',
                    'Verify you have ownership of the resource',
                    'Disable antivirus temporarily if blocking access'
                ],
                'prevention': [
                    'Always run system management tools as Administrator',
                    'Set up proper file permissions ahead of time',
                    'Use User Account Control (UAC) appropriately'
                ],
                'docs': [
                    'Windows UAC documentation',
                    'File permission management guide'
                ]
            },
            
            FailureType.LOCKED_FILE: {
                'diagnosis': 'File is locked by another process',
                'severity': 'medium',
                'recoverable': True,
                'steps': [
                    'Identify which process has the file open',
                    'Use: Get-Process | Where-Object {$_.Modules.FileName -like "*filename*"}',
                    'Close the application using the file',
                    'Use LockHunter or Process Explorer to unlock',
                    'Restart in Safe Mode if needed',
                    'Reboot the system as last resort'
                ],
                'prevention': [
                    'Close all applications before system operations',
                    'Use lsof (Linux) or Process Explorer (Windows) to check locks',
                    'Schedule operations during maintenance windows'
                ],
                'docs': [
                    'Process Explorer tool',
                    'File locking troubleshooting guide'
                ]
            },
            
            FailureType.SERVICE_DEPENDENCY: {
                'diagnosis': 'Required service is not running or dependency failed',
                'severity': 'high',
                'recoverable': True,
                'steps': [
                    'Check service status: Get-Service -Name ServiceName',
                    'Identify dependencies: Get-Service -Name ServiceName | Select-Object -ExpandProperty RequiredServices',
                    'Start dependent services first',
                    'Check service configuration: sc qc ServiceName',
                    'Review Event Viewer for service errors',
                    'Restart service with: Restart-Service -Name ServiceName -Force'
                ],
                'prevention': [
                    'Always start services in dependency order',
                    'Configure automatic service startup',
                    'Monitor service health regularly'
                ],
                'docs': [
                    'Windows Services management',
                    'Service dependency resolution guide'
                ]
            },
            
            FailureType.CORRUPT_UNINSTALL: {
                'diagnosis': 'Uninstall information is corrupted or incomplete',
                'severity': 'high',
                'recoverable': True,
                'steps': [
                    'Use Windows Settings → Apps to uninstall',
                    'Run installer repair if available',
                    'Use Microsoft Fix It tool',
                    'Manually remove registry entries (backup first!)',
                    'Registry path: HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
                    'Clean up leftover files manually',
                    'Use third-party uninstaller (Revo Uninstaller, IObit)',
                    'Re-install then uninstall cleanly'
                ],
                'prevention': [
                    'Always use official uninstallers',
                    'Create restore point before installing software',
                    'Keep installation files for repair purposes'
                ],
                'docs': [
                    'Registry backup and restore guide',
                    'Manual application removal guide'
                ]
            },
            
            FailureType.RESOURCE_IN_USE: {
                'diagnosis': 'Resource (port, handle, etc.) is already in use',
                'severity': 'medium',
                'recoverable': True,
                'steps': [
                    'Identify process using resource: netstat -ano | findstr :PORT',
                    'Stop conflicting process',
                    'Change resource allocation (different port, etc.)',
                    'Restart the service/application',
                    'Check for zombie processes'
                ],
                'prevention': [
                    'Use unique ports for services',
                    'Properly close resources in applications',
                    'Monitor resource usage'
                ],
                'docs': [
                    'Port management guide',
                    'Resource conflict resolution'
                ]
            },
            
            FailureType.NETWORK_ERROR: {
                'diagnosis': 'Network connectivity or DNS resolution failed',
                'severity': 'medium',
                'recoverable': True,
                'steps': [
                    'Check network connection',
                    'Ping target host: ping hostname',
                    'Check DNS: nslookup hostname',
                    'Flush DNS cache: ipconfig /flushdns',
                    'Reset network adapter',
                    'Check firewall rules',
                    'Verify proxy settings'
                ],
                'prevention': [
                    'Ensure stable network before operations',
                    'Use connection retry logic',
                    'Implement timeout handling'
                ],
                'docs': [
                    'Network troubleshooting guide',
                    'DNS configuration guide'
                ]
            },
            
            FailureType.INSUFFICIENT_PRIVILEGES: {
                'diagnosis': 'Operation requires elevated administrator privileges',
                'severity': 'critical',
                'recoverable': True,
                'steps': [
                    'Close application',
                    'Right-click application → "Run as Administrator"',
                    'Or use: Start-Process -Verb RunAs',
                    'Verify admin rights: net user %username%',
                    'Check UAC settings if repeatedly prompted'
                ],
                'prevention': [
                    'Always run system tools as Administrator',
                    'Create shortcut with "Run as Administrator" enabled',
                    'Configure UAC appropriately'
                ],
                'docs': [
                    'UAC configuration guide',
                    'Administrator privileges guide'
                ]
            },
            
            FailureType.DISK_SPACE: {
                'diagnosis': 'Insufficient disk space for operation',
                'severity': 'critical',
                'recoverable': True,
                'steps': [
                    'Check disk space: Get-PSDrive -PSProvider FileSystem',
                    'Run Disk Cleanup: cleanmgr',
                    'Delete temporary files',
                    'Empty Recycle Bin',
                    'Uninstall unused applications',
                    'Move files to another drive',
                    'Compress large files'
                ],
                'prevention': [
                    'Monitor disk space regularly',
                    'Set up low disk space alerts',
                    'Clean up regularly with automated tasks'
                ],
                'docs': [
                    'Disk cleanup guide',
                    'Storage management best practices'
                ]
            },
            
            FailureType.NOT_FOUND: {
                'diagnosis': 'Requested file, command, or resource not found',
                'severity': 'medium',
                'recoverable': True,
                'steps': [
                    'Verify path spelling and capitalization',
                    'Check if resource exists: Test-Path "path"',
                    'Search for file: Get-ChildItem -Recurse -Filter "name"',
                    'Reinstall missing software',
                    'Restore from backup if deleted',
                    'Check environment variables for command paths'
                ],
                'prevention': [
                    'Use absolute paths instead of relative',
                    'Verify resources before operations',
                    'Maintain regular backups'
                ],
                'docs': [
                    'Path management guide',
                    'File recovery guide'
                ]
            },
            
            FailureType.TIMEOUT: {
                'diagnosis': 'Operation exceeded time limit',
                'severity': 'low',
                'recoverable': True,
                'steps': [
                    'Increase timeout value',
                    'Check if operation is stuck',
                    'Break operation into smaller chunks',
                    'Check system performance (CPU, memory)',
                    'Retry operation during off-peak hours'
                ],
                'prevention': [
                    'Set realistic timeout values',
                    'Optimize slow operations',
                    'Monitor system resources'
                ],
                'docs': [
                    'Performance optimization guide',
                    'Timeout configuration'
                ]
            },
            
            FailureType.UNKNOWN: {
                'diagnosis': 'Unable to classify error type',
                'severity': 'medium',
                'recoverable': False,
                'steps': [
                    'Review full error message',
                    'Check application logs',
                    'Search error message online',
                    'Contact support with error details',
                    'Try operation in Safe Mode',
                    'Create minimal reproduction case'
                ],
                'prevention': [
                    'Keep detailed logs of operations',
                    'Test in isolated environment first',
                    'Document custom configurations'
                ],
                'docs': [
                    'Troubleshooting methodology',
                    'Log analysis guide'
                ]
            },
        }
        
        return recovery_guides.get(failure_type, recovery_guides[FailureType.UNKNOWN])
    
    def format_analysis(self, analysis: FailureAnalysis) -> str:
        """Format failure analysis for display"""
        severity_icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        icon = severity_icons.get(analysis.severity, '⚪')
        recoverable = "✅ Recoverable" if analysis.is_recoverable else "❌ Not Recoverable"
        
        output = f"""
{icon} Failure Analysis - {analysis.failure_type.value.replace('_', ' ').title()}
Severity: {analysis.severity.upper()}
Status: {recoverable}

📋 Diagnosis:
{analysis.diagnosis}

🔧 Recovery Steps:
"""
        for i, step in enumerate(analysis.recovery_steps, 1):
            output += f"{i}. {step}\n"
        
        if analysis.prevention_tips:
            output += "\n💡 Prevention Tips:\n"
            for tip in analysis.prevention_tips:
                output += f"  • {tip}\n"
        
        if analysis.related_docs:
            output += "\n📚 Related Documentation:\n"
            for doc in analysis.related_docs:
                output += f"  • {doc}\n"
        
        return output


# Global instance
_failure_classifier = None

def get_failure_classifier() -> FailureClassifier:
    """Get or create global FailureClassifier instance"""
    global _failure_classifier
    if _failure_classifier is None:
        _failure_classifier = FailureClassifier()
    return _failure_classifier
