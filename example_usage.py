"""
Voice Bot Intelligence Tool - Example Usage
============================================
Demonstrates how to use the intelligence engine with sample data
"""

from datetime import datetime, timedelta
import random

from models import (
    CallRecord, CampaignConfig, CallStatus, DropOffStage
)
from intelligence_engine import VoiceBotIntelligence


def generate_sample_calls(
    num_calls: int,
    campaign_id: str,
    start_date: datetime,
    conversion_rate: float = 0.12,
    drop_off_rate: float = 0.25,
    escalation_rate: float = 0.12,
    compliance_violation_rate: float = 0.02
) -> list:
    """
    Generate sample call data for testing
    
    Args:
        num_calls: Number of calls to generate
        campaign_id: Campaign identifier
        start_date: Start date for calls
        conversion_rate: Target conversion rate
        drop_off_rate: Rate of dropped calls
        escalation_rate: Rate of escalations
        compliance_violation_rate: Rate of compliance violations
        
    Returns:
        List of CallRecord objects
    """
    
    calls = []
    
    for i in range(num_calls):
        # Generate timestamp within the week
        timestamp = start_date + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(9, 17),
            minutes=random.randint(0, 59)
        )
        
        # Randomly assign call outcome
        rand = random.random()
        
        if rand < compliance_violation_rate:
            status = CallStatus.COMPLIANCE_VIOLATION
            drop_off_stage = None
            escalation_reason = None
            duration = random.randint(120, 300)
            conversion_value = 500
            actual_revenue = 0
            sentiment = random.uniform(-0.8, -0.4)
            compliance_flags = random.choice([
                ["unauthorized_claim"],
                ["missing_disclosure"],
                ["aggressive_language"],
                ["do_not_call_violation"]
            ])
            
        elif rand < compliance_violation_rate + drop_off_rate:
            status = CallStatus.DROPPED
            drop_off_stage = random.choice(list(DropOffStage))
            escalation_reason = None
            duration = random.randint(30, 180)
            conversion_value = 500
            actual_revenue = 0
            sentiment = random.uniform(-0.5, 0.2)
            compliance_flags = []
            
        elif rand < compliance_violation_rate + drop_off_rate + escalation_rate:
            status = CallStatus.ESCALATED
            drop_off_stage = None
            escalation_reason = random.choice([
                "complex_question",
                "pricing_negotiation",
                "technical_issue",
                "angry_customer",
                "special_request"
            ])
            duration = random.randint(180, 400)
            conversion_value = 500
            # 70% of escalated calls convert
            actual_revenue = 500 if random.random() < 0.70 else 0
            sentiment = random.uniform(-0.2, 0.4)
            compliance_flags = []
            
        else:
            status = CallStatus.COMPLETED
            drop_off_stage = None
            escalation_reason = None
            duration = random.randint(200, 450)
            conversion_value = 500
            # Apply conversion rate to completed calls
            actual_revenue = 500 if random.random() < (conversion_rate / (1 - drop_off_rate - escalation_rate)) else 0
            sentiment = random.uniform(0.1, 0.7) if actual_revenue > 0 else random.uniform(-0.3, 0.3)
            compliance_flags = []
        
        call = CallRecord(
            call_id=f"CALL_{campaign_id}_{i:06d}",
            campaign_id=campaign_id,
            timestamp=timestamp,
            duration_seconds=duration,
            status=status,
            drop_off_stage=drop_off_stage,
            escalation_reason=escalation_reason,
            compliance_flags=compliance_flags,
            conversion_value=conversion_value,
            actual_revenue=actual_revenue,
            sentiment_score=sentiment,
            script_version=f"v{random.randint(1,3)}.{random.randint(0,5)}",
            agent_id=f"AGENT_{random.randint(1,20):03d}" if status == CallStatus.ESCALATED else None
        )
        
        calls.append(call)
    
    return calls


