"""
Voice Bot Intelligence Tool - Revenue Calculator
=================================================
Calculates revenue leakage, identifies where money is being lost,
and quantifies the impact of each issue.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

from models import (
    CallRecord, CampaignConfig, PerformanceMetrics, PerformanceIssue,
    CallStatus, DropOffStage
)


@dataclass
class RevenueLeakageBreakdown:
    """Detailed breakdown of where revenue is being lost"""
    total_leakage: float
    leakage_by_reason: Dict[str, float]
    leakage_by_stage: Dict[str, float]
    recoverable_amount: float
    recovery_difficulty: str  # "easy", "medium", "hard"
    
    # Top leakage sources
    top_3_reasons: List[Tuple[str, float]]
    
    # Potential recovery scenarios
    if_conversion_improved: float
    if_dropoff_reduced: float
    if_escalations_handled: float


class RevenueCalculator:
    """
    Calculates detailed revenue metrics and leakage analysis
    """
    
    def __init__(self, config: CampaignConfig):
        """Initialize calculator with campaign configuration"""
        self.config = config
    
    def calculate_leakage(
        self, 
        calls: List[CallRecord],
        metrics: PerformanceMetrics
    ) -> RevenueLeakageBreakdown:
        """
        Calculate detailed revenue leakage breakdown
        
        Args:
            calls: Raw call records
            metrics: Calculated performance metrics
            
        Returns:
            Detailed revenue leakage breakdown
        """
        
        # Calculate leakage by reason
        leakage_by_reason = {
            "dropped_calls": self._calculate_dropoff_leakage(calls),
            "low_conversion": self._calculate_conversion_leakage(calls, metrics),
            "escalation_cost": self._calculate_escalation_cost(calls),
            "technical_failures": self._calculate_failure_leakage(calls),
            "compliance_violations": self._calculate_compliance_cost(calls)
        }
        
        # Calculate leakage by funnel stage
        leakage_by_stage = self._calculate_stage_leakage(calls)
        
        # Total leakage
        total_leakage = sum(leakage_by_reason.values())
        
        # Estimate recoverable amount
        recoverable, difficulty = self._estimate_recoverable_revenue(leakage_by_reason)
        
        # Get top 3 leakage sources
        top_3 = sorted(leakage_by_reason.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Calculate recovery scenarios
        scenarios = self._calculate_recovery_scenarios(calls, metrics)
        
        return RevenueLeakageBreakdown(
            total_leakage=total_leakage,
            leakage_by_reason=leakage_by_reason,
            leakage_by_stage=leakage_by_stage,
            recoverable_amount=recoverable,
            recovery_difficulty=difficulty,
            top_3_reasons=top_3,
            if_conversion_improved=scenarios["conversion"],
            if_dropoff_reduced=scenarios["dropoff"],
            if_escalations_handled=scenarios["escalation"]
        )
    
    def calculate_issue_revenue_impact(
        self,
        issue: PerformanceIssue,
        calls: List[CallRecord]
    ) -> Dict[str, float]:
        """
        Calculate detailed revenue impact of a specific issue
        
        Args:
            issue: The performance issue to analyze
            calls: Raw call records
            
        Returns:
            Dictionary with revenue impact breakdown
        """
        from models import IssueType
        
        if issue.issue_type == IssueType.LOW_CONVERSION:
            return self._conversion_issue_impact(issue, calls)
        
        elif issue.issue_type == IssueType.HIGH_DROP_OFF:
            return self._dropoff_issue_impact(issue, calls)
        
        elif issue.issue_type == IssueType.ESCALATION_SPIKE:
            return self._escalation_issue_impact(issue, calls)
        
        elif issue.issue_type == IssueType.COMPLIANCE_RISK:
            return self._compliance_issue_impact(issue, calls)
        
        elif issue.issue_type == IssueType.TECHNICAL_ERROR:
            return self._technical_issue_impact(issue, calls)
        
        return {
            "direct_loss": 0.0,
            "opportunity_cost": 0.0,
            "operational_cost": 0.0,
            "total_impact": 0.0
        }
    
    def _calculate_dropoff_leakage(self, calls: List[CallRecord]) -> float:
        """Calculate revenue lost from dropped calls"""
        dropped_calls = [c for c in calls if c.status == CallStatus.DROPPED]
        
        # Assume 30% of dropped calls would have converted
        # (conservative estimate since they showed initial interest)
        estimated_conversions = len(dropped_calls) * 0.30 * self.config.target_conversion_rate
        leakage = estimated_conversions * self.config.avg_deal_value
        
        return leakage
    
    def _calculate_conversion_leakage(
        self, 
        calls: List[CallRecord],
        metrics: PerformanceMetrics
    ) -> float:
        """Calculate revenue lost from low conversion rate"""
        
        # Get completed calls that didn't convert
        completed_no_conversion = [
            c for c in calls 
            if c.status == CallStatus.COMPLETED and c.actual_revenue == 0
        ]
        
        # Expected conversions from completed calls
        expected = len(completed_no_conversion) * self.config.target_conversion_rate
        leakage = expected * self.config.avg_deal_value
        
        return leakage
    
    def _calculate_escalation_cost(self, calls: List[CallRecord]) -> float:
        """Calculate cost of escalations (not direct revenue loss but operational cost)"""
        escalated = [c for c in calls if c.status == CallStatus.ESCALATED]
        
        # Cost per escalation (human agent time + potential revenue impact)
        # $50 agent time + potential 20% revenue reduction from delayed response
        cost_per_escalation = 50 + (self.config.avg_deal_value * 0.20)
        
        return len(escalated) * cost_per_escalation
    
    def _calculate_failure_leakage(self, calls: List[CallRecord]) -> float:
        """Calculate revenue lost from technical failures"""
        failed = [c for c in calls if c.status == CallStatus.FAILED]
        
        # Failed calls represent complete lost opportunity
        leakage = len(failed) * self.config.target_conversion_rate * self.config.avg_deal_value
        
        return leakage
    
    def _calculate_compliance_cost(self, calls: List[CallRecord]) -> float:
        """Calculate cost of compliance violations"""
        violations = [c for c in calls if c.status == CallStatus.COMPLIANCE_VIOLATION]
        
        # Cost per violation: potential fines ($500) + lost deal
        cost_per_violation = 500 + self.config.avg_deal_value
        
        return len(violations) * cost_per_violation
    
    def _calculate_stage_leakage(self, calls: List[CallRecord]) -> Dict[str, float]:
        """Calculate revenue leakage by funnel stage"""
        stage_leakage = {}
        
        for stage in DropOffStage:
            stage_drops = [c for c in calls if c.drop_off_stage == stage]
            
            # Calculate potential revenue from these drops
            # Use declining conversion probability as we move through funnel
            stage_conversion_probability = {
                DropOffStage.INTRO: 0.10,  # Low probability, early stage
                DropOffStage.QUALIFICATION: 0.20,
                DropOffStage.PITCH: 0.30,
                DropOffStage.OBJECTION_HANDLING: 0.40,
                DropOffStage.CLOSING: 0.60,  # High probability, late stage
                DropOffStage.FOLLOW_UP: 0.50
            }
            
            prob = stage_conversion_probability.get(stage, 0.25)
            leakage = len(stage_drops) * prob * self.config.avg_deal_value
            
            if leakage > 0:
                stage_leakage[stage.value] = leakage
        
        return stage_leakage
    
    def _estimate_recoverable_revenue(
        self, 
        leakage_by_reason: Dict[str, float]
    ) -> Tuple[float, str]:
        """
        Estimate how much revenue is recoverable and how difficult
        
        Returns:
            (recoverable_amount, difficulty_level)
        """
        
        # Recovery potential by leakage type
        recovery_potential = {
            "dropped_calls": 0.60,        # 60% recoverable - script improvements
            "low_conversion": 0.50,       # 50% recoverable - better pitch/objection handling
            "escalation_cost": 0.40,      # 40% recoverable - better bot training
            "technical_failures": 0.90,   # 90% recoverable - fix technical issues
            "compliance_violations": 0.80  # 80% recoverable - script compliance fixes
        }
        
        # Calculate weighted recoverable amount
        recoverable = sum(
            leakage * recovery_potential.get(reason, 0.50)
            for reason, leakage in leakage_by_reason.items()
        )
        
        # Determine difficulty based on primary leakage source
        max_leakage_source = max(leakage_by_reason.items(), key=lambda x: x[1])[0]
        
        difficulty_map = {
            "technical_failures": "easy",      # Technical fixes are straightforward
            "compliance_violations": "easy",   # Script updates are straightforward
            "dropped_calls": "medium",         # Requires script iteration and testing
            "low_conversion": "medium",        # Requires pitch refinement
            "escalation_cost": "hard"          # Requires significant bot intelligence improvement
        }
        
        difficulty = difficulty_map.get(max_leakage_source, "medium")
        
        return recoverable, difficulty
    
    def _calculate_recovery_scenarios(
        self,
        calls: List[CallRecord],
        metrics: PerformanceMetrics
    ) -> Dict[str, float]:
        """Calculate revenue recovery under different improvement scenarios"""
        
        scenarios = {}
        
        # Scenario 1: Improve conversion rate to target
        if metrics.conversion_rate < self.config.target_conversion_rate:
            additional_conversions = (
                (self.config.target_conversion_rate - metrics.conversion_rate) * 
                metrics.total_calls
            )
            scenarios["conversion"] = additional_conversions * self.config.avg_deal_value
        else:
            scenarios["conversion"] = 0.0
        
        # Scenario 2: Reduce drop-off by 50%
        if metrics.dropped_calls > 0:
            recovered_calls = metrics.dropped_calls * 0.50
            scenarios["dropoff"] = (
                recovered_calls * 
                self.config.target_conversion_rate * 
                self.config.avg_deal_value
            )
        else:
            scenarios["dropoff"] = 0.0
        
        # Scenario 3: Handle escalations better (keep 70% of escalations in bot)
        if metrics.escalated_calls > 0:
            kept_in_bot = metrics.escalated_calls * 0.70
            # Assume 50% of those would convert vs 70% with human agent
            saved_cost = kept_in_bot * 50  # Agent cost savings
            revenue_diff = kept_in_bot * (0.50 - 0.70) * self.config.avg_deal_value  # Lower conversion
            scenarios["escalation"] = saved_cost + revenue_diff
        else:
            scenarios["escalation"] = 0.0
        
        return scenarios
    
    def _conversion_issue_impact(
        self,
        issue: PerformanceIssue,
        calls: List[CallRecord]
    ) -> Dict[str, float]:
        """Calculate impact of conversion issue"""
        
        # Direct loss: Expected conversions - Actual conversions
        direct_loss = issue.revenue_impact
        
        # Opportunity cost: Could have converted more if running optimally
        opportunity_cost = direct_loss * 0.30  # 30% additional upside
        
        return {
            "direct_loss": direct_loss,
            "opportunity_cost": opportunity_cost,
            "operational_cost": 0.0,
            "total_impact": direct_loss + opportunity_cost
        }
    
    def _dropoff_issue_impact(
        self,
        issue: PerformanceIssue,
        calls: List[CallRecord]
    ) -> Dict[str, float]:
        """Calculate impact of drop-off issue"""
        
        direct_loss = issue.revenue_impact
        
        # Opportunity cost from lost leads
        opportunity_cost = direct_loss * 0.50
        
        return {
            "direct_loss": direct_loss,
            "opportunity_cost": opportunity_cost,
            "operational_cost": 0.0,
            "total_impact": direct_loss + opportunity_cost
        }
    
    def _escalation_issue_impact(
        self,
        issue: PerformanceIssue,
        calls: List[CallRecord]
    ) -> Dict[str, float]:
        """Calculate impact of escalation issue"""
        
        # Escalations are primarily operational cost
        operational_cost = issue.revenue_impact  # Already calculated as agent costs
        
        # But there's also opportunity cost from delayed response
        escalated = [c for c in calls if c.status == CallStatus.ESCALATED]
        opportunity_cost = len(escalated) * 0.10 * self.config.avg_deal_value
        
        return {
            "direct_loss": 0.0,
            "opportunity_cost": opportunity_cost,
            "operational_cost": operational_cost,
            "total_impact": operational_cost + opportunity_cost
        }
    
    def _compliance_issue_impact(
        self,
        issue: PerformanceIssue,
        calls: List[CallRecord]
    ) -> Dict[str, float]:
        """Calculate impact of compliance issue"""
        
        # Compliance has both direct cost and huge risk
        direct_loss = issue.revenue_impact
        
        # Risk multiplier for brand damage
        risk_cost = direct_loss * 2.0  # Compliance issues can have 2x the financial impact
        
        return {
            "direct_loss": direct_loss,
            "opportunity_cost": 0.0,
            "operational_cost": risk_cost,
            "total_impact": direct_loss + risk_cost
        }
    
    def _technical_issue_impact(
        self,
        issue: PerformanceIssue,
        calls: List[CallRecord]
    ) -> Dict[str, float]:
        """Calculate impact of technical issue"""
        
        # Technical failures are complete lost opportunities
        direct_loss = issue.revenue_impact
        
        # Plus operational cost of engineering time to fix
        operational_cost = 5000  # Estimated engineering cost
        
        return {
            "direct_loss": direct_loss,
            "opportunity_cost": 0.0,
            "operational_cost": operational_cost,
            "total_impact": direct_loss + operational_cost
        }
    
    def calculate_weekly_revenue_trend(
        self,
        current_week_revenue: float,
        previous_week_revenue: float
    ) -> Dict[str, any]:
        """
        Calculate week-over-week revenue trends
        
        Returns:
            Dictionary with trend metrics
        """
        
        if previous_week_revenue == 0:
            return {
                "change_amount": current_week_revenue,
                "change_percentage": 100.0 if current_week_revenue > 0 else 0.0,
                "trend": "new",
                "alert_needed": False
            }
        
        change_amount = current_week_revenue - previous_week_revenue
        change_pct = (change_amount / previous_week_revenue) * 100
        
        # Determine trend
        if change_pct > 5:
            trend = "improving"
        elif change_pct < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        # Alert if revenue drops >10%
        alert_needed = change_pct < -10
        
        return {
            "change_amount": change_amount,
            "change_percentage": change_pct,
            "trend": trend,
            "alert_needed": alert_needed
        }
