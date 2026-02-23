# Voice Bot Intelligence Tool - Backend Core Logic

**Internal analytics and intelligence engine for sales teams using voice bots**

## 🎯 Overview

This is a comprehensive backend intelligence system that analyzes voice bot campaign performance, detects issues, calculates revenue leakage, and provides actionable recommendations. The system is designed for sales teams to:

1. **Detect Performance Issues** - Automatically identify problems in campaigns
2. **Calculate Revenue Leakage** - Quantify exactly where money is being lost
3. **Root Cause Analysis** - Pinpoint whether issues stem from drop-offs, escalations, or compliance
4. **Generate Actionable Fixes** - Provide step-by-step recommendations with impact estimates
5. **Score Campaign Health** - Calculate 0-100 health scores with component breakdowns
6. **Alert on Changes** - Monitor week-over-week performance and trigger alerts

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Voice Bot Intelligence Engine                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Intelligence Engine (Main Orchestrator)          │  │
│  └──────────────────────────────────────────────────┘  │
│                       │                                  │
│           ┌───────────┴───────────┐                     │
│           │                       │                     │
│  ┌────────▼────────┐    ┌────────▼──────────┐         │
│  │ Performance     │    │  Revenue          │         │
│  │ Analyzer        │    │  Calculator       │         │
│  └────────┬────────┘    └────────┬──────────┘         │
│           │                       │                     │
│  ┌────────▼────────┐    ┌────────▼──────────┐         │
│  │ Root Cause      │    │ Recommendation    │         │
│  │ Analyzer        │    │ Engine            │         │
│  └────────┬────────┘    └────────┬──────────┘         │
│           │                       │                     │
│  ┌────────▼────────┐    ┌────────▼──────────┐         │
│  │ Health          │    │  Alert            │         │
│  │ Scorer          │    │  System           │         │
│  └─────────────────┘    └───────────────────┘         │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
voice_bot_intelligence/
│
├── models.py                    # Data models and structures
├── performance_analyzer.py      # Issue detection and metrics
├── revenue_calculator.py        # Revenue leakage analysis
├── recommendation_engine.py     # Actionable fix generation
├── health_scorer.py            # 0-100 health scoring
├── alert_system.py             # WoW monitoring and alerts
├── intelligence_engine.py      # Main orchestrator
├── example_usage.py            # Usage examples
└── README.md                   # This file
```

## 🚀 Quick Start

### Basic Usage

```python
from datetime import datetime, timedelta
from models import CampaignConfig, CallRecord
from intelligence_engine import VoiceBotIntelligence

# 1. Configure your campaign
config = CampaignConfig(
    campaign_id="CAMP_001",
    campaign_name="Q1 Sales Outreach",
    start_date=datetime.now() - timedelta(days=30),
    target_calls_per_day=200,
    target_conversion_rate=0.15,  # 15%
    target_revenue_per_call=75,
    avg_deal_value=500,
    compliance_rules=["disclosure_required", "dnc_respect"],
    script_versions=["v1.0", "v1.1"]
)

# 2. Initialize intelligence engine
intelligence = VoiceBotIntelligence(config)

# 3. Load your call data (from your database)
current_calls = load_calls_from_database(last_7_days=True)
previous_calls = load_calls_from_database(days_ago=14, duration=7)

# 4. Generate intelligence report
report = intelligence.analyze_campaign(
    current_calls=current_calls,
    previous_calls=previous_calls
)

# 5. Access insights
print(f"Health Score: {report.health_score.overall_score}/100")
print(f"Revenue Leakage: ${report.performance_metrics.revenue_leakage:,.0f}")
print(f"Issues Detected: {len(report.issues)}")
print(f"Active Alerts: {len(report.active_alerts)}")

# 6. Get top recommendations
for rec in report.recommendations[:3]:
    print(f"Priority {rec.priority}: {rec.action}")
    print(f"  Impact: {rec.expected_impact}")
```

### Quick Status Check

```python
# Lightweight status check (no historical comparison)
status = intelligence.get_quick_status(current_calls)

