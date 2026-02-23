"""
Voice Bot Intelligence Tool - Recommendation Engine
====================================================
Generates actionable recommendations to fix detected issues,
prioritizes actions, and estimates impact.
"""

from typing import List, Dict
from datetime import datetime

from models import (
    PerformanceIssue, ActionableRecommendation, IssueType,
    IssueSeverity, DropOffStage, CampaignConfig
)


class RecommendationEngine:
    """
    Generates prioritized, actionable recommendations for fixing issues
    """
    
    def __init__(self, config: CampaignConfig):
        """Initialize recommendation engine with campaign config"""
        self.config = config
        self.recommendation_counter = 0
    
    def generate_recommendations(
        self,
        issues: List[PerformanceIssue]
    ) -> List[ActionableRecommendation]:
        """
        Generate recommendations for all detected issues
        
        Args:
            issues: List of detected performance issues
            
        Returns:
            Prioritized list of actionable recommendations
        """
        
        recommendations = []
        
        for issue in issues:
            # Generate specific recommendations based on issue type
            issue_recommendations = self._generate_for_issue(issue)
            recommendations.extend(issue_recommendations)
        
        # Sort by priority (1 = highest priority)
        recommendations.sort(key=lambda r: (r.priority, -r.expected_revenue_recovery))
        
        return recommendations
    
    def _generate_for_issue(
        self,
        issue: PerformanceIssue
    ) -> List[ActionableRecommendation]:
        """Generate recommendations for a specific issue"""
        
        if issue.issue_type == IssueType.LOW_CONVERSION:
            return self._recommendations_for_conversion(issue)
        
        elif issue.issue_type == IssueType.HIGH_DROP_OFF:
            return self._recommendations_for_dropoff(issue)
        
        elif issue.issue_type == IssueType.ESCALATION_SPIKE:
            return self._recommendations_for_escalation(issue)
        
        elif issue.issue_type == IssueType.COMPLIANCE_RISK:
            return self._recommendations_for_compliance(issue)
        
        elif issue.issue_type == IssueType.TECHNICAL_ERROR:
            return self._recommendations_for_technical(issue)
        
        return []
    
    def _recommendations_for_conversion(
        self,
        issue: PerformanceIssue
    ) -> List[ActionableRecommendation]:
        """Generate recommendations for low conversion issues"""
        
        recommendations = []
        
        # Recommendation 1: A/B test improved pitch
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=self._calculate_priority(issue, 0.70),  # High potential
            action="A/B test an improved value proposition and pitch script",
            expected_impact=f"Potential to recover ${issue.revenue_impact * 0.40:,.0f} (40% of lost revenue)",
            implementation_effort="medium",
            steps=[
                "Analyze top 20 successful calls to identify winning patterns",
                "Rewrite pitch focusing on customer pain points mentioned in successful calls",
                "Create 2-3 variations of the pitch with different value propositions",
                "Run A/B test with 20% traffic for 3 days",
                "Roll out winning variant to 100% traffic"
            ],
            resources_needed=[
                "Copywriter or script optimization specialist",
                "Access to call recordings and transcripts",
                "A/B testing capability in bot platform"
            ],
            estimated_time="3-5 days",
            expected_revenue_recovery=issue.revenue_impact * 0.40,
            expected_conversion_lift=0.25,  # 25% improvement
            confidence_score=0.70
        ))
        
        # Recommendation 2: Improve objection handling
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=self._calculate_priority(issue, 0.65),
            action="Enhance objection handling with dynamic responses",
            expected_impact=f"Potential to recover ${issue.revenue_impact * 0.30:,.0f} (30% of lost revenue)",
            implementation_effort="medium",
            steps=[
                "Identify top 10 objections from call transcripts",
                "Create compelling responses for each objection with proof points",
                "Train bot to recognize objection patterns and respond appropriately",
                "Add fallback responses for unexpected objections",
                "Test with sample calls before deploying"
            ],
            resources_needed=[
                "Sales expert to craft objection responses",
                "Bot training capability",
                "Sample objection scenarios for testing"
            ],
            estimated_time="4-6 days",
            expected_revenue_recovery=issue.revenue_impact * 0.30,
            expected_conversion_lift=0.20,
            confidence_score=0.65
        ))
        
        # Recommendation 3: Add social proof elements
        if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
            recommendations.append(ActionableRecommendation(
                recommendation_id=self._next_id(),
                issue_id=issue.issue_id,
                priority=self._calculate_priority(issue, 0.55),
                action="Integrate social proof and urgency elements into script",
                expected_impact=f"Potential to recover ${issue.revenue_impact * 0.25:,.0f} (25% of lost revenue)",
                implementation_effort="low",
                steps=[
                    "Gather customer testimonials and success metrics",
                    "Add specific numbers (e.g., '500+ customers', '97% satisfaction')",
                    "Incorporate limited-time offers or scarcity elements",
                    "Place social proof strategically before objection handling phase",
                    "Test and measure impact on conversion"
                ],
                resources_needed=[
                    "Customer success data and testimonials",
                    "Marketing copy guidelines",
                    "Script modification access"
                ],
                estimated_time="2-3 days",
                expected_revenue_recovery=issue.revenue_impact * 0.25,
                expected_conversion_lift=0.15,
                confidence_score=0.55
            ))
        
        return recommendations
    
    def _recommendations_for_dropoff(
        self,
        issue: PerformanceIssue
    ) -> List[ActionableRecommendation]:
        """Generate recommendations for high drop-off issues"""
        
        recommendations = []
        
        # Stage-specific recommendations
        if issue.problematic_stage == DropOffStage.INTRO:
            recommendations.append(ActionableRecommendation(
                recommendation_id=self._next_id(),
                issue_id=issue.issue_id,
                priority=1,  # Critical - first impression
                action="Shorten and personalize the introduction",
                expected_impact=f"Reduce intro drop-off by 50%, recover ${issue.revenue_impact * 0.50:,.0f}",
                implementation_effort="low",
                steps=[
                    "Cut intro to 15 seconds maximum",
                    "Lead with value, not company background",
                    "Personalize greeting using available lead data",
                    "Get to the reason for call within first 10 seconds",
                    "Add pattern interrupt or intriguing question"
                ],
                resources_needed=[
                    "Script editor access",
                    "Lead data integration (name, company, etc.)"
                ],
                estimated_time="1-2 days",
                expected_revenue_recovery=issue.revenue_impact * 0.50,
                expected_conversion_lift=0.30,
                confidence_score=0.80
            ))
        
        elif issue.problematic_stage == DropOffStage.PITCH:
            recommendations.append(ActionableRecommendation(
                recommendation_id=self._next_id(),
                issue_id=issue.issue_id,
                priority=1,
                action="Restructure pitch to be more conversational and benefit-focused",
                expected_impact=f"Reduce pitch drop-off by 40%, recover ${issue.revenue_impact * 0.45:,.0f}",
                implementation_effort="medium",
                steps=[
                    "Break monologue into dialogue with confirmation questions",
                    "Focus on benefits not features",
                    "Use storytelling framework (problem-solution-outcome)",
                    "Add pauses for engagement checks",
                    "Reduce pitch length by 30%"
                ],
                resources_needed=[
                    "Sales methodology expert",
                    "Call flow redesign capability"
                ],
                estimated_time="3-5 days",
                expected_revenue_recovery=issue.revenue_impact * 0.45,
                expected_conversion_lift=0.35,
                confidence_score=0.75
            ))
        
        elif issue.problematic_stage == DropOffStage.OBJECTION_HANDLING:
            recommendations.append(ActionableRecommendation(
                recommendation_id=self._next_id(),
                issue_id=issue.issue_id,
                priority=1,
                action="Improve objection detection and response quality",
                expected_impact=f"Reduce objection-phase drop-off by 45%, recover ${issue.revenue_impact * 0.50:,.0f}",
                implementation_effort="high",
                steps=[
                    "Analyze all objections from dropped calls",
                    "Train bot NLU to better recognize objection patterns",
                    "Create empathetic, non-defensive response frameworks",
                    "Add confirmation loop to ensure objection is addressed",
                    "Implement graceful transition after objection handling"
                ],
                resources_needed=[
                    "NLU/ML engineer for bot training",
                    "Sales psychology expert",
                    "Call transcript analysis"
                ],
                estimated_time="5-7 days",
                expected_revenue_recovery=issue.revenue_impact * 0.50,
                expected_conversion_lift=0.40,
                confidence_score=0.70
            ))
        
        # General drop-off recommendation
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=2,
            action="Implement engagement monitoring and recovery mechanisms",
            expected_impact=f"Catch and recover 20% of at-risk calls, ${issue.revenue_impact * 0.20:,.0f}",
            implementation_effort="medium",
            steps=[
                "Add sentiment detection to identify disengagement",
                "Create 'rescue' scripts when engagement drops",
                "Implement conversation pacing adjustments",
                "Add value-add interrupts when losing attention",
                "Create smooth exit options to avoid awkward hang-ups"
            ],
            resources_needed=[
                "Sentiment analysis integration",
                "Dynamic scripting capability",
                "A/B testing for rescue scripts"
            ],
            estimated_time="4-6 days",
            expected_revenue_recovery=issue.revenue_impact * 0.20,
            expected_conversion_lift=0.15,
            confidence_score=0.60
        ))
        
        return recommendations
    
    def _recommendations_for_escalation(
        self,
        issue: PerformanceIssue
    ) -> List[ActionableRecommendation]:
        """Generate recommendations for escalation issues"""
        
        recommendations = []
        
        # Find top escalation reason from evidence
        top_reason = issue.evidence.get("top_reason", "Unknown")
        
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=2,
            action=f"Train bot to handle '{top_reason}' scenarios autonomously",
            expected_impact=f"Reduce escalations by 40%, save ${issue.revenue_impact * 0.40:,.0f} in agent costs",
            implementation_effort="high",
            steps=[
                f"Collect all '{top_reason}' escalation call recordings",
                "Identify what information or capability bot was missing",
                "Train bot with required knowledge and response patterns",
                "Create decision tree for complex scenarios",
                "Add confidence checks before escalating",
                "Test with similar scenarios before deployment"
            ],
            resources_needed=[
                "ML engineer for bot training",
                "Domain knowledge expert",
                "Test scenario creation",
                "QA testing capability"
            ],
            estimated_time="1-2 weeks",
            expected_revenue_recovery=issue.revenue_impact * 0.40,
            expected_conversion_lift=0.0,  # Saves cost, doesn't improve conversion
            confidence_score=0.65
        ))
        
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=3,
            action="Improve escalation qualification criteria",
            expected_impact=f"Reduce unnecessary escalations by 25%, save ${issue.revenue_impact * 0.25:,.0f}",
            implementation_effort="low",
            steps=[
                "Review escalated calls to identify premature escalations",
                "Set stricter criteria for when to escalate",
                "Add bot confidence scoring before escalation",
                "Create intermediate 'retry' step before escalating",
                "Train bot to attempt resolution at least twice"
            ],
            resources_needed=[
                "Escalation log analysis",
                "Bot logic configuration access"
            ],
            estimated_time="2-3 days",
            expected_revenue_recovery=issue.revenue_impact * 0.25,
            expected_conversion_lift=0.0,
            confidence_score=0.70
        ))
        
        return recommendations
    
    def _recommendations_for_compliance(
        self,
        issue: PerformanceIssue
    ) -> List[ActionableRecommendation]:
        """Generate recommendations for compliance issues"""
        
        recommendations = []
        
        top_violation = issue.evidence.get("top_violation", "Unknown")
        
        # Compliance is always priority 1
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=1,  # Always highest priority
            action=f"Immediately fix '{top_violation}' compliance violation in script",
            expected_impact=f"Eliminate 80% of violations, avoid ${issue.revenue_impact * 0.80:,.0f} in fines/risk",
            implementation_effort="low",
            steps=[
                "Pause campaign immediately if risk is critical",
                f"Review all instances of '{top_violation}' in current scripts",
                "Consult legal/compliance team for approved language",
                "Update scripts with compliant alternatives",
                "Add automated compliance checks before call deployment",
                "Implement kill-switch for detecting violations in real-time"
            ],
            resources_needed=[
                "Legal/compliance review",
                "Script update access",
                "Real-time monitoring capability"
            ],
            estimated_time="1-2 days (urgent)",
            expected_revenue_recovery=issue.revenue_impact * 0.80,
            expected_conversion_lift=0.0,
            confidence_score=0.95
        ))
        
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=1,
            action="Implement pre-call compliance validation system",
            expected_impact="Prevent future violations, ensure 99%+ compliance rate",
            implementation_effort="medium",
            steps=[
                "Create compliance rule engine",
                "Build pre-flight checks for all outbound calls",
                "Implement real-time transcript monitoring",
                "Auto-terminate calls that violate rules",
                "Generate compliance reports for auditing"
            ],
            resources_needed=[
                "Engineering team for rule engine",
                "Compliance rule documentation",
                "Monitoring infrastructure"
            ],
            estimated_time="1 week",
            expected_revenue_recovery=issue.revenue_impact * 0.90,
            expected_conversion_lift=0.0,
            confidence_score=0.90
        ))
        
        return recommendations
    
    def _recommendations_for_technical(
        self,
        issue: PerformanceIssue
    ) -> List[ActionableRecommendation]:
        """Generate recommendations for technical issues"""
        
        recommendations = []
        
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=1,
            action="Investigate and fix technical infrastructure issues",
            expected_impact=f"Eliminate 90% of failures, recover ${issue.revenue_impact * 0.90:,.0f}",
            implementation_effort="high",
            steps=[
                "Review error logs for failure patterns",
                "Check API uptime and latency metrics",
                "Verify telephony provider stability",
                "Test database connection pooling",
                "Implement retry logic for transient failures",
                "Add circuit breakers for dependent services",
                "Set up proactive alerting for failures"
            ],
            resources_needed=[
                "DevOps/SRE engineer",
                "Access to infrastructure logs",
                "Monitoring tools (APM, logging)",
                "Testing environment"
            ],
            estimated_time="3-5 days",
            expected_revenue_recovery=issue.revenue_impact * 0.90,
            expected_conversion_lift=0.0,
            confidence_score=0.85
        ))
        
        recommendations.append(ActionableRecommendation(
            recommendation_id=self._next_id(),
            issue_id=issue.issue_id,
            priority=2,
            action="Implement graceful degradation and fallback mechanisms",
            expected_impact="Reduce future failure impact by 60%",
            implementation_effort="medium",
            steps=[
                "Design fallback flows for common failure scenarios",
                "Implement queue-based retry system",
                "Add ability to fall back to human agents automatically",
                "Create cached responses for critical paths",
                "Build health check endpoints for all dependencies"
            ],
            resources_needed=[
                "Backend engineer",
                "Queueing system (e.g., Redis, RabbitMQ)",
                "Caching layer"
            ],
            estimated_time="5-7 days",
            expected_revenue_recovery=issue.revenue_impact * 0.60,
            expected_conversion_lift=0.0,
            confidence_score=0.75
        ))
        
        return recommendations
    
    def _calculate_priority(self, issue: PerformanceIssue, confidence: float) -> int:
        """
        Calculate recommendation priority (1-5, 1 being highest)
        
        Factors:
        - Issue severity
        - Revenue impact
        - Confidence in recommendation
        """
        
        # Start with severity
        if issue.severity == IssueSeverity.CRITICAL:
            base_priority = 1
        elif issue.severity == IssueSeverity.HIGH:
            base_priority = 2
        elif issue.severity == IssueSeverity.MEDIUM:
            base_priority = 3
        else:
            base_priority = 4
        
        # Adjust for confidence
        if confidence < 0.50:
            base_priority += 1  # Lower confidence = lower priority
        elif confidence > 0.80:
            base_priority = max(1, base_priority - 1)  # High confidence = higher priority
        
        # Adjust for revenue impact
        if issue.revenue_impact > 50000:  # >$50k impact
            base_priority = max(1, base_priority - 1)
        
        return min(5, max(1, base_priority))
    
    def _next_id(self) -> str:
        """Generate next recommendation ID"""
        self.recommendation_counter += 1
        return f"REC_{self.config.campaign_id}_{self.recommendation_counter:04d}"
