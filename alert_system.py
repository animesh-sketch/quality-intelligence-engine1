"""
Voice Bot Intelligence Tool - Alert System
===========================================
Monitors week-over-week changes and generates alerts when
performance drops or issues arise.
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta

from models import (
    PerformanceMetrics, Alert, IssueSeverity, CampaignConfig,
    HealthScore, PerformanceIssue
)


class AlertSystem:
    """
    Monitors performance changes and generates alerts
    """
    
    # Alert thresholds (percentage change to trigger alert)
    THRESHOLDS = {
        "revenue_drop": -10.0,           # Alert if revenue drops >10%
        "conversion_drop": -15.0,        # Alert if conversion drops >15%
        "drop_off_spike": 20.0,          # Alert if drop-off increases >20%
        "escalation_spike": 25.0,        # Alert if escalations increase >25%
        "compliance_violation": 0.0,     # Alert on ANY compliance increase
        "health_score_drop": -15.0,      # Alert if health score drops >15 points
        "failure_spike": 50.0            # Alert if failures increase >50%
    }
    
    def __init__(self, config: CampaignConfig):
        """Initialize alert system with campaign config"""
        self.config = config
        self.alert_counter = 0
    
    def generate_alerts(
        self,
        current_metrics: PerformanceMetrics,
        previous_metrics: PerformanceMetrics,
        current_health: HealthScore,
        previous_health: HealthScore = None,
        issues: List[PerformanceIssue] = None
    ) -> List[Alert]:
        """
        Generate all relevant alerts by comparing current vs previous period
        
        Args:
            current_metrics: Current period metrics
            previous_metrics: Previous period metrics
            current_health: Current health score
            previous_health: Previous health score (optional)
            issues: Currently detected issues (optional)
            
        Returns:
            List of generated alerts
        """
        
        alerts = []
        
        # Revenue alerts
        revenue_alerts = self._check_revenue_alerts(current_metrics, previous_metrics)
        alerts.extend(revenue_alerts)
        
        # Conversion alerts
        conversion_alerts = self._check_conversion_alerts(current_metrics, previous_metrics)
        alerts.extend(conversion_alerts)
        
        # Operational alerts
        operational_alerts = self._check_operational_alerts(current_metrics, previous_metrics)
        alerts.extend(operational_alerts)
        
        # Compliance alerts
        compliance_alerts = self._check_compliance_alerts(current_metrics, previous_metrics)
        alerts.extend(compliance_alerts)
        
        # Health score alerts
        if previous_health:
            health_alerts = self._check_health_alerts(current_health, previous_health)
            alerts.extend(health_alerts)
        
        # Issue-based alerts
        if issues:
            issue_alerts = self._generate_issue_alerts(issues)
            alerts.extend(issue_alerts)
        
        # Sort by severity
        alerts.sort(key=lambda a: (
            0 if a.severity == IssueSeverity.CRITICAL else
            1 if a.severity == IssueSeverity.HIGH else
            2 if a.severity == IssueSeverity.MEDIUM else 3
        ))
        
        return alerts
    
    def _check_revenue_alerts(
        self,
        current: PerformanceMetrics,
        previous: PerformanceMetrics
    ) -> List[Alert]:
        """Check for revenue-related alerts"""
        
        alerts = []
        
        if previous.total_revenue == 0:
            return alerts
        
        # Calculate revenue change
        change_amount = current.total_revenue - previous.total_revenue
        change_pct = (change_amount / previous.total_revenue) * 100
        
        # Alert on significant revenue drop
        if change_pct < self.THRESHOLDS["revenue_drop"]:
            
            # Determine severity
            if change_pct < -25:
                severity = IssueSeverity.CRITICAL
            elif change_pct < -20:
                severity = IssueSeverity.HIGH
            else:
                severity = IssueSeverity.MEDIUM
            
            alert = Alert(
                alert_id=self._next_id(),
                campaign_id=self.config.campaign_id,
                alert_type="revenue_drop",
                severity=severity,
                triggered_at=datetime.now(),
                title="Revenue Drop Alert",
                message=f"Revenue decreased by {abs(change_pct):.1f}% compared to last week. Lost ${abs(change_amount):,.0f} in revenue.",
                metric_name="total_revenue",
                current_value=current.total_revenue,
                previous_value=previous.total_revenue,
                threshold_value=previous.total_revenue * (1 + self.THRESHOLDS["revenue_drop"]/100),
                percentage_change=change_pct,
                absolute_change=change_amount,
                affected_period=self._format_period(current),
                comparison_period=self._format_period(previous)
            )
            
            alerts.append(alert)
        
        # Alert on revenue leakage increase
        if previous.revenue_leakage > 0:
            leakage_change_pct = (
                (current.revenue_leakage - previous.revenue_leakage) / 
                previous.revenue_leakage * 100
            )
            
            if leakage_change_pct > 20:  # >20% increase in leakage
                alert = Alert(
                    alert_id=self._next_id(),
                    campaign_id=self.config.campaign_id,
                    alert_type="revenue_leakage_increase",
                    severity=IssueSeverity.HIGH,
                    triggered_at=datetime.now(),
                    title="Revenue Leakage Increasing",
                    message=f"Revenue leakage increased by {leakage_change_pct:.1f}% to ${current.revenue_leakage:,.0f}",
                    metric_name="revenue_leakage",
                    current_value=current.revenue_leakage,
                    previous_value=previous.revenue_leakage,
                    threshold_value=previous.revenue_leakage * 1.20,
                    percentage_change=leakage_change_pct,
                    absolute_change=current.revenue_leakage - previous.revenue_leakage,
                    affected_period=self._format_period(current),
                    comparison_period=self._format_period(previous)
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _check_conversion_alerts(
        self,
        current: PerformanceMetrics,
        previous: PerformanceMetrics
    ) -> List[Alert]:
        """Check for conversion-related alerts"""
        
        alerts = []
        
        if previous.conversion_rate == 0:
            return alerts
        
        # Calculate conversion rate change
        rate_change = current.conversion_rate - previous.conversion_rate
        rate_change_pct = (rate_change / previous.conversion_rate) * 100
        
        if rate_change_pct < self.THRESHOLDS["conversion_drop"]:
            
            severity = IssueSeverity.HIGH if rate_change_pct < -25 else IssueSeverity.MEDIUM
            
            alert = Alert(
                alert_id=self._next_id(),
                campaign_id=self.config.campaign_id,
                alert_type="conversion_drop",
                severity=severity,
                triggered_at=datetime.now(),
                title="Conversion Rate Declining",
                message=f"Conversion rate dropped {abs(rate_change_pct):.1f}% from {previous.conversion_rate:.1%} to {current.conversion_rate:.1%}",
                metric_name="conversion_rate",
                current_value=current.conversion_rate,
                previous_value=previous.conversion_rate,
                threshold_value=previous.conversion_rate * (1 + self.THRESHOLDS["conversion_drop"]/100),
                percentage_change=rate_change_pct,
                absolute_change=rate_change,
                affected_period=self._format_period(current),
                comparison_period=self._format_period(previous)
            )
            
            alerts.append(alert)
        
        return alerts
    
    def _check_operational_alerts(
        self,
        current: PerformanceMetrics,
        previous: PerformanceMetrics
    ) -> List[Alert]:
        """Check for operational alerts (drop-offs, escalations, failures)"""
        
        alerts = []
        
        # Drop-off rate alert
        current_dropoff_rate = current.dropped_calls / current.total_calls if current.total_calls > 0 else 0
        previous_dropoff_rate = previous.dropped_calls / previous.total_calls if previous.total_calls > 0 else 0
        
        if previous_dropoff_rate > 0:
            dropoff_change_pct = (
                (current_dropoff_rate - previous_dropoff_rate) / 
                previous_dropoff_rate * 100
            )
            
            if dropoff_change_pct > self.THRESHOLDS["drop_off_spike"]:
                alert = Alert(
                    alert_id=self._next_id(),
                    campaign_id=self.config.campaign_id,
                    alert_type="drop_off_spike",
                    severity=IssueSeverity.HIGH,
                    triggered_at=datetime.now(),
                    title="Drop-off Rate Increasing",
                    message=f"Call drop-off rate spiked {dropoff_change_pct:.1f}% to {current_dropoff_rate:.1%}. {current.dropped_calls} calls dropped this period.",
                    metric_name="drop_off_rate",
                    current_value=current_dropoff_rate,
                    previous_value=previous_dropoff_rate,
                    threshold_value=previous_dropoff_rate * (1 + self.THRESHOLDS["drop_off_spike"]/100),
                    percentage_change=dropoff_change_pct,
                    absolute_change=current_dropoff_rate - previous_dropoff_rate,
                    affected_period=self._format_period(current),
                    comparison_period=self._format_period(previous)
                )
                
                alerts.append(alert)
        
        # Escalation rate alert
        current_escalation_rate = current.escalation_rate()
        previous_escalation_rate = previous.escalation_rate()
        
        if previous_escalation_rate > 0:
            escalation_change_pct = (
                (current_escalation_rate - previous_escalation_rate) / 
                previous_escalation_rate * 100
            )
            
            if escalation_change_pct > self.THRESHOLDS["escalation_spike"]:
                alert = Alert(
                    alert_id=self._next_id(),
                    campaign_id=self.config.campaign_id,
                    alert_type="escalation_spike",
                    severity=IssueSeverity.MEDIUM,
                    triggered_at=datetime.now(),
                    title="Escalation Rate Spiking",
                    message=f"Escalations increased {escalation_change_pct:.1f}% to {current_escalation_rate:.1%}. {current.escalated_calls} calls escalated.",
                    metric_name="escalation_rate",
                    current_value=current_escalation_rate,
                    previous_value=previous_escalation_rate,
                    threshold_value=previous_escalation_rate * (1 + self.THRESHOLDS["escalation_spike"]/100),
                    percentage_change=escalation_change_pct,
                    absolute_change=current_escalation_rate - previous_escalation_rate,
                    affected_period=self._format_period(current),
                    comparison_period=self._format_period(previous)
                )
                
                alerts.append(alert)
        
        # Technical failure alert
        current_failure_rate = current.failed_calls / current.total_calls if current.total_calls > 0 else 0
        previous_failure_rate = previous.failed_calls / previous.total_calls if previous.total_calls > 0 else 0
        
        if previous_failure_rate > 0:
            failure_change_pct = (
                (current_failure_rate - previous_failure_rate) / 
                previous_failure_rate * 100
            )
            
            if failure_change_pct > self.THRESHOLDS["failure_spike"]:
                alert = Alert(
                    alert_id=self._next_id(),
                    campaign_id=self.config.campaign_id,
                    alert_type="technical_failure_spike",
                    severity=IssueSeverity.CRITICAL,
                    triggered_at=datetime.now(),
                    title="Technical Failures Spiking",
                    message=f"System failures increased {failure_change_pct:.1f}% to {current_failure_rate:.1%}. {current.failed_calls} calls failed.",
                    metric_name="failure_rate",
                    current_value=current_failure_rate,
                    previous_value=previous_failure_rate,
                    threshold_value=previous_failure_rate * (1 + self.THRESHOLDS["failure_spike"]/100),
                    percentage_change=failure_change_pct,
                    absolute_change=current_failure_rate - previous_failure_rate,
                    affected_period=self._format_period(current),
                    comparison_period=self._format_period(previous)
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _check_compliance_alerts(
        self,
        current: PerformanceMetrics,
        previous: PerformanceMetrics
    ) -> List[Alert]:
        """Check for compliance alerts"""
        
        alerts = []
        
        # Alert on ANY increase in compliance violations
        violation_increase = current.compliance_violations - previous.compliance_violations
        
        if violation_increase > 0:
            alert = Alert(
                alert_id=self._next_id(),
                campaign_id=self.config.campaign_id,
                alert_type="compliance_violation_increase",
                severity=IssueSeverity.CRITICAL,  # Compliance is always critical
                triggered_at=datetime.now(),
                title="Compliance Violations Detected",
                message=f"Compliance violations increased by {violation_increase}. Total violations: {current.compliance_violations}. IMMEDIATE ACTION REQUIRED.",
                metric_name="compliance_violations",
                current_value=float(current.compliance_violations),
                previous_value=float(previous.compliance_violations),
                threshold_value=float(previous.compliance_violations),
                percentage_change=(violation_increase / max(1, previous.compliance_violations)) * 100,
                absolute_change=float(violation_increase),
                affected_period=self._format_period(current),
                comparison_period=self._format_period(previous)
            )
            
            alerts.append(alert)
        
        return alerts
    
    def _check_health_alerts(
        self,
        current_health: HealthScore,
        previous_health: HealthScore
    ) -> List[Alert]:
        """Check for health score alerts"""
        
        alerts = []
        
        # Overall health score drop
        score_change = current_health.overall_score - previous_health.overall_score
        
        if score_change < self.THRESHOLDS["health_score_drop"]:
            
            if score_change < -25:
                severity = IssueSeverity.CRITICAL
            elif score_change < -20:
                severity = IssueSeverity.HIGH
            else:
                severity = IssueSeverity.MEDIUM
            
            alert = Alert(
                alert_id=self._next_id(),
                campaign_id=self.config.campaign_id,
                alert_type="health_score_drop",
                severity=severity,
                triggered_at=datetime.now(),
                title="Campaign Health Declining",
                message=f"Overall health score dropped {abs(score_change)} points from {previous_health.overall_score} to {current_health.overall_score}",
                metric_name="health_score",
                current_value=float(current_health.overall_score),
                previous_value=float(previous_health.overall_score),
                threshold_value=float(previous_health.overall_score + self.THRESHOLDS["health_score_drop"]),
                percentage_change=(score_change / max(1, previous_health.overall_score)) * 100,
                absolute_change=float(score_change),
                affected_period="Current period",
                comparison_period="Previous period"
            )
            
            alerts.append(alert)
        
        return alerts
    
    def _generate_issue_alerts(
        self,
        issues: List[PerformanceIssue]
    ) -> List[Alert]:
        """Generate alerts from detected issues"""
        
        alerts = []
        
        # Create alerts for critical and high severity issues
        for issue in issues:
            if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
                
                alert = Alert(
                    alert_id=self._next_id(),
                    campaign_id=self.config.campaign_id,
                    alert_type=f"issue_{issue.issue_type.value}",
                    severity=issue.severity,
                    triggered_at=datetime.now(),
                    title=f"{issue.severity.value.upper()}: {issue.issue_type.value.replace('_', ' ').title()}",
                    message=f"{issue.root_cause}. Impact: ${issue.revenue_impact:,.0f} revenue at risk.",
                    metric_name=issue.issue_type.value,
                    current_value=float(issue.affected_calls),
                    previous_value=0.0,  # No previous value for issue-based alerts
                    threshold_value=0.0,
                    percentage_change=0.0,
                    absolute_change=float(issue.affected_calls),
                    affected_period="Current period",
                    comparison_period="N/A"
                )
                
                alerts.append(alert)
        
        return alerts
    
    def _format_period(self, metrics: PerformanceMetrics) -> str:
        """Format period for display"""
        start = metrics.period_start.strftime("%Y-%m-%d")
        end = metrics.period_end.strftime("%Y-%m-%d")
        return f"{start} to {end}"
    
    def _next_id(self) -> str:
        """Generate next alert ID"""
        self.alert_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ALERT_{self.config.campaign_id}_{timestamp}_{self.alert_counter:04d}"
    
    def get_critical_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """Filter to only critical alerts"""
        return [a for a in alerts if a.severity == IssueSeverity.CRITICAL]
    
    def format_alert_summary(self, alerts: List[Alert]) -> str:
        """
        Create a formatted summary of alerts
        
        Returns:
            Human-readable alert summary
        """
        
        if not alerts:
            return "✓ No alerts - campaign performing normally"
        
        critical = sum(1 for a in alerts if a.severity == IssueSeverity.CRITICAL)
        high = sum(1 for a in alerts if a.severity == IssueSeverity.HIGH)
        medium = sum(1 for a in alerts if a.severity == IssueSeverity.MEDIUM)
        
        summary_lines = [
            f"⚠️ {len(alerts)} ACTIVE ALERTS",
            ""
        ]
        
        if critical > 0:
            summary_lines.append(f"🔴 CRITICAL: {critical}")
        if high > 0:
            summary_lines.append(f"🟠 HIGH: {high}")
        if medium > 0:
            summary_lines.append(f"🟡 MEDIUM: {medium}")
        
        summary_lines.append("")
        summary_lines.append("Top Alerts:")
        
        # Show top 3 most severe alerts
        top_alerts = sorted(
            alerts,
            key=lambda a: (
                0 if a.severity == IssueSeverity.CRITICAL else
                1 if a.severity == IssueSeverity.HIGH else 2
            )
        )[:3]
        
        for i, alert in enumerate(top_alerts, 1):
            summary_lines.append(f"{i}. {alert.title} - {alert.message}")
        
        return "\n".join(summary_lines)
