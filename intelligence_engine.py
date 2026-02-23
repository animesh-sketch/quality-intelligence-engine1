"""
Voice Bot Intelligence Tool - Main Intelligence Engine
=======================================================
Orchestrates all modules to provide complete campaign intelligence,
recommendations, and actionable insights.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta

from models import (
    CallRecord, CampaignConfig, IntelligenceReport,
    PerformanceMetrics, PerformanceIssue, ActionableRecommendation,
    HealthScore, Alert, IssueSeverity
)
from performance_analyzer import PerformanceAnalyzer
from revenue_calculator import RevenueCalculator, RevenueLeakageBreakdown
from recommendation_engine import RecommendationEngine
from health_scorer import HealthScorer
from alert_system import AlertSystem


class VoiceBotIntelligence:
    """
    Main intelligence engine that coordinates all analysis modules
    to provide comprehensive campaign insights
    """
    
    def __init__(self, campaign_config: CampaignConfig):
        """
        Initialize intelligence engine with campaign configuration
        
        Args:
            campaign_config: Campaign configuration and targets
        """
        self.config = campaign_config
        
        # Initialize all modules
        self.analyzer = PerformanceAnalyzer(campaign_config)
        self.revenue_calc = RevenueCalculator(campaign_config)
        self.recommender = RecommendationEngine(campaign_config)
        self.health_scorer = HealthScorer(campaign_config)
        self.alert_system = AlertSystem(campaign_config)
    
    def analyze_campaign(
        self,
        current_calls: List[CallRecord],
        previous_calls: Optional[List[CallRecord]] = None
    ) -> IntelligenceReport:
        """
        Generate complete intelligence report for campaign
        
        Args:
            current_calls: Call records from current period
            previous_calls: Call records from previous period (for WoW comparison)
            
        Returns:
            Complete intelligence report with all insights
        """
        
        # Step 1: Calculate performance metrics
        print("📊 Calculating performance metrics...")
        current_metrics = self.analyzer.calculate_metrics(current_calls)
        previous_metrics = (
            self.analyzer.calculate_metrics(previous_calls)
            if previous_calls else None
        )
        
        # Step 2: Detect performance issues
        print("🔍 Detecting performance issues...")
        issues = self.analyzer.detect_issues(current_metrics, current_calls)
        
        # Step 3: Calculate revenue leakage
        print("💰 Calculating revenue leakage...")
        leakage = self.revenue_calc.calculate_leakage(current_calls, current_metrics)
        
        # Step 4: Generate recommendations
        print("💡 Generating actionable recommendations...")
        recommendations = self.recommender.generate_recommendations(issues)
        
        # Step 5: Calculate health score
        print("📈 Calculating campaign health score...")
        current_health = self.health_scorer.calculate_health(
            current_metrics,
            previous_metrics,
            issues
        )
        
        previous_health = None
        if previous_metrics:
            previous_health = self.health_scorer.calculate_health(previous_metrics)
        
        # Step 6: Generate alerts
        print("🚨 Generating alerts...")
        alerts = []
        if previous_metrics:
            alerts = self.alert_system.generate_alerts(
                current_metrics,
                previous_metrics,
                current_health,
                previous_health,
                issues
            )
        
        # Step 7: Calculate week-over-week changes
        wow_changes = self._calculate_wow_changes(current_metrics, previous_metrics)
        
        # Step 8: Generate executive summary
        summary = self._generate_executive_summary(
            current_metrics,
            current_health,
            issues,
            leakage,
            alerts
        )
        
        # Step 9: Generate key insights
        key_insights = self._generate_key_insights(
            current_metrics,
            issues,
            leakage,
            recommendations,
            alerts
        )
        
        # Step 10: Identify urgent actions
        urgent_actions = self._identify_urgent_actions(
            issues,
            recommendations,
            alerts
        )
        
        # Create comprehensive report
        report = IntelligenceReport(
            campaign_id=self.config.campaign_id,
            report_date=datetime.now(),
            period_analyzed=self._format_period(current_metrics),
            performance_metrics=current_metrics,
            health_score=current_health,
            issues=issues,
            recommendations=recommendations,
            active_alerts=alerts,
            week_over_week_changes=wow_changes,
            summary=summary,
            key_insights=key_insights,
            urgent_actions=urgent_actions
        )
        
        print("✅ Intelligence report generated successfully!")
        return report
    
    def get_quick_status(self, calls: List[CallRecord]) -> Dict[str, any]:
        """
        Quick campaign status check (lightweight version)
        
        Args:
            calls: Recent call records
            
        Returns:
            Dictionary with key status indicators
        """
        
        metrics = self.analyzer.calculate_metrics(calls)
        health = self.health_scorer.calculate_health(metrics)
        
        return {
            "campaign_id": self.config.campaign_id,
            "health_score": health.overall_score,
            "health_status": health.health_status(),
            "total_calls": metrics.total_calls,
            "conversion_rate": f"{metrics.conversion_rate:.1%}",
            "total_revenue": f"${metrics.total_revenue:,.0f}",
            "revenue_leakage": f"${metrics.revenue_leakage:,.0f}",
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_specific_issue(
        self,
        issue: PerformanceIssue,
        calls: List[CallRecord]
    ) -> Dict[str, any]:
        """
        Deep dive analysis of a specific issue
        
        Args:
            issue: The issue to analyze
            calls: Related call records
            
        Returns:
            Detailed issue analysis
        """
        
        # Calculate detailed revenue impact
        revenue_impact = self.revenue_calc.calculate_issue_revenue_impact(issue, calls)
        
        # Generate specific recommendations
        recommendations = self.recommender._generate_for_issue(issue)
        
        return {
            "issue": issue,
            "revenue_impact_breakdown": revenue_impact,
            "recommendations": recommendations,
            "affected_calls_percentage": (issue.affected_calls / len(calls) * 100) if calls else 0
        }
    
    def _calculate_wow_changes(
        self,
        current: PerformanceMetrics,
        previous: Optional[PerformanceMetrics]
    ) -> Dict[str, float]:
        """Calculate week-over-week percentage changes"""
        
        if not previous:
            return {}
        
        changes = {}
        
        # Revenue change
        if previous.total_revenue > 0:
            changes["revenue"] = (
                (current.total_revenue - previous.total_revenue) / 
                previous.total_revenue * 100
            )
        
        # Conversion rate change
        if previous.conversion_rate > 0:
            changes["conversion_rate"] = (
                (current.conversion_rate - previous.conversion_rate) / 
                previous.conversion_rate * 100
            )
        
        # Call volume change
        if previous.total_calls > 0:
            changes["call_volume"] = (
                (current.total_calls - previous.total_calls) / 
                previous.total_calls * 100
            )
        
        # Drop-off rate change
        current_dropoff = current.dropped_calls / current.total_calls if current.total_calls > 0 else 0
        previous_dropoff = previous.dropped_calls / previous.total_calls if previous.total_calls > 0 else 0
        
        if previous_dropoff > 0:
            changes["drop_off_rate"] = (
                (current_dropoff - previous_dropoff) / 
                previous_dropoff * 100
            )
        
        return changes
    
    def _generate_executive_summary(
        self,
        metrics: PerformanceMetrics,
        health: HealthScore,
        issues: List[PerformanceIssue],
        leakage: RevenueLeakageBreakdown,
        alerts: List[Alert]
    ) -> str:
        """Generate executive summary of campaign performance"""
        
        summary_parts = []
        
        # Overall status
        summary_parts.append(
            f"Campaign '{self.config.campaign_name}' health score: {health.overall_score}/100 ({health.health_status()})"
        )
        
        # Revenue performance
        revenue_vs_target = (metrics.total_revenue / (self.config.expected_daily_revenue() * 7)) * 100
        summary_parts.append(
            f"Revenue: ${metrics.total_revenue:,.0f} ({revenue_vs_target:.0f}% of target) "
            f"with ${metrics.revenue_leakage:,.0f} in leakage ({metrics.revenue_leakage_percentage:.1f}%)"
        )
        
        # Conversion performance
        summary_parts.append(
            f"Conversion rate: {metrics.conversion_rate:.1%} "
            f"(target: {self.config.target_conversion_rate:.1%}) "
            f"from {metrics.total_calls} calls"
        )
        
        # Critical issues
        critical_issues = [i for i in issues if i.severity == IssueSeverity.CRITICAL]
        if critical_issues:
            summary_parts.append(
                f"⚠️ {len(critical_issues)} CRITICAL issues requiring immediate attention"
            )
        
        # Critical alerts
        critical_alerts = [a for a in alerts if a.is_critical()]
        if critical_alerts:
            summary_parts.append(
                f"🚨 {len(critical_alerts)} CRITICAL alerts triggered"
            )
        
        # Recovery opportunity
        summary_parts.append(
            f"Recovery opportunity: ${leakage.recoverable_amount:,.0f} "
            f"({leakage.recovery_difficulty} difficulty)"
        )
        
        return " | ".join(summary_parts)
    
    def _generate_key_insights(
        self,
        metrics: PerformanceMetrics,
        issues: List[PerformanceIssue],
        leakage: RevenueLeakageBreakdown,
        recommendations: List[ActionableRecommendation],
        alerts: List[Alert]
    ) -> List[str]:
        """Generate key insights from analysis"""
        
        insights = []
        
        # Top leakage source
        if leakage.top_3_reasons:
            top_reason, top_amount = leakage.top_3_reasons[0]
            insights.append(
                f"Largest revenue leak: {top_reason.replace('_', ' ').title()} "
                f"(${top_amount:,.0f}, {(top_amount/leakage.total_leakage*100):.0f}% of total leakage)"
            )
        
        # Conversion opportunity
        if metrics.conversion_rate < self.config.target_conversion_rate:
            gap = self.config.target_conversion_rate - metrics.conversion_rate
            potential = gap * metrics.total_calls * self.config.avg_deal_value
            insights.append(
                f"Closing conversion gap to target would recover ${potential:,.0f}"
            )
        
        # Drop-off pattern
        if metrics.drop_off_by_stage:
            worst_stage = max(metrics.drop_off_by_stage.items(), key=lambda x: x[1])
            insights.append(
                f"Highest drop-off at '{worst_stage[0]}' stage ({worst_stage[1]} calls)"
            )
        
        # Top recommendation
        if recommendations:
            top_rec = recommendations[0]
            insights.append(
                f"Top recommendation: {top_rec.action} (${top_rec.expected_revenue_recovery:,.0f} potential recovery)"
            )
        
        # Trend insight
        if alerts:
            declining_alerts = [a for a in alerts if "drop" in a.alert_type.lower() or "declining" in a.message.lower()]
            if declining_alerts:
                insights.append(
                    f"Performance declining in {len(declining_alerts)} key metrics - immediate action needed"
                )
        
        return insights
    
    def _identify_urgent_actions(
        self,
        issues: List[PerformanceIssue],
        recommendations: List[ActionableRecommendation],
        alerts: List[Alert]
    ) -> List[str]:
        """Identify most urgent actions needed"""
        
        urgent = []
        
        # Critical compliance issues
        from models import IssueType, IssueSeverity
        compliance_issues = [
            i for i in issues 
            if i.issue_type == IssueType.COMPLIANCE_RISK
        ]
        
        if compliance_issues:
            urgent.append(
                "IMMEDIATE: Fix compliance violations to avoid regulatory risk"
            )
        
        # Critical alerts
        critical_alerts = [a for a in alerts if a.severity == IssueSeverity.CRITICAL]
        if critical_alerts:
            for alert in critical_alerts[:2]:  # Top 2 critical alerts
                urgent.append(f"CRITICAL: {alert.title}")
        
        # High-priority, high-impact recommendations
        high_impact_recs = [
            r for r in recommendations
            if r.priority == 1 and r.expected_revenue_recovery > 10000
        ]
        
        for rec in high_impact_recs[:3]:  # Top 3
            urgent.append(
                f"Priority {rec.priority}: {rec.action} "
                f"(${rec.expected_revenue_recovery:,.0f} recovery, {rec.estimated_time})"
            )
        
        if not urgent:
            urgent.append("No urgent actions - continue monitoring performance")
        
        return urgent
    
    def _format_period(self, metrics: PerformanceMetrics) -> str:
        """Format analysis period"""
        start = metrics.period_start.strftime("%Y-%m-%d")
        end = metrics.period_end.strftime("%Y-%m-%d")
        return f"{start} to {end}"
    
    def export_report_summary(self, report: IntelligenceReport) -> str:
        """
        Export report as formatted text summary
        
        Args:
            report: Intelligence report to export
            
        Returns:
            Formatted text summary
        """
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"VOICE BOT INTELLIGENCE REPORT - {self.config.campaign_name}")
        lines.append("=" * 80)
        lines.append(f"Report Date: {report.report_date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Period: {report.period_analyzed}")
        lines.append("")
        
        # Executive Summary
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 80)
        lines.append(report.summary)
        lines.append("")
        
        # Health Score
        lines.append("HEALTH SCORE")
        lines.append("-" * 80)
        lines.append(f"Overall: {report.health_score.overall_score}/100 ({report.health_score.health_status()})")
        lines.append(f"  Conversion Health: {report.health_score.conversion_health}/100")
        lines.append(f"  Revenue Health: {report.health_score.revenue_health}/100")
        lines.append(f"  Compliance Health: {report.health_score.compliance_health}/100")
        lines.append(f"  Efficiency Health: {report.health_score.efficiency_health}/100")
        lines.append(f"  Quality Health: {report.health_score.quality_health}/100")
        lines.append(f"Trend: {report.health_score.trend.upper()} ({report.health_score.week_over_week_change:+.1f}% WoW)")
        lines.append("")
        
        # Key Metrics
        lines.append("KEY METRICS")
        lines.append("-" * 80)
        m = report.performance_metrics
        lines.append(f"Total Calls: {m.total_calls:,}")
        lines.append(f"Conversion Rate: {m.conversion_rate:.1%} (target: {self.config.target_conversion_rate:.1%})")
        lines.append(f"Revenue: ${m.total_revenue:,.0f}")
        lines.append(f"Revenue Leakage: ${m.revenue_leakage:,.0f} ({m.revenue_leakage_percentage:.1f}%)")
        lines.append(f"Completion Rate: {m.completion_rate():.1%}")
        lines.append(f"Escalation Rate: {m.escalation_rate():.1%}")
        lines.append("")
        
        # Alerts
        if report.active_alerts:
            lines.append("ACTIVE ALERTS")
            lines.append("-" * 80)
            for alert in report.active_alerts[:5]:  # Top 5
                lines.append(f"[{alert.severity.value.upper()}] {alert.title}")
                lines.append(f"  {alert.message}")
            lines.append("")
        
        # Issues
        if report.issues:
            lines.append("DETECTED ISSUES")
            lines.append("-" * 80)
            for issue in report.issues[:5]:  # Top 5
                lines.append(f"[{issue.severity.value.upper()}] {issue.issue_type.value.replace('_', ' ').title()}")
                lines.append(f"  {issue.root_cause}")
                lines.append(f"  Impact: ${issue.revenue_impact:,.0f}, {issue.affected_calls} calls")
            lines.append("")
        
        # Urgent Actions
        lines.append("URGENT ACTIONS REQUIRED")
        lines.append("-" * 80)
        for i, action in enumerate(report.urgent_actions, 1):
            lines.append(f"{i}. {action}")
        lines.append("")
        
        # Top Recommendations
        lines.append("TOP RECOMMENDATIONS")
        lines.append("-" * 80)
        for rec in report.recommendations[:3]:  # Top 3
            lines.append(f"Priority {rec.priority}: {rec.action}")
            lines.append(f"  Expected Impact: {rec.expected_impact}")
            lines.append(f"  Effort: {rec.implementation_effort}, Time: {rec.estimated_time}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
