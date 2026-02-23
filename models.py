"""
Voice Bot Intelligence Tool - Data Models
==========================================
Defines all data structures for campaign analysis, call logs, and performance metrics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class CallStatus(Enum):
    """Possible outcomes of a voice bot call"""
    COMPLETED = "completed"
    DROPPED = "dropped"
    ESCALATED = "escalated"
    FAILED = "failed"
    COMPLIANCE_VIOLATION = "compliance_violation"


class DropOffStage(Enum):
    """Stages where calls can drop off"""
    INTRO = "intro"
    QUALIFICATION = "qualification"
    PITCH = "pitch"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"


class IssueType(Enum):
    """Types of performance issues"""
    HIGH_DROP_OFF = "high_drop_off"
    LOW_CONVERSION = "low_conversion"
    COMPLIANCE_RISK = "compliance_risk"
    ESCALATION_SPIKE = "escalation_spike"
    SCRIPT_FAILURE = "script_failure"
    TECHNICAL_ERROR = "technical_error"


class IssueSeverity(Enum):
    """Severity levels for issues"""
    CRITICAL = "critical"  # >20% revenue impact
    HIGH = "high"          # 10-20% revenue impact
    MEDIUM = "medium"      # 5-10% revenue impact
    LOW = "low"            # <5% revenue impact


@dataclass
class CallRecord:
    """Individual call data from voice bot"""
    call_id: str
    campaign_id: str
    timestamp: datetime
    duration_seconds: int
    status: CallStatus
    drop_off_stage: Optional[DropOffStage]
    escalation_reason: Optional[str]
    compliance_flags: List[str]
    conversion_value: float  # Expected revenue from this call
    actual_revenue: float    # Actual revenue generated
    sentiment_score: float   # -1 to 1 (negative to positive)
    script_version: str
    agent_id: Optional[str]  # If escalated to human
    
    def __post_init__(self):
        """Validate call record data"""
        if not 0 <= self.duration_seconds <= 7200:  # Max 2 hours
            raise ValueError(f"Invalid duration: {self.duration_seconds}")
        if not -1 <= self.sentiment_score <= 1:
            raise ValueError(f"Invalid sentiment score: {self.sentiment_score}")


@dataclass
class CampaignConfig:
    """Campaign configuration and targets"""
    campaign_id: str
    campaign_name: str
    start_date: datetime
    target_calls_per_day: int
    target_conversion_rate: float  # 0.0 to 1.0
    target_revenue_per_call: float
    avg_deal_value: float
    compliance_rules: List[str]
    script_versions: List[str]
    
    def expected_daily_revenue(self) -> float:
        """Calculate expected daily revenue"""
        return (self.target_calls_per_day * 
                self.target_conversion_rate * 
                self.avg_deal_value)


@dataclass
class PerformanceMetrics:
    """Calculated performance metrics for a time period"""
    campaign_id: str
    period_start: datetime
    period_end: datetime
    total_calls: int
    completed_calls: int
    dropped_calls: int
    escalated_calls: int
    failed_calls: int
    compliance_violations: int
    
    # Conversion metrics
    conversions: int
    conversion_rate: float
    
    # Revenue metrics
    total_revenue: float
    expected_revenue: float
    revenue_leakage: float
    revenue_leakage_percentage: float
    
    # Quality metrics
    avg_call_duration: float
    avg_sentiment_score: float
    
    # Drop-off analysis
    drop_off_by_stage: Dict[DropOffStage, int] = field(default_factory=dict)
    
    def completion_rate(self) -> float:
        """Calculate completion rate"""
        if self.total_calls == 0:
            return 0.0
        return self.completed_calls / self.total_calls
    
    def escalation_rate(self) -> float:
        """Calculate escalation rate"""
        if self.total_calls == 0:
            return 0.0
        return self.escalated_calls / self.total_calls


@dataclass
class PerformanceIssue:
    """Identified performance issue"""
    issue_id: str
    campaign_id: str
    issue_type: IssueType
    severity: IssueSeverity
    detected_at: datetime
    
    # Impact metrics
    affected_calls: int
    revenue_impact: float
    conversion_impact: float
    
    # Root cause details
    root_cause: str
    contributing_factors: List[str]
    
    # Location in funnel
    problematic_stage: Optional[DropOffStage]
    script_version: Optional[str]
    
    # Supporting data
    evidence: Dict[str, any] = field(default_factory=dict)
    
    def impact_percentage(self, total_revenue: float) -> float:
        """Calculate impact as percentage of total revenue"""
        if total_revenue == 0:
            return 0.0
        return (self.revenue_impact / total_revenue) * 100


@dataclass
class ActionableRecommendation:
    """Generated recommendation to fix an issue"""
    recommendation_id: str
    issue_id: str
    priority: int  # 1-5, 1 being highest
    
    # The recommendation
    action: str
    expected_impact: str
    implementation_effort: str  # "low", "medium", "high"
    
    # Implementation details
    steps: List[str]
    resources_needed: List[str]
    estimated_time: str
    
    # Expected outcomes
    expected_revenue_recovery: float
    expected_conversion_lift: float
    confidence_score: float  # 0.0 to 1.0


@dataclass
class HealthScore:
    """Overall campaign health scoring"""
    campaign_id: str
    calculated_at: datetime
    overall_score: int  # 0-100
    
    # Component scores (each 0-100)
    conversion_health: int
    revenue_health: int
    compliance_health: int
    efficiency_health: int
    quality_health: int
    
    # Trend indicators
    trend: str  # "improving", "stable", "declining"
    week_over_week_change: float
    
    # Score breakdown
    score_components: Dict[str, float] = field(default_factory=dict)
    
    def health_status(self) -> str:
        """Get human-readable health status"""
        if self.overall_score >= 80:
            return "Excellent"
        elif self.overall_score >= 60:
            return "Good"
        elif self.overall_score >= 40:
            return "Fair"
        elif self.overall_score >= 20:
            return "Poor"
        else:
            return "Critical"


@dataclass
class Alert:
    """Performance alert triggered by system"""
    alert_id: str
    campaign_id: str
    alert_type: str
    severity: IssueSeverity
    triggered_at: datetime
    
    # Alert details
    title: str
    message: str
    metric_name: str
    current_value: float
    previous_value: float
    threshold_value: float
    
    # Change metrics
    percentage_change: float
    absolute_change: float
    
    # Context
    affected_period: str
    comparison_period: str
    
    def is_critical(self) -> bool:
        """Check if alert is critical"""
        return self.severity == IssueSeverity.CRITICAL


@dataclass
class IntelligenceReport:
    """Complete intelligence report for a campaign"""
    campaign_id: str
    report_date: datetime
    period_analyzed: str
    
    # Core metrics
    performance_metrics: PerformanceMetrics
    health_score: HealthScore
    
    # Issues and recommendations
    issues: List[PerformanceIssue]
    recommendations: List[ActionableRecommendation]
    
    # Alerts
    active_alerts: List[Alert]
    
    # Trends
    week_over_week_changes: Dict[str, float]
    
    # Executive summary
    summary: str
    key_insights: List[str]
    urgent_actions: List[str]
