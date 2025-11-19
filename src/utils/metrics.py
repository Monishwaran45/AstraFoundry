"""Metrics collection and tracking for AstraFoundry"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import json


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution"""
    agent_name: str
    duration_ms: int
    status: str  # 'success' or 'failed'
    quality_score: Optional[float] = None
    error: Optional[str] = None


@dataclass
class RunMetrics:
    """Metrics for a complete pipeline run"""
    run_id: str
    timestamp: str
    total_duration_ms: int
    status: str  # 'success', 'partial', or 'failed'
    agent_durations: Dict[str, int] = field(default_factory=dict)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    tool_invocations: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert metrics to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert metrics to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class MetricsCollector:
    """Collects and aggregates metrics during pipeline execution"""
    
    PERFORMANCE_THRESHOLD_MS = 60000  # 60 seconds
    
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.start_time = datetime.utcnow()
        self.agent_metrics: List[AgentMetrics] = []
        self.tool_invocations: Dict[str, int] = {}
        self.errors: List[str] = []
        self.alerts: List[str] = []
    
    def record_agent_execution(
        self,
        agent_name: str,
        duration_ms: int,
        status: str,
        quality_score: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Record metrics for an agent execution"""
        metrics = AgentMetrics(
            agent_name=agent_name,
            duration_ms=duration_ms,
            status=status,
            quality_score=quality_score,
            error=error
        )
        self.agent_metrics.append(metrics)
        
        # Check for performance alerts
        if duration_ms > self.PERFORMANCE_THRESHOLD_MS:
            alert = f"Agent '{agent_name}' exceeded performance threshold: {duration_ms}ms"
            self.alerts.append(alert)
        
        # Record errors
        if error:
            self.errors.append(f"{agent_name}: {error}")
    
    def record_tool_invocation(self, tool_name: str):
        """Record a tool invocation"""
        self.tool_invocations[tool_name] = self.tool_invocations.get(tool_name, 0) + 1
    
    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)
    
    def add_alert(self, alert: str):
        """Add an alert message"""
        self.alerts.append(alert)
    
    def finalize(self, status: str) -> RunMetrics:
        """Finalize metrics and return RunMetrics object"""
        end_time = datetime.utcnow()
        total_duration_ms = int((end_time - self.start_time).total_seconds() * 1000)
        
        # Aggregate agent durations
        agent_durations = {
            m.agent_name: m.duration_ms
            for m in self.agent_metrics
        }
        
        # Aggregate quality scores
        quality_scores = {
            m.agent_name: m.quality_score
            for m in self.agent_metrics
            if m.quality_score is not None
        }
        
        return RunMetrics(
            run_id=self.run_id,
            timestamp=self.start_time.isoformat() + 'Z',
            total_duration_ms=total_duration_ms,
            status=status,
            agent_durations=agent_durations,
            quality_scores=quality_scores,
            tool_invocations=self.tool_invocations,
            errors=self.errors,
            alerts=self.alerts
        )


class MetricsStore:
    """Simple in-memory store for metrics (can be extended to persist to file/database)"""
    
    def __init__(self):
        self.metrics: List[RunMetrics] = []
    
    def store(self, metrics: RunMetrics):
        """Store metrics for a run"""
        self.metrics.append(metrics)
    
    def get_all(self) -> List[RunMetrics]:
        """Get all stored metrics"""
        return self.metrics
    
    def get_by_run_id(self, run_id: str) -> Optional[RunMetrics]:
        """Get metrics for a specific run"""
        for m in self.metrics:
            if m.run_id == run_id:
                return m
        return None
    
    def get_average_duration(self) -> float:
        """Get average total duration across all runs"""
        if not self.metrics:
            return 0.0
        return sum(m.total_duration_ms for m in self.metrics) / len(self.metrics)
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage"""
        if not self.metrics:
            return 0.0
        successful = sum(1 for m in self.metrics if m.status == 'success')
        return (successful / len(self.metrics)) * 100


# Global metrics store
_metrics_store = MetricsStore()


def get_metrics_store() -> MetricsStore:
    """Get global metrics store instance"""
    return _metrics_store