def main():
    """Main example demonstrating the intelligence engine"""
    
    print("=" * 80)
    print("Voice Bot Intelligence Tool - Example Usage")
    print("=" * 80)
    print()
    
    # Step 1: Configure campaign
    print("📋 Setting up campaign configuration...")
    campaign = CampaignConfig(
        campaign_id="CAMP_001",
        campaign_name="Q1 2025 Sales Outreach",
        start_date=datetime.now() - timedelta(days=30),
        target_calls_per_day=200,
        target_conversion_rate=0.15,  # 15% target
        target_revenue_per_call=75,
        avg_deal_value=500,
        compliance_rules=[
            "Must include disclosure statement",
            "Cannot make unauthorized claims",
            "Respect DNC list"
        ],
        script_versions=["v1.0", "v1.1", "v1.2"]
    )
    
    print(f"  Campaign: {campaign.campaign_name}")
    print(f"  Target conversion rate: {campaign.target_conversion_rate:.1%}")
    print(f"  Average deal value: ${campaign.avg_deal_value}")
    print()
    
    # Step 2: Generate sample data
    print("🎲 Generating sample call data...")
    
    # Current week data (slightly underperforming)
    current_week_start = datetime.now() - timedelta(days=7)
    current_calls = generate_sample_calls(
        num_calls=1400,  # 200 calls/day * 7 days
        campaign_id=campaign.campaign_id,
        start_date=current_week_start,
        conversion_rate=0.12,  # Below target (15%)
        drop_off_rate=0.28,    # Slightly high
        escalation_rate=0.14,  # Slightly high
        compliance_violation_rate=0.025  # Slightly concerning
    )
    
    print(f"  Current week: {len(current_calls)} calls generated")
    
    # Previous week data (better performance)
    previous_week_start = datetime.now() - timedelta(days=14)
    previous_calls = generate_sample_calls(
        num_calls=1400,
        campaign_id=campaign.campaign_id,
        start_date=previous_week_start,
        conversion_rate=0.14,  # Better
        drop_off_rate=0.22,    # Better
        escalation_rate=0.11,  # Better
        compliance_violation_rate=0.01  # Better
    )
    
    print(f"  Previous week: {len(previous_calls)} calls generated")
    print()
    
    # Step 3: Initialize intelligence engine
    print("🧠 Initializing Voice Bot Intelligence Engine...")
    intelligence = VoiceBotIntelligence(campaign)
    print("  ✓ Performance Analyzer initialized")
    print("  ✓ Revenue Calculator initialized")
    print("  ✓ Recommendation Engine initialized")
    print("  ✓ Health Scorer initialized")
    print("  ✓ Alert System initialized")
    print()
    
    # Step 4: Generate intelligence report
    print("🔬 Analyzing campaign performance...")
    print()
    
    report = intelligence.analyze_campaign(
        current_calls=current_calls,
        previous_calls=previous_calls
    )
    
    print()
    print("=" * 80)
    print("INTELLIGENCE REPORT GENERATED")
    print("=" * 80)
    print()
    
    # Display report summary
    report_text = intelligence.export_report_summary(report)
    print(report_text)
    
    # Additional examples
    print()
    print("=" * 80)
    print("ADDITIONAL FUNCTIONALITY EXAMPLES")
    print("=" * 80)
    print()
    
    # Example 1: Quick status check
    print("📊 Example: Quick Status Check")
    print("-" * 80)
    quick_status = intelligence.get_quick_status(current_calls)
    for key, value in quick_status.items():
        print(f"  {key}: {value}")
    print()
    
    # Example 2: Deep dive on specific issue
    if report.issues:
        print("🔍 Example: Deep Dive on Top Issue")
        print("-" * 80)
        top_issue = report.issues[0]
        deep_dive = intelligence.analyze_specific_issue(top_issue, current_calls)
        print(f"  Issue Type: {top_issue.issue_type.value}")
        print(f"  Severity: {top_issue.severity.value}")
        print(f"  Affected Calls: {deep_dive['affected_calls_percentage']:.1f}%")
        print(f"  Revenue Impact Breakdown:")
        for key, value in deep_dive['revenue_impact_breakdown'].items():
            print(f"    {key}: ${value:,.0f}")
        print(f"  Recommendations: {len(deep_dive['recommendations'])}")
        print()
    
    # Example 3: Alert summary
    if report.active_alerts:
        print("🚨 Example: Alert Summary")
        print("-" * 80)
        alert_summary = intelligence.alert_system.format_alert_summary(report.active_alerts)
        print(alert_summary)
        print()
    
    # Example 4: Health score insights
    print("💊 Example: Health Score Insights")
    print("-" * 80)
    health_insights = intelligence.health_scorer.get_health_insights(report.health_score)
    for insight in health_insights:
        print(f"  • {insight}")
    print()
    
    print("=" * 80)
    print("✅ Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
