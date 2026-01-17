# Security & Threat Model

This document outlines the security measures, threat model, and abuse prevention strategies implemented in the Personal AI Agent.

## 🛡️ Security Principles

### 1. Local-Only Execution
**Design Goal:** All operations execute locally on the user's machine. No remote command injection possible.

**Implementation:**
- No remote API endpoints for command execution
- No network-based command reception
- All commands originate from local user input
- WebSocket connections are read-only for status updates

**Protection Against:**
- Remote code execution (RCE) attacks
- Man-in-the-middle command injection
- Unauthorized remote access
- Network-based exploitation

### 2. Explicit User Confirmation
**Design Goal:** No silent execution of system-modifying commands.

**Implementation:**
- Every command requires explicit user approval
- Clear preview of actions before execution
- Dry-run mode available for testing
- Confirmation modals in UI show:
  - Exact command to be executed
  - Predicted changes
  - Safety risk level
  - Reversibility status

**Protection Against:**
- Accidental destructive operations
- Social engineering attacks
- Malicious prompt injection
- Unintended automation

### 3. Comprehensive Audit Logging
**Design Goal:** Full transparency and traceability of all operations.

**Implementation:**
- Every command logged with timestamp
- Before/after state tracking
- Execution results captured
- Change history maintained
- Logs stored in `/logs` directory
- JSON format for easy parsing

**Log Contents:**
```json
{
  "timestamp": "2026-01-18T10:30:00",
  "command": "Get-Service",
  "operation_type": "service_query",
  "privilege_level": "user",
  "result": {
    "success": true,
    "return_code": 0,
    "execution_time": 1.2
  },
  "changes": []
}
```

**Protection Against:**
- Untracked system modifications
- Forensic investigation gaps
- Compliance violations
- Accountability issues

### 4. Privilege Escalation Protection
**Design Goal:** Prevent unauthorized privilege escalation.

**Implementation:**
- Explicit admin privilege detection
- Graceful degradation when privileges insufficient
- Clear messaging about permission requirements
- No automatic privilege escalation
- Separate admin-required operations flagged

**Protection Against:**
- UAC bypass attempts
- Privilege escalation exploits
- Unauthorized system access
- Silent elevation

### 5. Command Sandboxing
**Design Goal:** Protect critical system paths and prevent destructive operations.

**Implementation:**
```python
PROTECTED_PATHS = [
    "C:\\Windows\\System32",
    "C:\\Windows\\SysWOW64",
    "C:\\Windows\\Boot",
    "C:\\Windows\\WinSxS"
]

DANGEROUS_COMMANDS = [
    "format",
    "rd /s",
    "del /s",
    "diskpart",
    "bcdedit"
]
```

- Path allowlist/denylist validation
- Dangerous command pattern detection
- Critical file protection
- System integrity verification

**Protection Against:**
- Accidental system corruption
- Malicious command injection
- Critical file deletion
- Bootloader modification

## 🚨 Threat Model

### Threats We Protect Against

#### 1. Malicious Prompt Injection
**Threat:** Attacker tricks LLM into generating malicious commands.

**Mitigation:**
- User confirmation required for all executions
- Command preview with safety warnings
- Dangerous pattern detection
- Sandboxing of critical operations

**Risk Level:** MEDIUM (user must still approve)

#### 2. Local Malware Abuse
**Threat:** Local malware attempts to use agent for privilege escalation.

**Mitigation:**
- No remote API exposure
- Requires interactive user session
- Audit logs track all operations
- Privilege checks prevent unauthorized elevation

**Risk Level:** LOW (requires existing local access)

#### 3. Accidental Data Loss
**Threat:** User accidentally approves destructive operation.

**Mitigation:**
- Automatic backups before destructive ops
- Rollback scripts generated
- Dry-run mode for testing
- Clear warnings for high-risk operations
- Change tracking with undo capability

**Risk Level:** LOW (multiple safety layers)

#### 4. Social Engineering
**Threat:** Attacker convinces user to execute malicious commands.

**Mitigation:**
- Clear command preview
- Risk level indicators
- Suggestion of safer alternatives
- Educational warnings for dangerous patterns

**Risk Level:** MEDIUM (depends on user awareness)

#### 5. Configuration Tampering
**Threat:** Attacker modifies agent configuration to bypass safety.

**Mitigation:**
- Configuration files require admin access
- Validation of configuration values
- Audit logging of configuration changes
- Sandboxing cannot be disabled for critical paths

**Risk Level:** LOW (requires admin access)

### Threats Out of Scope

#### 1. Kernel-Level Attacks
- Agent operates in user-space only
- No kernel module interaction
- No bootloader modification

#### 2. Hardware-Level Attacks
- No BIOS/UEFI modification
- No firmware updates
- No direct hardware access

#### 3. Network-Based RCE
- No remote command execution APIs
- No network-based command reception
- Local-only architecture

## 🔐 Abuse Prevention Mechanisms

### 1. Command Validation Pipeline