print(f"Health: {status['health_score']}/100 ({status['health_status']})")
print(f"Conversion: {status['conversion_rate']}")
print(f"Revenue: {status['total_revenue']}")
```

## 📊 Core Modules

### 1. Performance Analyzer

**Purpose**: Detect performance issues in campaigns

**Key Features**:
- Conversion rate analysis vs targets and benchmarks
- Drop-off detection by funnel stage
- Escalation spike identification
- Compliance violation tracking
- Technical failure detection

**Usage**:
```python
from performance_analyzer import PerformanceAnalyzer

analyzer = PerformanceAnalyzer(config)

# Calculate metrics
metrics = analyzer.calculate_metrics(calls)

# Detect issues
issues = analyzer.detect_issues(metrics, calls)

for issue in issues:
    print(f"{issue.severity.value}: {issue.root_cause}")
    print(f"  Impact: ${issue.revenue_impact:,.0f}")
```

### 2. Revenue Calculator

**Purpose**: Calculate revenue leakage and quantify impact

**Key Features**:
- Total leakage calculation
- Leakage breakdown by reason (drop-offs, conversions, escalations, etc.)
- Leakage breakdown by funnel stage
- Recoverable revenue estimation
- Recovery scenario modeling

**Usage**:
```python
from revenue_calculator import RevenueCalculator

calc = RevenueCalculator(config)

# Calculate leakage
leakage = calc.calculate_leakage(calls, metrics)

print(f"Total Leakage: ${leakage.total_leakage:,.0f}")
print(f"Recoverable: ${leakage.recoverable_amount:,.0f} ({leakage.recovery_difficulty})")

# Top leakage sources
for reason, amount in leakage.top_3_reasons:
    print(f"{reason}: ${amount:,.0f}")
```

### 3. Recommendation Engine

**Purpose**: Generate actionable fixes for issues

**Key Features**:
- Issue-specific recommendations
- Prioritized action plans
- Step-by-step implementation guides
- Resource requirements
- Impact estimates (revenue, conversion lift, confidence)

**Usage**:
```python
from recommendation_engine import RecommendationEngine

engine = RecommendationEngine(config)

# Generate recommendations
recommendations = engine.generate_recommendations(issues)

for rec in recommendations:
    print(f"Priority {rec.priority}: {rec.action}")
    print(f"  Expected Recovery: ${rec.expected_revenue_recovery:,.0f}")
    print(f"  Effort: {rec.implementation_effort}")
    print(f"  Time: {rec.estimated_time}")
    print(f"  Steps: {len(rec.steps)}")
```

### 4. Health Scorer

**Purpose**: Calculate 0-100 health score with component breakdowns

**Key Features**:
- Overall health score (0-100)
- Component scores: Conversion, Revenue, Compliance, Efficiency, Quality
- Weighted scoring based on business impact
- Trend analysis (improving/stable/declining)
- Week-over-week change tracking

**Scoring Components**:
- **Conversion (35%)**: Conversion rate vs target and benchmarks
- **Revenue (25%)**: Revenue achievement and leakage
- **Compliance (20%)**: Compliance rate (strict penalties)
- **Efficiency (12%)**: Drop-off, escalation, failure rates
- **Quality (8%)**: Sentiment and engagement metrics

**Usage**:
```python
from health_scorer import HealthScorer

scorer = HealthScorer(config)

# Calculate health
health = scorer.calculate_health(current_metrics, previous_metrics, issues)

print(f"Overall: {health.overall_score}/100 ({health.health_status()})")
print(f"  Conversion: {health.conversion_health}/100")
print(f"  Revenue: {health.revenue_health}/100")
print(f"  Compliance: {health.compliance_health}/100")
print(f"Trend: {health.trend} ({health.week_over_week_change:+.1f}% WoW)")

# Get insights
insights = scorer.get_health_insights(health)
for insight in insights:
    print(f"• {insight}")
```

### 5. Alert System

**Purpose**: Monitor performance changes and trigger alerts

**Key Features**:
- Week-over-week comparison
- Configurable thresholds
- Severity-based alerts (Critical, High, Medium, Low)
- Multiple alert types (revenue, conversion, drop-off, escalation, compliance, health)

**Alert Thresholds**:
- Revenue drop: >10% decrease
- Conversion drop: >15% decrease
- Drop-off spike: >20% increase
- Escalation spike: >25% increase
- Compliance: ANY violation increase (critical)
- Health score drop: >15 point decrease

**Usage**:
```python
from alert_system import AlertSystem

alert_system = AlertSystem(config)

