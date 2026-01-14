"""
OS Intelligence Module - System-aware capabilities for Windows
"""

from .app_analyzer import AppAnalyzer
from .leftover_detector import LeftoverDetector
from .service_inspector import ServiceInspector
from .registry_scanner import RegistryScanner
from .smart_uninstaller import SmartUninstaller

__all__ = ["AppAnalyzer", "LeftoverDetector", "ServiceInspector", "RegistryScanner", "SmartUninstaller"]
