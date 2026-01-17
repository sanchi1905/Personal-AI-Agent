"""
Decision & Orchestration Engine

Coordinates the flow from user intent → safety validation → 
command planning → execution with explicit decision tracking.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

from utils.privilege_manager import get_privilege_manager, PrivilegeCheck
from utils.failure_classifier import get_failure_classifier

logger = logging.getLogger(__name__)


class DecisionStage(Enum):
    """Stages in the decision pipeline"""
    INTENT_EXTRACTION = "intent_extraction"
    SAFETY_VALIDATION = "safety_validation"
    PRIVILEGE_CHECK = "privilege_check"
    PLANNING = "planning"
    USER_CONFIRMATION = "user_confirmation"
    BACKUP_CREATION = "backup_creation"
    EXECUTION = "execution"
    LOGGING = "logging"
    COMPLETED = "completed"


class DecisionOutcome(Enum):
    """Possible outcomes at each stage"""
    APPROVED = "approved"
    DENIED = "denied"
    NEEDS_REVIEW = "needs_review"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class DecisionPoint:
    """Individual decision at a pipeline stage"""
    stage: DecisionStage
    timestamp: str
    outcome: DecisionOutcome
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """Complete plan for executing an operation"""
    operation_type: str
    operation_name: str
    commands: List[str]
    predicted_changes: List[Dict[str, Any]]
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    is_reversible: bool
    requires_backup: bool
    requires_admin: bool
    estimated_duration: float
    dependencies: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)


@dataclass
class OrchestratedDecision:
    """Complete decision trail for an operation"""
    request_id: str
    user_intent: str
    timestamp_start: str
    timestamp_end: Optional[str] = None
    current_stage: DecisionStage = DecisionStage.INTENT_EXTRACTION
    final_outcome: Optional[DecisionOutcome] = None
    decision_trail: List[DecisionPoint] = field(default_factory=list)
    execution_plan: Optional[ExecutionPlan] = None
    execution_result: Optional[Dict] = None
    total_duration: Optional[float] = None


class DecisionOrchestrator:
    """
    Orchestrates the complete decision and execution pipeline.
    
    Pipeline:
    1. Intent Extraction (from LLM)
    2. Safety Validation (dangerous patterns, protected paths)
    3. Privilege Check (admin requirements)
    4. Planning (command generation, change prediction)
    5. User Confirmation (explicit approval)
    6. Backup Creation (if needed)
    7. Execution (actual command run)
    8. Logging (audit trail)
    """
    
    def __init__(self):
        self.privilege_manager = get_privilege_manager()
        self.failure_classifier = get_failure_classifier()
        self.decision_history: List[OrchestratedDecision] = []
        self.request_counter = 0
    
    def create_decision(self, user_intent: str) -> OrchestratedDecision:
        """
        Create a new orchestrated decision flow.
        
        Args:
            user_intent: Natural language user request
        
        Returns:
            OrchestratedDecision object tracking the entire flow
        """
        self.request_counter += 1
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{self.request_counter:04d}"
        
        decision = OrchestratedDecision(
            request_id=request_id,
            user_intent=user_intent,
            timestamp_start=datetime.now().isoformat()
        )
        
        self.decision_history.append(decision)
        logger.info(f"Created decision flow: {request_id}")
        
        return decision
    
    def record_decision(self, decision: OrchestratedDecision, 
                       stage: DecisionStage,
                       outcome: DecisionOutcome,
                       reasoning: str,
                       **kwargs) -> None:
        """
        Record a decision point in the orchestration trail.
        
        Args:
            decision: The orchestrated decision being tracked
            stage: Current pipeline stage
            outcome: Decision outcome at this stage
            reasoning: Explanation for the decision
            **kwargs: Additional metadata
        """
        decision_point = DecisionPoint(
            stage=stage,
            timestamp=datetime.now().isoformat(),
            outcome=outcome,
            reasoning=reasoning,
            metadata=kwargs.get('metadata', {}),
            warnings=kwargs.get('warnings', []),
            recommendations=kwargs.get('recommendations', [])
        )
        
        decision.decision_trail.append(decision_point)
        decision.current_stage = stage
        
        logger.info(f"{decision.request_id} - {stage.value}: {outcome.value} - {reasoning}")
        
        # Update final outcome if decision is terminal
        if outcome in [DecisionOutcome.DENIED, DecisionOutcome.FAILED]:
            decision.final_outcome = outcome
            decision.timestamp_end = datetime.now().isoformat()
    
    def validate_safety(self, decision: OrchestratedDecision, 
                       commands: List[str],
                       safety_checker) -> bool:
        """
        Validate operation safety.
        
        Args:
            decision: The orchestrated decision
            commands: Commands to validate
            safety_checker: Safety validation service
        
        Returns:
            True if safe to proceed
        """
        stage = DecisionStage.SAFETY_VALIDATION
        
        try:
            # Check each command for safety
            dangerous_patterns = []
            protected_paths = []
            warnings = []
            
            for cmd in commands:
                # Use safety checker to validate
                if hasattr(safety_checker, 'is_dangerous'):
                    if safety_checker.is_dangerous(cmd):
                        dangerous_patterns.append(cmd)
                
                if hasattr(safety_checker, 'check_protected_paths'):
                    if not safety_checker.check_protected_paths(cmd):
                        protected_paths.append(cmd)
            
            if dangerous_patterns or protected_paths:
                self.record_decision(
                    decision, stage, DecisionOutcome.NEEDS_REVIEW,
                    "Operation contains high-risk patterns",
                    warnings=[
                        f"Dangerous patterns detected: {len(dangerous_patterns)}",
                        f"Protected paths involved: {len(protected_paths)}"
                    ],
                    recommendations=[
                        "Review command carefully before approval",
                        "Consider using dry-run mode first",
                        "Ensure backups are available"
                    ]
                )
                return True  # Needs review but not denied
            
            self.record_decision(
                decision, stage, DecisionOutcome.APPROVED,
                "No safety issues detected"
            )
            return True
            
        except Exception as e:
            self.record_decision(
                decision, stage, DecisionOutcome.FAILED,
                f"Safety validation error: {str(e)}"
            )
            return False
    
    def check_privileges(self, decision: OrchestratedDecision,
                        operation_type: str,
                        operation_name: str) -> bool:
        """
        Check if current privileges are sufficient.
        
        Args:
            decision: The orchestrated decision
            operation_type: Type of operation
            operation_name: Human-readable name
        
        Returns:
            True if can proceed (possibly degraded)
        """
        stage = DecisionStage.PRIVILEGE_CHECK
        
        priv_check = self.privilege_manager.check_operation(operation_type, operation_name)
        
        if not priv_check.can_proceed:
            self.record_decision(
                decision, stage, DecisionOutcome.DENIED,
                priv_check.message,
                recommendations=priv_check.suggestions
            )
            return False
        
        if priv_check.degraded_mode:
            self.record_decision(
                decision, stage, DecisionOutcome.DEGRADED,
                priv_check.message,
                warnings=["Operating in degraded mode"],
                recommendations=priv_check.suggestions
            )
        else:
            self.record_decision(
                decision, stage, DecisionOutcome.APPROVED,
                priv_check.message
            )
        
        return True
    
    def create_execution_plan(self, decision: OrchestratedDecision,
                             operation_type: str,
                             operation_name: str,
                             commands: List[str],
                             **kwargs) -> ExecutionPlan:
        """
        Create detailed execution plan.
        
        Args:
            decision: The orchestrated decision
            operation_type: Type of operation
            operation_name: Human-readable name
            commands: Commands to execute
            **kwargs: Additional plan parameters
        
        Returns:
            ExecutionPlan object
        """
        stage = DecisionStage.PLANNING
        
        plan = ExecutionPlan(
            operation_type=operation_type,
            operation_name=operation_name,
            commands=commands,
            predicted_changes=kwargs.get('predicted_changes', []),
            risk_level=kwargs.get('risk_level', 'medium'),
            is_reversible=kwargs.get('is_reversible', True),
            requires_backup=kwargs.get('requires_backup', False),
            requires_admin=kwargs.get('requires_admin', False),
            estimated_duration=kwargs.get('estimated_duration', 1.0),
            dependencies=kwargs.get('dependencies', []),
            alternatives=kwargs.get('alternatives', [])
        )
        
        decision.execution_plan = plan
        
        self.record_decision(
            decision, stage, DecisionOutcome.APPROVED,
            f"Execution plan created: {len(commands)} commands, risk={plan.risk_level}",
            metadata={
                'commands_count': len(commands),
                'risk_level': plan.risk_level,
                'reversible': plan.is_reversible,
                'needs_backup': plan.requires_backup
            }
        )
        
        return plan
    
    def await_user_confirmation(self, decision: OrchestratedDecision,
                               user_approved: bool,
                               user_feedback: Optional[str] = None) -> bool:
        """
        Record user confirmation decision.
        
        Args:
            decision: The orchestrated decision
            user_approved: Whether user approved
            user_feedback: Optional user comments
        
        Returns:
            True if approved
        """
        stage = DecisionStage.USER_CONFIRMATION
        
        if user_approved:
            self.record_decision(
                decision, stage, DecisionOutcome.APPROVED,
                "User explicitly approved operation",
                metadata={'user_feedback': user_feedback} if user_feedback else {}
            )
            return True
        else:
            self.record_decision(
                decision, stage, DecisionOutcome.DENIED,
                "User declined operation",
                metadata={'user_feedback': user_feedback} if user_feedback else {}
            )
            decision.final_outcome = DecisionOutcome.DENIED
            decision.timestamp_end = datetime.now().isoformat()
            return False
    
    def execute_with_orchestration(self, decision: OrchestratedDecision,
                                   executor,
                                   timeout: int = 30) -> Dict[str, Any]:
        """
        Execute the planned operation with full orchestration.
        
        Args:
            decision: The orchestrated decision
            executor: CommandExecutor instance
            timeout: Execution timeout
        
        Returns:
            Execution result dictionary
        """
        stage = DecisionStage.EXECUTION
        
        if not decision.execution_plan:
            self.record_decision(
                decision, stage, DecisionOutcome.FAILED,
                "No execution plan available"
            )
            return {'success': False, 'error': 'No execution plan'}
        
        plan = decision.execution_plan
        results = []
        
        try:
            for cmd in plan.commands:
                # Execute command
                result = executor.execute(
                    cmd,
                    timeout=timeout,
                    operation_type=plan.operation_type,
                    operation_name=plan.operation_name
                )
                
                results.append({
                    'command': cmd,
                    'success': result.success,
                    'output': result.stdout,
                    'error': result.stderr,
                    'return_code': result.return_code
                })
                
                # Stop on first failure
                if not result.success:
                    break
            
            # Determine overall success
            all_success = all(r['success'] for r in results)
            
            if all_success:
                self.record_decision(
                    decision, stage, DecisionOutcome.APPROVED,
                    "All commands executed successfully",
                    metadata={'commands_executed': len(results)}
                )
            else:
                self.record_decision(
                    decision, stage, DecisionOutcome.FAILED,
                    "One or more commands failed",
                    metadata={'commands_executed': len(results)}
                )
            
            decision.execution_result = {
                'success': all_success,
                'results': results
            }
            
            return decision.execution_result
            
        except Exception as e:
            self.record_decision(
                decision, stage, DecisionOutcome.FAILED,
                f"Execution exception: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    def complete_decision(self, decision: OrchestratedDecision) -> None:
        """
        Mark decision as completed and calculate metrics.
        
        Args:
            decision: The orchestrated decision to complete
        """
        decision.current_stage = DecisionStage.COMPLETED
        decision.timestamp_end = datetime.now().isoformat()
        
        # Calculate total duration
        start = datetime.fromisoformat(decision.timestamp_start)
        end = datetime.fromisoformat(decision.timestamp_end)
        decision.total_duration = (end - start).total_seconds()
        
        # Determine final outcome if not set
        if not decision.final_outcome:
            if decision.execution_result and decision.execution_result.get('success'):
                decision.final_outcome = DecisionOutcome.APPROVED
            else:
                decision.final_outcome = DecisionOutcome.FAILED
        
        logger.info(f"{decision.request_id} completed: {decision.final_outcome.value} in {decision.total_duration:.2f}s")
    
    def get_decision_summary(self, decision: OrchestratedDecision) -> Dict[str, Any]:
        """
        Get a summary of the decision flow.
        
        Args:
            decision: The orchestrated decision
        
        Returns:
            Summary dictionary
        """
        return {
            'request_id': decision.request_id,
            'user_intent': decision.user_intent,
            'start_time': decision.timestamp_start,
            'end_time': decision.timestamp_end,
            'duration': decision.total_duration,
            'final_outcome': decision.final_outcome.value if decision.final_outcome else None,
            'stages_completed': len(decision.decision_trail),
            'decision_trail': [
                {
                    'stage': dp.stage.value,
                    'outcome': dp.outcome.value,
                    'reasoning': dp.reasoning,
                    'warnings': dp.warnings,
                    'recommendations': dp.recommendations
                }
                for dp in decision.decision_trail
            ],
            'execution_plan': {
                'operation': decision.execution_plan.operation_name if decision.execution_plan else None,
                'commands_count': len(decision.execution_plan.commands) if decision.execution_plan else 0,
                'risk_level': decision.execution_plan.risk_level if decision.execution_plan else None
            } if decision.execution_plan else None,
            'execution_result': decision.execution_result
        }
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decision summaries"""
        return [
            self.get_decision_summary(d)
            for d in self.decision_history[-limit:]
        ]


# Global instance
_orchestrator = None

def get_orchestrator() -> DecisionOrchestrator:
    """Get or create global DecisionOrchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = DecisionOrchestrator()
    return _orchestrator
