"""
Voice Bot Intelligence Tool - Health Scorer
============================================
Calculates comprehensive health score (0-100) for campaigns
with component breakdowns and trend analysis.
"""

from typing import Dict, List, Tuple
from datetime import datetime

from models import (
    PerformanceMetrics, HealthScore, CampaignConfig,
    PerformanceIssue, IssueSeverity
)


class HealthScorer:
    """
    Calculates campaign health scores with detailed component breakdowns
    """
    
    # Weight distribution for overall score (must sum to 1.0)
    WEIGHTS = {
        "conversion": 0.35,      # 35% - Most important for revenue
        "revenue": 0.25,         # 25% - Direct business impact
        "compliance": 0.20,      # 20% - Risk management
        "efficiency": 0.12,      # 12% - Operational efficiency
        "quality": 0.08          # 8% - Customer experience
    }
    
    # Benchmarks for scoring
    BENCHMARKS = {
        "conversion_rate": 0.15,        # 15%
        "completion_rate": 0.70,        # 70%
        "escalation_rate": 0.10,        # 10%
        "compliance_rate": 0.98,        # 98%
        "avg_sentiment": 0.30,          # 0.30 (positive)
        "revenue_efficiency": 1.0       # 100% of expected revenue
    }
    
    def __init__(self, config: CampaignConfig):
        """Initialize scorer with campaign configuration"""
        self.config = config
    
    def calculate_health(
        self,
        current_metrics: PerformanceMetrics,
        previous_metrics: PerformanceMetrics = None,
        issues: List[PerformanceIssue] = None
    ) -> HealthScore:
        """
        Calculate comprehensive health score
        
        Args:
            current_metrics: Current period performance metrics
            previous_metrics: Previous period metrics for trend analysis (optional)
            issues: Detected issues to factor into scoring (optional)
            
        Returns:
            HealthScore object with overall score and component breakdowns
        """
        
        # Calculate component scores
        conversion_health = self._score_conversion(current_metrics)
        revenue_health = self._score_revenue(current_metrics)
        compliance_health = self._score_compliance(current_metrics)
        efficiency_health = self._score_efficiency(current_metrics)
        quality_health = self._score_quality(current_metrics)
        
        # Apply issue penalties if issues detected
        if issues:
            conversion_health = self._apply_issue_penalty(conversion_health, issues, "conversion")
            revenue_health = self._apply_issue_penalty(revenue_health, issues, "revenue")
            compliance_health = self._apply_issue_penalty(compliance_health, issues, "compliance")
        
        # Calculate weighted overall score
        overall_score = int(
            conversion_health * self.WEIGHTS["conversion"] +
            revenue_health * self.WEIGHTS["revenue"] +
            compliance_health * self.WEIGHTS["compliance"] +
            efficiency_health * self.WEIGHTS["efficiency"] +
            quality_health * self.WEIGHTS["quality"]
        )
        
        # Calculate trend and WoW change
        trend, wow_change = self._calculate_trend(current_metrics, previous_metrics)
        
        # Detailed component breakdown
        score_components = {
            "conversion_health": conversion_health,
            "revenue_health": revenue_health,
            "compliance_health": compliance_health,
            "efficiency_health": efficiency_health,
            "quality_health": quality_health,
            "conversion_weight": self.WEIGHTS["conversion"],
            "revenue_weight": self.WEIGHTS["revenue"],
            "compliance_weight": self.WEIGHTS["compliance"],
            "efficiency_weight": self.WEIGHTS["efficiency"],
            "quality_weight": self.WEIGHTS["quality"]
        }
        
        return HealthScore(
            campaign_id=self.config.campaign_id,
            calculated_at=datetime.now(),
            overall_score=overall_score,
            conversion_health=conversion_health,
            revenue_health=revenue_health,
            compliance_health=compliance_health,
            efficiency_health=efficiency_health,
            quality_health=quality_health,
            score_components=score_components,
            trend=trend,
            week_over_week_change=wow_change
        )
    
    def _score_conversion(self, metrics: PerformanceMetrics) -> int:
        """
        Score conversion performance (0-100)
        
        Factors:
        - Actual conversion rate vs target
        - Actual conversion rate vs benchmark
        - Completion rate (getting prospects to end of call)
        """
        
        # Base score from conversion rate
        target_rate = self.config.target_conversion_rate
        actual_rate = metrics.conversion_rate
        benchmark_rate = self.BENCHMARKS["conversion_rate"]
        
        # Score against target (60% of score)
        if target_rate > 0:
            target_score = min(100, (actual_rate / target_rate) * 100)
        else:
            target_score = 50
        
        # Score against benchmark (40% of score)
        benchmark_score = min(100, (actual_rate / benchmark_rate) * 100)
        
        conversion_score = (target_score * 0.60) + (benchmark_score * 0.40)
        
        # Bonus for high completion rate (more people hearing full pitch)
        completion_rate = metrics.completion_rate()
        if completion_rate > self.BENCHMARKS["completion_rate"]:
            completion_bonus = (completion_rate - self.BENCHMARKS["completion_rate"]) * 50
            conversion_score += completion_bonus
        
        return int(min(100, max(0, conversion_score)))
    
    def _score_revenue(self, metrics: PerformanceMetrics) -> int:
        """
        Score revenue performance (0-100)
        
        Factors:
        - Revenue vs expected
        - Revenue leakage percentage
        - Revenue per call efficiency
        """
        
        # Score based on revenue achievement
        if metrics.expected_revenue > 0:
            revenue_achievement = (metrics.total_revenue / metrics.expected_revenue)
            base_score = min(100, revenue_achievement * 100)
        else:
            base_score = 50
        
        # Penalty for revenue leakage
        leakage_penalty = metrics.revenue_leakage_percentage / 2  # Scale penalty
        
        revenue_score = base_score - leakage_penalty
        
        # Check revenue per call efficiency
        if metrics.total_calls > 0:
            revenue_per_call = metrics.total_revenue / metrics.total_calls
            expected_per_call = self.config.target_revenue_per_call
            
            if expected_per_call > 0:
                efficiency_ratio = revenue_per_call / expected_per_call
                
                # Bonus for exceeding per-call target
                if efficiency_ratio > 1.0:
                    efficiency_bonus = (efficiency_ratio - 1.0) * 20
                    revenue_score += efficiency_bonus
        
        return int(min(100, max(0, revenue_score)))
    
    def _score_compliance(self, metrics: PerformanceMetrics) -> int:
        """
        Score compliance performance (0-100)
        
        Compliance is critical - severe penalties for any violations
        """
        
        if metrics.total_calls == 0:
            return 100
        
        # Calculate compliance rate
        compliance_rate = 1 - (metrics.compliance_violations / metrics.total_calls)
        
        # Compliance scoring is strict
        if compliance_rate >= self.BENCHMARKS["compliance_rate"]:
            # Perfect or near-perfect compliance
            score = 95 + ((compliance_rate - self.BENCHMARKS["compliance_rate"]) * 500)
        elif compliance_rate >= 0.95:
            # Acceptable compliance
            score = 70 + ((compliance_rate - 0.95) * 833)  # Scale 95-98% to 70-95
        elif compliance_rate >= 0.90:
            # Poor compliance
            score = 40 + ((compliance_rate - 0.90) * 600)  # Scale 90-95% to 40-70
        else:
            # Critical compliance issues
            score = compliance_rate * 40  # Scale 0-90% to 0-40
        
        return int(min(100, max(0, score)))
    
    def _score_efficiency(self, metrics: PerformanceMetrics) -> int:
        """
        Score operational efficiency (0-100)
        
        Factors:
        - Call drop-off rate
        - Escalation rate
        - Technical failure rate
        """
        
        if metrics.total_calls == 0:
            return 100
        
        # Drop-off scoring (40% of efficiency score)
        drop_rate = metrics.dropped_calls / metrics.total_calls
        benchmark_completion = self.BENCHMARKS["completion_rate"]
        actual_completion = metrics.completion_rate()
        
        if benchmark_completion > 0:
            drop_score = (actual_completion / benchmark_completion) * 100
        else:
            drop_score = 50
        
        # Escalation scoring (40% of efficiency score)
        escalation_rate = metrics.escalation_rate()
        benchmark_escalation = self.BENCHMARKS["escalation_rate"]
        
        if escalation_rate <= benchmark_escalation:
            escalation_score = 100
        else:
            # Penalty for excess escalations
            excess = (escalation_rate - benchmark_escalation) / benchmark_escalation
            escalation_score = max(0, 100 - (excess * 100))
        
        # Technical failure scoring (20% of efficiency score)
        failure_rate = metrics.failed_calls / metrics.total_calls
        
        if failure_rate <= 0.02:  # <2% failures is acceptable
            failure_score = 100
        elif failure_rate <= 0.05:  # 2-5% is concerning
            failure_score = 60
        else:  # >5% is critical
            failure_score = max(0, 100 - (failure_rate * 500))
        
        efficiency_score = (
            drop_score * 0.40 +
            escalation_score * 0.40 +
            failure_score * 0.20
        )
        
        return int(min(100, max(0, efficiency_score)))
    
    def _score_quality(self, metrics: PerformanceMetrics) -> int:
        """
        Score call quality (0-100)
        
        Factors:
        - Average sentiment score
        - Average call duration (engagement indicator)
        """
        
        # Sentiment scoring (70% of quality score)
        avg_sentiment = metrics.avg_sentiment_score
        benchmark_sentiment = self.BENCHMARKS["avg_sentiment"]
        
        # Convert sentiment (-1 to 1) to 0-100 scale
        # Sentiment of 0.30 (benchmark) should score 70
        # Sentiment of 0.60+ should score 100
        if avg_sentiment >= benchmark_sentiment:
            sentiment_score = 70 + ((avg_sentiment - benchmark_sentiment) / 0.30) * 30
        elif avg_sentiment >= 0:
            sentiment_score = 50 + ((avg_sentiment / benchmark_sentiment) * 20)
        else:
            # Negative sentiment is very bad
            sentiment_score = 50 + (avg_sentiment * 50)
        
        # Duration scoring (30% of quality score)
        avg_duration = metrics.avg_call_duration
        
        # Ideal call duration: 3-5 minutes (180-300 seconds)
        if 180 <= avg_duration <= 300:
            duration_score = 100
        elif avg_duration < 180:
            # Too short = low engagement
            duration_score = (avg_duration / 180) * 100
        else:
            # Too long = inefficient
            duration_score = max(60, 100 - ((avg_duration - 300) / 60) * 10)
        
        quality_score = (sentiment_score * 0.70) + (duration_score * 0.30)
        
        return int(min(100, max(0, quality_score)))
    
    def _apply_issue_penalty(
        self,
        score: int,
        issues: List[PerformanceIssue],
        category: str
    ) -> int:
        """
        Apply penalties to component scores based on detected issues
        
        Args:
            score: Current component score
            issues: List of detected issues
            category: Which category to check ("conversion", "revenue", "compliance")
        """
        
        from models import IssueType
        
        # Map categories to issue types
        category_issues = {
            "conversion": [IssueType.LOW_CONVERSION, IssueType.HIGH_DROP_OFF],
            "revenue": [IssueType.LOW_CONVERSION, IssueType.HIGH_DROP_OFF],
            "compliance": [IssueType.COMPLIANCE_RISK]
        }
        
        relevant_issue_types = category_issues.get(category, [])
        
        # Calculate total penalty
        total_penalty = 0
        
        for issue in issues:
            if issue.issue_type in relevant_issue_types:
                # Penalty based on severity
                if issue.severity == IssueSeverity.CRITICAL:
                    penalty = 20
                elif issue.severity == IssueSeverity.HIGH:
                    penalty = 12
                elif issue.severity == IssueSeverity.MEDIUM:
                    penalty = 6
                else:
                    penalty = 2
                
                total_penalty += penalty
        
        # Apply penalty, but don't go below 0
        penalized_score = max(0, score - total_penalty)
        
        return penalized_score
    
    def _calculate_trend(
        self,
        current_metrics: PerformanceMetrics,
        previous_metrics: PerformanceMetrics = None
    ) -> Tuple[str, float]:
        """
        Calculate trend and week-over-week change
        
        Returns:
            (trend_status, wow_change_percentage)
        """
        
        if not previous_metrics:
            return "new", 0.0
        
        # Calculate previous period score (simplified - just use revenue)
        if previous_metrics.total_revenue == 0:
            return "improving", 100.0 if current_metrics.total_revenue > 0 else 0.0
        
        change_pct = (
            (current_metrics.total_revenue - previous_metrics.total_revenue) / 
            previous_metrics.total_revenue * 100
        )
        
        # Determine trend
        if change_pct > 5:
            trend = "improving"
        elif change_pct < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        return trend, change_pct
    
    def get_health_insights(self, health_score: HealthScore) -> List[str]:
        """
        Generate human-readable insights from health score
        
        Args:
            health_score: Calculated health score
            
        Returns:
            List of insight strings
        """
        
        insights = []
        
        # Overall health insight
        status = health_score.health_status()
        insights.append(f"Campaign health is {status} with overall score of {health_score.overall_score}/100")
        
        # Component insights
        components = [
            ("Conversion", health_score.conversion_health),
            ("Revenue", health_score.revenue_health),
            ("Compliance", health_score.compliance_health),
            ("Efficiency", health_score.efficiency_health),
            ("Quality", health_score.quality_health)
        ]
        
        # Identify strengths
        strengths = [name for name, score in components if score >= 80]
        if strengths:
            insights.append(f"Strong performance in: {', '.join(strengths)}")
        
        # Identify weaknesses
        weaknesses = [name for name, score in components if score < 60]
        if weaknesses:
            insights.append(f"Needs improvement in: {', '.join(weaknesses)}")
        
        # Critical alerts
        if health_score.compliance_health < 70:
            insights.append("⚠️ CRITICAL: Compliance issues detected - immediate attention required")
        
        if health_score.overall_score < 50:
            insights.append("⚠️ WARNING: Campaign health is poor - consider pausing for optimization")
        
        # Trend insight
        if health_score.trend == "improving":
            insights.append(f"✓ Positive trend: {health_score.week_over_week_change:+.1f}% improvement WoW")
        elif health_score.trend == "declining":
            insights.append(f"⚠️ Declining trend: {health_score.week_over_week_change:.1f}% decrease WoW")
        
        return insights