# Generate alerts
alerts = alert_system.generate_alerts(
    current_metrics,
    previous_metrics,
    current_health,
    previous_health,
    issues
)

# Get critical alerts only
critical = alert_system.get_critical_alerts(alerts)

# Format summary
summary = alert_system.format_alert_summary(alerts)
print(summary)
```

## 🔧 Integration Guide

### Step 1: Define Your Campaign

```python
config = CampaignConfig(
    campaign_id="YOUR_CAMPAIGN_ID",
    campaign_name="Campaign Name",
    start_date=campaign_start_date,
    target_calls_per_day=200,
    target_conversion_rate=0.15,
    target_revenue_per_call=75,
    avg_deal_value=500,
    compliance_rules=["your", "compliance", "rules"],
    script_versions=["v1.0", "v1.1"]
)
```

### Step 2: Map Your Data to CallRecord

```python
from models import CallRecord, CallStatus, DropOffStage

def convert_your_call_to_callrecord(your_call_data):
    """Convert your database records to CallRecord format"""
    
    return CallRecord(
        call_id=your_call_data.id,
        campaign_id=your_call_data.campaign_id,
        timestamp=your_call_data.created_at,
        duration_seconds=your_call_data.duration,
        status=map_to_call_status(your_call_data.status),
        drop_off_stage=map_to_drop_off_stage(your_call_data.stage) if dropped else None,
        escalation_reason=your_call_data.escalation_reason if escalated else None,
        compliance_flags=your_call_data.compliance_violations or [],
        conversion_value=expected_value_of_this_call,
        actual_revenue=actual_revenue_from_this_call,
        sentiment_score=your_sentiment_analysis_score,  # -1 to 1
        script_version=your_call_data.script_version,
        agent_id=your_call_data.agent_id if escalated else None
    )
```

### Step 3: Set Up Automated Reporting

```python
from datetime import datetime, timedelta

def generate_weekly_report():
    """Run this weekly to generate reports"""
    
    # Load calls from your database
    current_calls = load_calls_from_db(
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now()
    )
    
    previous_calls = load_calls_from_db(
        start_date=datetime.now() - timedelta(days=14),
        end_date=datetime.now() - timedelta(days=7)
    )
    
    # Generate report
    intelligence = VoiceBotIntelligence(config)
    report = intelligence.analyze_campaign(current_calls, previous_calls)
    
    # Send to stakeholders
    send_email(
        subject=f"Weekly Intelligence Report - {config.campaign_name}",
        body=intelligence.export_report_summary(report),
        recipients=["team@company.com"]
    )
    
    # Save to database
    save_report_to_db(report)
    
    # Trigger webhooks for critical alerts
    if report.active_alerts:
        critical_alerts = [a for a in report.active_alerts if a.is_critical()]
        if critical_alerts:
            trigger_slack_notification(critical_alerts)
```

## 📈 Example Report Output

```
================================================================================
VOICE BOT INTELLIGENCE REPORT - Q1 2025 Sales Outreach
================================================================================
Report Date: 2025-02-23 14:30:00
Period: 2025-02-16 to 2025-02-22

EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Campaign 'Q1 2025 Sales Outreach' health score: 67/100 (Good) | Revenue: 
$84,000 (80% of target) with $21,000 in leakage (20.0%) | Conversion rate: 
12.0% (target: 15.0%) from 1,400 calls | ⚠️ 2 CRITICAL issues requiring 
immediate attention | Recovery opportunity: $16,800 (medium difficulty)

HEALTH SCORE
--------------------------------------------------------------------------------
Overall: 67/100 (Good)
  Conversion Health: 65/100
  Revenue Health: 70/100
  Compliance Health: 85/100
  Efficiency Health: 62/100
  Quality Health: 72/100
Trend: DECLINING (-8.5% WoW)

KEY METRICS
--------------------------------------------------------------------------------
Total Calls: 1,400
Conversion Rate: 12.0% (target: 15.0%)
Revenue: $84,000
Revenue Leakage: $21,000 (20.0%)
Completion Rate: 72.0%
Escalation Rate: 14.0%

ACTIVE ALERTS
--------------------------------------------------------------------------------
[HIGH] Revenue Drop Alert
  Revenue decreased by 12.0% compared to last week. Lost $11,424 in revenue.
[HIGH] Conversion Rate Declining
  Conversion rate dropped 14.3% from 14.0% to 12.0%
