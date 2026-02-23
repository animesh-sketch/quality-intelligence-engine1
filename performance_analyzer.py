"""
Voice Bot Intelligence Tool - Performance Analyzer
===================================================
Detects performance issues in voice bot campaigns by analyzing call patterns,
conversion rates, and comparing against benchmarks.
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from models import (
    CallRecord, CampaignConfig, PerformanceMetrics, PerformanceIssue,
    IssueType, IssueSeverity, CallStatus, DropOffStage
)


class PerformanceAnalyzer:
    """
    Analyzes campaign performance and detects issues
    """
    
    # Industry benchmarks
    BENCHMARK_CONVERSION_RATE = 0.15  # 15%
    BENCHMARK_COMPLETION_RATE = 0.70  # 70%
    BENCHMARK_ESCALATION_RATE = 0.10  # 10%
    BENCHMARK_COMPLIANCE_RATE = 0.98  # 98% clean calls
    
    # Thresholds for issue detection
    CRITICAL_DROP_OFF_THRESHOLD = 0.30  # >30% drop-off is critical
    HIGH_DROP_OFF_THRESHOLD = 0.20      # >20% drop-off is high
    
    def __init__(self, config: CampaignConfig):
        """Initialize analyzer with campaign configuration"""
        self.config = config
        self.issues: List[PerformanceIssue] = []
    
    def calculate_metrics(self, calls: List[CallRecord]) -> PerformanceMetrics:
        """
        Calculate performance metrics from call records
        
        Args:
            calls: List of call records to analyze
            
        Returns:
            PerformanceMetrics object with all calculated metrics
        """
        if not calls:
            return self._empty_metrics()
        
        # Basic counts
        total_calls = len(calls)
        completed = sum(1 for c in calls if c.status == CallStatus.COMPLETED)
        dropped = sum(1 for c in calls if c.status == CallStatus.DROPPED)
        escalated = sum(1 for c in calls if c.status == CallStatus.ESCALATED)
        failed = sum(1 for c in calls if c.status == CallStatus.FAILED)
        compliance_violations = sum(1 for c in calls if c.status == CallStatus.COMPLIANCE_VIOLATION)
        
        # Conversion metrics
        conversions = sum(1 for c in calls if c.actual_revenue > 0)
        conversion_rate = conversions / total_calls if total_calls > 0 else 0.0
        
        # Revenue metrics
        total_revenue = sum(c.actual_revenue for c in calls)
        expected_revenue = sum(c.conversion_value for c in calls)
        revenue_leakage = expected_revenue - total_revenue
        revenue_leakage_pct = (revenue_leakage / expected_revenue * 100) if expected_revenue > 0 else 0.0
        
        # Quality metrics
        avg_duration = statistics.mean([c.duration_seconds for c in calls]) if calls else 0.0
        avg_sentiment = statistics.mean([c.sentiment_score for c in calls]) if calls else 0.0
        
        # Drop-off analysis by stage
        drop_off_by_stage = defaultdict(int)
        for call in calls:
            if call.drop_off_stage:
                drop_off_by_stage[call.drop_off_stage] += 1
        
        # Get period from calls
        period_start = min(c.timestamp for c in calls)
        period_end = max(c.timestamp for c in calls)
        
        return PerformanceMetrics(
            campaign_id=self.config.campaign_id,
            period_start=period_start,
            period_end=period_end,
            total_calls=total_calls,
            completed_calls=completed,
            dropped_calls=dropped,
            escalated_calls=escalated,
            failed_calls=failed,
            compliance_violations=compliance_violations,
            conversions=conversions,
            conversion_rate=conversion_rate,
            total_revenue=total_revenue,
            expected_revenue=expected_revenue,
            revenue_leakage=revenue_leakage,
            revenue_leakage_percentage=revenue_leakage_pct,
            avg_call_duration=avg_duration,
            avg_sentiment_score=avg_sentiment,
            drop_off_by_stage=dict(drop_off_by_stage)
        )
    
    def detect_issues(
        self, 
        current_metrics: PerformanceMetrics,
        calls: List[CallRecord]
    ) -> List[PerformanceIssue]:
        """
        Detect all performance issues in current metrics
        
        Args:
            current_metrics: Current period performance metrics
            calls: Raw call records for detailed analysis
            
        Returns:
            List of detected performance issues
        """
        self.issues = []
        
        # Check each type of issue
        self._detect_conversion_issues(current_metrics, calls)
        self._detect_drop_off_issues(current_metrics, calls)
        self._detect_escalation_issues(current_metrics, calls)
        self._detect_compliance_issues(current_metrics, calls)
        self._detect_technical_issues(current_metrics, calls)
        
        return self.issues
    
    def _detect_conversion_issues(
        self, 
        metrics: PerformanceMetrics,
        calls: List[CallRecord]
    ) -> None:
        """Detect low conversion rate issues"""
        
        # Compare to target
        target_rate = self.config.target_conversion_rate
        actual_rate = metrics.conversion_rate
        
        # Calculate variance
        variance = (target_rate - actual_rate) / target_rate if target_rate > 0 else 0
        
        # Only flag if significantly below target
        if variance > 0.20:  # >20% below target
            
            # Calculate revenue impact
            lost_conversions = (target_rate - actual_rate) * metrics.total_calls
            revenue_impact = lost_conversions * self.config.avg_deal_value
            
            # Determine severity
            severity = self._calculate_severity(revenue_impact, metrics.total_revenue)
            
            # Analyze contributing factors
            factors = self._analyze_conversion_factors(calls)
            
            issue = PerformanceIssue(
                issue_id=f"CONV_{self.config.campaign_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                campaign_id=self.config.campaign_id,
                issue_type=IssueType.LOW_CONVERSION,
                severity=severity,
                detected_at=datetime.now(),
                affected_calls=metrics.total_calls,
                revenue_impact=revenue_impact,
                conversion_impact=variance,
                root_cause=f"Conversion rate {actual_rate:.1%} is {variance:.1%} below target {target_rate:.1%}",
                contributing_factors=factors,
                problematic_stage=None,
                script_version=None,
                evidence={
                    "target_rate": target_rate,
                    "actual_rate": actual_rate,
                    "variance": variance,
                    "lost_conversions": lost_conversions
                }
            )
            
            self.issues.append(issue)
    
    def _detect_drop_off_issues(
        self, 
        metrics: PerformanceMetrics,
        calls: List[CallRecord]
    ) -> None:
        """Detect high drop-off rate issues"""
        
        drop_off_rate = metrics.dropped_calls / metrics.total_calls if metrics.total_calls > 0 else 0
        
        if drop_off_rate > self.HIGH_DROP_OFF_THRESHOLD:
            
            # Find the stage with highest drop-off
            worst_stage = None
            worst_stage_count = 0
            
            for stage, count in metrics.drop_off_by_stage.items():
                if count > worst_stage_count:
                    worst_stage = stage
                    worst_stage_count = count
            
            # Calculate impact
            # Assume 50% of dropped calls would have converted
            potential_conversions = metrics.dropped_calls * self.config.target_conversion_rate * 0.5
            revenue_impact = potential_conversions * self.config.avg_deal_value
            
            severity = self._calculate_severity(revenue_impact, metrics.total_revenue)
            
            # Analyze why calls are dropping at this stage
            factors = self._analyze_drop_off_factors(calls, worst_stage)
            
            issue = PerformanceIssue(
                issue_id=f"DROP_{self.config.campaign_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                campaign_id=self.config.campaign_id,
                issue_type=IssueType.HIGH_DROP_OFF,
                severity=severity,
                detected_at=datetime.now(),
                affected_calls=metrics.dropped_calls,
                revenue_impact=revenue_impact,
                conversion_impact=drop_off_rate,
                root_cause=f"High drop-off rate of {drop_off_rate:.1%} (threshold: {self.HIGH_DROP_OFF_THRESHOLD:.1%})",
                contributing_factors=factors,
                problematic_stage=worst_stage,
                script_version=None,
                evidence={
                    "drop_off_rate": drop_off_rate,
                    "worst_stage": worst_stage.value if worst_stage else None,
                    "worst_stage_count": worst_stage_count,
                    "drop_off_by_stage": {k.value: v for k, v in metrics.drop_off_by_stage.items()}
                }
            )
            
            self.issues.append(issue)
    
    def _detect_escalation_issues(
        self, 
        metrics: PerformanceMetrics,
        calls: List[CallRecord]
    ) -> None:
        """Detect high escalation rate issues"""
        
        escalation_rate = metrics.escalation_rate()
        
        if escalation_rate > self.BENCHMARK_ESCALATION_RATE * 1.5:  # 50% above benchmark
            
            # Analyze escalation reasons
            escalation_reasons = defaultdict(int)
            for call in calls:
                if call.status == CallStatus.ESCALATED and call.escalation_reason:
                    escalation_reasons[call.escalation_reason] += 1
            
            # Find most common reason
            top_reason = max(escalation_reasons.items(), key=lambda x: x[1]) if escalation_reasons else ("Unknown", 0)
            
            # Calculate impact (escalations are expensive)
            # Assume each escalation costs $50 in human agent time
            revenue_impact = metrics.escalated_calls * 50
            
            severity = self._calculate_severity(revenue_impact, metrics.total_revenue)
            
            factors = [
                f"Top escalation reason: {top_reason[0]} ({top_reason[1]} calls)",
                f"Escalation rate {escalation_rate:.1%} vs benchmark {self.BENCHMARK_ESCALATION_RATE:.1%}",
                "Bot unable to handle complex objections or questions"
            ]
            
            issue = PerformanceIssue(
                issue_id=f"ESC_{self.config.campaign_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                campaign_id=self.config.campaign_id,
                issue_type=IssueType.ESCALATION_SPIKE,
                severity=severity,
                detected_at=datetime.now(),
                affected_calls=metrics.escalated_calls,
                revenue_impact=revenue_impact,
                conversion_impact=0.0,
                root_cause=f"Escalation rate {escalation_rate:.1%} is {(escalation_rate/self.BENCHMARK_ESCALATION_RATE - 1):.1%} above benchmark",
                contributing_factors=factors,
                problematic_stage=None,
                script_version=None,
                evidence={
                    "escalation_rate": escalation_rate,
                    "escalation_reasons": dict(escalation_reasons),
                    "top_reason": top_reason[0]
                }
            )
            
            self.issues.append(issue)
    
    def _detect_compliance_issues(
        self, 
        metrics: PerformanceMetrics,
        calls: List[CallRecord]
    ) -> None:
        """Detect compliance violation issues"""
        
        compliance_rate = 1 - (metrics.compliance_violations / metrics.total_calls) if metrics.total_calls > 0 else 1.0
        
        if compliance_rate < self.BENCHMARK_COMPLIANCE_RATE:
            
            # Collect all compliance flags
            compliance_flags = defaultdict(int)
            for call in calls:
                if call.status == CallStatus.COMPLIANCE_VIOLATION:
                    for flag in call.compliance_flags:
                        compliance_flags[flag] += 1
            
            # Find most common violation
            top_violation = max(compliance_flags.items(), key=lambda x: x[1]) if compliance_flags else ("Unknown", 0)
            
            # Compliance issues are always critical
            severity = IssueSeverity.CRITICAL
            
            # Revenue impact: potential fines + lost business
            revenue_impact = metrics.compliance_violations * 1000  # Assume $1000 per violation risk
            
            factors = [
                f"Most common violation: {top_violation[0]} ({top_violation[1]} occurrences)",
                f"Compliance rate {compliance_rate:.1%} vs required {self.BENCHMARK_COMPLIANCE_RATE:.1%}",
                "Risk of regulatory fines and brand damage"
            ]
            
            issue = PerformanceIssue(
                issue_id=f"COMP_{self.config.campaign_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                campaign_id=self.config.campaign_id,
                issue_type=IssueType.COMPLIANCE_RISK,
                severity=severity,
                detected_at=datetime.now(),
                affected_calls=metrics.compliance_violations,
                revenue_impact=revenue_impact,
                conversion_impact=0.0,
                root_cause=f"Compliance rate {compliance_rate:.1%} below required {self.BENCHMARK_COMPLIANCE_RATE:.1%}",
                contributing_factors=factors,
                problematic_stage=None,
                script_version=None,
                evidence={
                    "compliance_rate": compliance_rate,
                    "violation_types": dict(compliance_flags),
                    "top_violation": top_violation[0]
                }
            )
            
            self.issues.append(issue)
    
    def _detect_technical_issues(
        self, 
        metrics: PerformanceMetrics,
        calls: List[CallRecord]
    ) -> None:
        """Detect technical failures"""
        
        failure_rate = metrics.failed_calls / metrics.total_calls if metrics.total_calls > 0 else 0
        
        if failure_rate > 0.05:  # >5% failure rate
            
            # Technical failures directly impact revenue
            potential_revenue = metrics.failed_calls * self.config.target_revenue_per_call
            
            severity = self._calculate_severity(potential_revenue, metrics.total_revenue)
            
            factors = [
                f"{metrics.failed_calls} calls failed to complete due to technical issues",
                "Potential infrastructure, API, or telephony problems",
                f"Failure rate: {failure_rate:.1%}"
            ]
            
            issue = PerformanceIssue(
                issue_id=f"TECH_{self.config.campaign_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                campaign_id=self.config.campaign_id,
                issue_type=IssueType.TECHNICAL_ERROR,
                severity=severity,
                detected_at=datetime.now(),
                affected_calls=metrics.failed_calls,
                revenue_impact=potential_revenue,
                conversion_impact=failure_rate,
                root_cause=f"Technical failure rate of {failure_rate:.1%} affecting {metrics.failed_calls} calls",
                contributing_factors=factors,
                problematic_stage=None,
                script_version=None,
                evidence={
                    "failure_rate": failure_rate,
                    "failed_calls": metrics.failed_calls
                }
            )
            
            self.issues.append(issue)
    
    def _analyze_conversion_factors(self, calls: List[CallRecord]) -> List[str]:
        """Analyze what's causing low conversions"""
        factors = []
        
        # Check sentiment scores
        avg_sentiment = statistics.mean([c.sentiment_score for c in calls]) if calls else 0
        if avg_sentiment < 0:
            factors.append(f"Negative average sentiment score: {avg_sentiment:.2f}")
        
        # Check call duration
        completed_calls = [c for c in calls if c.status == CallStatus.COMPLETED]
        if completed_calls:
            avg_duration = statistics.mean([c.duration_seconds for c in completed_calls])
            if avg_duration < 180:  # Less than 3 minutes
                factors.append(f"Very short call duration ({avg_duration/60:.1f} min) suggests low engagement")
        
        # Check if specific script versions perform poorly
        script_conversions = defaultdict(lambda: {"total": 0, "converted": 0})
        for call in calls:
            script_conversions[call.script_version]["total"] += 1
            if call.actual_revenue > 0:
                script_conversions[call.script_version]["converted"] += 1
        
        for script, stats in script_conversions.items():
            conv_rate = stats["converted"] / stats["total"] if stats["total"] > 0 else 0
            if conv_rate < self.config.target_conversion_rate * 0.7:  # 30% below target
                factors.append(f"Script version {script} has low conversion rate: {conv_rate:.1%}")
        
        if not factors:
            factors.append("Multiple factors affecting conversion - requires deeper analysis")
        
        return factors
    
    def _analyze_drop_off_factors(
        self, 
        calls: List[CallRecord],
        stage: Optional[DropOffStage]
    ) -> List[str]:
        """Analyze why calls are dropping off"""
        factors = []
        
        if stage:
            # Analyze calls that dropped at this specific stage
            stage_drops = [c for c in calls if c.drop_off_stage == stage]
            
            if stage_drops:
                avg_duration = statistics.mean([c.duration_seconds for c in stage_drops])
                avg_sentiment = statistics.mean([c.sentiment_score for c in stage_drops])
                
                factors.append(f"Stage '{stage.value}' has highest drop-off")
                factors.append(f"Average duration before drop: {avg_duration/60:.1f} minutes")
                
                if avg_sentiment < -0.2:
                    factors.append(f"Negative sentiment ({avg_sentiment:.2f}) indicates user frustration")
                
                # Check if script length is an issue
                if stage == DropOffStage.INTRO and avg_duration < 30:
                    factors.append("Intro too long or unengaging - users drop within 30 seconds")
                elif stage == DropOffStage.PITCH and avg_duration > 300:
                    factors.append("Pitch phase too lengthy - losing user attention")
        
        if not factors:
            factors.append("High overall drop-off across multiple stages")
        
        return factors
    
    def _calculate_severity(self, revenue_impact: float, total_revenue: float) -> IssueSeverity:
        """Calculate issue severity based on revenue impact"""
        if total_revenue == 0:
            return IssueSeverity.MEDIUM
        
        impact_pct = (revenue_impact / total_revenue) * 100
        
        if impact_pct > 20:
            return IssueSeverity.CRITICAL
        elif impact_pct > 10:
            return IssueSeverity.HIGH
        elif impact_pct > 5:
            return IssueSeverity.MEDIUM
        else:
            return IssueSeverity.LOW
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics when no calls available"""
        return PerformanceMetrics(
            campaign_id=self.config.campaign_id,
            period_start=datetime.now(),
            period_end=datetime.now(),
            total_calls=0,
            completed_calls=0,
            dropped_calls=0,
            escalated_calls=0,
            failed_calls=0,
            compliance_violations=0,
            conversions=0,
            conversion_rate=0.0,
            total_revenue=0.0,
            expected_revenue=0.0,
            revenue_leakage=0.0,
            revenue_leakage_percentage=0.0,
            avg_call_duration=0.0,
            avg_sentiment_score=0.0,
            drop_off_by_stage={}
        )