```
User Input
    ↓
LLM Intent Extraction
    ↓
Safety Validator (filters malicious patterns)
    ↓
Privilege Checker (ensures sufficient permissions)
    ↓
Sandbox Validator (protects critical paths)
    ↓
User Confirmation (explicit approval required)
    ↓
Backup Creation (if destructive)
    ↓
Execution
    ↓
Audit Logging
```

### 2. Rate Limiting
- No automated batch execution without user approval
- Each command requires individual confirmation
- Prevents rapid-fire malicious operations

### 3. Rollback Capability
- Every destructive operation generates rollback script
- Backups stored in `/backups` directory
- Windows restore point integration
- Change tracking for undo

### 4. Educational Warnings

For high-risk operations, display:
```
⚠️ WARNING: HIGH RISK OPERATION

This command will:
  • Delete files permanently
  • Modify system registry
  • Stop critical services

Reversibility: PARTIAL
Backup: ✅ Automatic backup created
Recommendation: Run in dry-run mode first

Are you sure you want to proceed?
```

## 📋 Security Checklist

### Deployment Security

- [ ] Review and configure protected paths in `safety/sandbox.py`
- [ ] Set appropriate permissions on log directory
- [ ] Enable automatic backups in configuration
- [ ] Configure Windows restore point creation
- [ ] Review audit log retention policy
- [ ] Test rollback procedures
- [ ] Verify privilege detection works correctly
- [ ] Enable dry-run mode for testing

### Operational Security

- [ ] Regularly review audit logs
- [ ] Monitor for suspicious command patterns
- [ ] Keep backups of critical data
- [ ] Test restore procedures periodically
- [ ] Update dangerous command patterns
- [ ] Review and update protected paths list
- [ ] Validate configuration integrity

### Development Security

- [ ] Code review for new command types
- [ ] Security testing for privilege escalation
- [ ] Validate input sanitization
- [ ] Test sandbox bypass attempts
- [ ] Verify audit logging completeness
- [ ] Test failure recovery paths

## 🔍 Security Monitoring

### What to Monitor

1. **Audit Logs**
   - Location: `/logs/*.log`
   - Review frequency: Daily for production systems
   - Look for: Failed privilege checks, sandbox violations, unusual patterns

2. **Failed Operations**
   - Location: Execution history in logs
   - Alert on: Multiple privilege denied errors, sandbox violations
   - Investigate: Patterns of dangerous command attempts

3. **Configuration Changes**
   - Location: `/config/*.json`
   - Monitor: File modification timestamps
   - Verify: Changes are authorized

4. **Backup Integrity**
   - Location: `/backups/*`
   - Verify: Backups are being created
   - Test: Periodic restore testing

## 📞 Incident Response

### If Suspicious Activity Detected

1. **Immediate Actions**
   - Halt agent execution
   - Review recent audit logs
   - Check for unauthorized configuration changes
   - Verify system integrity

2. **Investigation**
   - Identify the source of suspicious commands
   - Review command history
   - Check for privilege escalation attempts
   - Examine backup and rollback history

3. **Recovery**
   - Restore from backups if needed
   - Roll back unauthorized changes
   - Review and update security policies
   - Enhance monitoring if needed

## 🔒 Privacy Considerations

### Data Collection
- **Local Only:** All data stays on user's machine
- **No Telemetry:** No usage data sent to external servers
- **No Cloud Sync:** Logs and history stored locally

### LLM Privacy
- **Local Models (Ollama):** Recommended for sensitive environments
- **API Models (OpenAI):** Commands sent to API for processing
  - Review OpenAI's data usage policy
  - Consider using Azure OpenAI for enterprise compliance
  - Enable opt-out of data training if using OpenAI

### Sensitive Data
- Audit logs may contain sensitive system information
- Secure log directory with appropriate permissions
- Consider encrypting logs for highly sensitive environments
- Implement log rotation and secure deletion

## ✅ Security Best Practices

### For Users

1. **Always review commands before approving**
2. **Use dry-run mode for unfamiliar operations**
3. **Keep backups enabled**
4. **Review audit logs periodically**
5. **Run with least necessary privileges**
6. **Keep agent software updated**

### For Administrators

1. **Configure protected paths for your environment**
2. **Set up automated backup verification**
3. **Implement log monitoring and alerting**
4. **Regular security audits**
5. **Test incident response procedures**
6. **Document custom security policies**

### For Developers

1. **Follow secure coding practices**
2. **Validate all inputs**
3. **Maintain comprehensive audit logging**
4. **Test security controls regularly**
5. **Keep dependencies updated**
6. **Document security assumptions**

## 📚 Related Documentation

- [README.md](../README.md) - General project overview
- [src/safety/](../src/safety/) - Safety validation implementation
- [src/utils/privilege_manager.py](../src/utils/privilege_manager.py) - Privilege detection
- [src/utils/failure_classifier.py](../src/utils/failure_classifier.py) - Error handling
- [SCOPE_BOUNDARIES.md](./SCOPE_BOUNDARIES.md) - What the agent will never do

## 🆘 Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. Contact the maintainers privately
3. Provide detailed reproduction steps
4. Allow reasonable time for fix before disclosure
5. Follow responsible disclosure practices

---

**Last Updated:** January 18, 2026
**Version:** 1.0
**Status:** Production Ready