[MEDIUM] Drop-off Rate Increasing
  Call drop-off rate spiked 27.3% to 28.0%. 392 calls dropped this period.

DETECTED ISSUES
--------------------------------------------------------------------------------
[HIGH] Low Conversion
  Conversion rate 12.0% is 20.0% below target 15.0%
  Impact: $21,000, 1,400 calls
[HIGH] High Drop Off
  High drop-off rate of 28.0% (threshold: 20.0%)
  Impact: $29,400, 392 calls

URGENT ACTIONS REQUIRED
--------------------------------------------------------------------------------
1. Priority 1: A/B test an improved value proposition and pitch script 
   ($8,400 recovery, 3-5 days)
2. Priority 1: Shorten and personalize the introduction ($14,700 recovery, 
   1-2 days)
3. Priority 2: Enhance objection handling with dynamic responses ($6,300 
   recovery, 4-6 days)

TOP RECOMMENDATIONS
--------------------------------------------------------------------------------
Priority 1: A/B test an improved value proposition and pitch script
  Expected Impact: Potential to recover $8,400 (40% of lost revenue)
  Effort: medium, Time: 3-5 days

Priority 1: Shorten and personalize the introduction
  Expected Impact: Reduce intro drop-off by 50%, recover $14,700
  Effort: low, Time: 1-2 days

Priority 2: Enhance objection handling with dynamic responses
  Expected Impact: Potential to recover $6,300 (30% of lost revenue)
  Effort: medium, Time: 4-6 days

================================================================================
```

## 🎓 Running the Example

To see the system in action:

```bash
python example_usage.py
```

This will:
1. Create sample campaign configuration
2. Generate realistic call data (current + previous week)
3. Run full intelligence analysis
4. Display comprehensive report
5. Show additional functionality examples

## 🔒 Data Models

### CallRecord
Core data structure for individual calls:
- `call_id`: Unique identifier
- `timestamp`: When call occurred
- `status`: COMPLETED | DROPPED | ESCALATED | FAILED | COMPLIANCE_VIOLATION
- `drop_off_stage`: Which funnel stage (if dropped)
- `conversion_value`: Expected revenue
- `actual_revenue`: Actual revenue generated
- `sentiment_score`: -1 to 1 (negative to positive)

### PerformanceMetrics
Aggregated metrics for a period:
- Call counts (total, completed, dropped, etc.)
- Conversion metrics
- Revenue metrics
- Quality metrics
- Drop-off breakdown by stage

### PerformanceIssue
Detected performance problem:
- Issue type and severity
- Revenue impact
- Root cause
- Contributing factors
- Evidence/data

### ActionableRecommendation
Fix for an issue:
- Action description
- Implementation steps
- Expected impact
- Resource requirements
- Effort level and timeline

### HealthScore
Campaign health assessment:
- Overall score (0-100)
- Component scores
- Trend direction
- WoW change

### Alert
Performance alert:
- Alert type and severity
- Current vs previous values
- Threshold crossed
- Percentage change

## 🎯 Design Principles

1. **Modular Architecture**: Each module has a single, clear responsibility
2. **Production Ready**: Comprehensive error handling, validation, and logging hooks
3. **Extensible**: Easy to add new issue types, recommendation strategies, or scoring components
4. **Data-Driven**: All recommendations backed by actual impact calculations
5. **Actionable**: Every issue comes with specific, implementable fixes

## 🚦 Next Steps

### For Production Deployment:

1. **Database Integration**: Connect to your call database
2. **API Layer**: Add REST API for frontend consumption
3. **Caching**: Implement caching for repeated calculations
4. **Monitoring**: Add logging and performance monitoring
5. **Scheduling**: Set up automated report generation
6. **Notifications**: Integrate with Slack, email, etc.

### For Enhancement:

1. **ML Models**: Add predictive models for churn, conversion probability
2. **A/B Testing**: Built-in A/B test analysis for script variations
3. **Benchmarking**: Industry benchmark comparisons
4. **Forecasting**: Revenue and performance forecasting
5. **Custom Metrics**: Support for team-specific KPIs

## 📝 License

This is backend logic for internal use. No external dependencies required beyond Python standard library.

## 🤝 Support

For questions or issues with implementation, refer to the example code in `example_usage.py` which demonstrates all major features.
