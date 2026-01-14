"""
Basic tests for the AI agent
"""

import pytest
from src.executor.validators import CommandValidator


def test_command_validator_safe():
    """Test that safe commands are validated correctly"""
    command = "Get-Process"
    is_safe, warnings, risk_level = CommandValidator.validate(command)
    
    assert is_safe == True
    assert risk_level == "safe"
    assert len(warnings) == 0


def test_command_validator_dangerous():
    """Test that dangerous commands are blocked"""
    command = "Remove-Item -Recurse C:\\"
    is_safe, warnings, risk_level = CommandValidator.validate(command)
    
    assert is_safe == False
    assert risk_level == "dangerous"


def test_command_validator_caution():
    """Test that cautionary commands are flagged"""
    command = "Remove-Item test.txt"
    is_safe, warnings, risk_level = CommandValidator.validate(command)
    
    assert is_safe == True
    assert risk_level == "caution"
    assert len(warnings) > 0


def test_admin_detection():
    """Test admin privilege detection"""
    command = "Set-Service -Name wuauserv -Status Stopped"
    requires_admin = CommandValidator.requires_admin(command)
    
    assert requires_admin == True


def test_destructive_detection():
    """Test destructive operation detection"""
    command = "Remove-Item -Path test.txt"
    is_destructive = CommandValidator.is_destructive(command)
    
    assert is_destructive == True
