# QUICK START GUIDE
# Voice Bot Intelligence Tool

## ⚡ Get Running in 5 Minutes

### Step 1: Extract Files
Unzip voice_bot_intelligence.zip to your project folder

### Step 2: Test the System
```bash
cd voice_bot_intelligence
python example_usage.py
```

You should see a complete intelligence report with:
- Health scores
- Detected issues
- Revenue leakage analysis
- Recommendations
- Alerts

### Step 3: Understand the Data Flow

```
Your Call Data → CallRecord → Intelligence Engine → Intelligence Report
```

### Step 4: Connect Your Data

Edit this template to load YOUR call data:

```python
from datetime import datetime
from models import CallRecord, CallStatus, CampaignConfig
from intelligence_engine import VoiceBotIntelligence

# Your campaign config
config = CampaignConfig(
    campaign_id="YOUR_CAMPAIGN_ID",
    campaign_name="Your Campaign Name",
    start_date=datetime(2025, 1, 1),
    target_calls_per_day=200,
    target_conversion_rate=0.15,  # 15%
    target_revenue_per_call=75,
    avg_deal_value=500,
    compliance_rules=["disclosure_required"],
    script_versions=["v1.0"]
)

# Load YOUR calls from YOUR database
def load_your_calls():
    # Replace this with your actual database query
    raw_calls = your_database.query("SELECT * FROM calls WHERE...")
    
    # Convert to CallRecord format
    calls = []
    for row in raw_calls:
        call = CallRecord(
            call_id=row['id'],
            campaign_id=row['campaign_id'],
            timestamp=row['created_at'],
            duration_seconds=row['duration'],
            status=CallStatus(row['status']),  # 'completed', 'dropped', etc.
            drop_off_stage=None,  # Add your stage mapping
            escalation_reason=row['escalation_reason'] if row['escalated'] else None,
            compliance_flags=row['violations'] or [],
            conversion_value=500,  # Expected value
            actual_revenue=row['revenue'],  # Actual revenue
            sentiment_score=row['sentiment'],  # -1 to 1
            script_version=row['script_version'],
            agent_id=row['agent_id'] if row['escalated'] else None
        )
        calls.append(call)
    
    return calls

# Run analysis
current_calls = load_your_calls()
intelligence = VoiceBotIntelligence(config)
report = intelligence.analyze_campaign(current_calls)

# Print results
print(f"Health Score: {report.health_score.overall_score}/100")
print(f"Revenue: ${report.performance_metrics.total_revenue:,.0f}")
print(f"Leakage: ${report.performance_metrics.revenue_leakage:,.0f}")
print(f"\nTop 3 Issues:")
for i, issue in enumerate(report.issues[:3], 1):
    print(f"{i}. {issue.root_cause} (${issue.revenue_impact:,.0f})")
```

### Step 5: What Each File Does

**Core Engine:**
- `models.py` - All data structures (CallRecord, PerformanceMetrics, etc.)
- `intelligence_engine.py` - Main orchestrator (use this!)

**Analysis Modules:**
- `performance_analyzer.py` - Detects issues
- `revenue_calculator.py` - Calculates leakage
- `recommendation_engine.py` - Generates fixes
- `health_scorer.py` - Calculates 0-100 scores
- `alert_system.py` - Week-over-week monitoring

**Examples & Docs:**
- `example_usage.py` - Working demo with sample data
- `README.md` - Complete documentation
- `INTEGRATION_GUIDE.md` - Database, API, Frontend setup

### Step 6: Build Your Dashboard

See INTEGRATION_GUIDE.md for:
- Database schema (PostgreSQL)
- REST API (FastAPI)
- Frontend example (React)
- Docker deployment
- Scheduled reports
- Slack notifications

## 🎯 Most Common Use Cases

### Use Case 1: Weekly Report
```python
intelligence = VoiceBotIntelligence(config)
current_week = load_calls(last_7_days=True)
previous_week = load_calls(days_ago=14, duration=7)

report = intelligence.analyze_campaign(current_week, previous_week)

# Email to team
send_email(intelligence.export_report_summary(report))
```

### Use Case 2: Real-Time Dashboard
```python
# Quick health check (no historical comparison)
status = intelligence.get_quick_status(recent_calls)
# Returns: {health_score: 67, conversion_rate: "12.0%", ...}
```

### Use Case 3: Deep Dive on Issue
```python
# Analyze specific issue
if report.issues:
    top_issue = report.issues[0]
    deep_dive = intelligence.analyze_specific_issue(top_issue, calls)
    print(deep_dive['revenue_impact_breakdown'])
    print(deep_dive['recommendations'])
```

## 🚨 Common Questions

**Q: Where do I get call data?**
A: From your voice bot platform's database or API. You'll need to map their data to our CallRecord format.

**Q: What if I don't have sentiment scores?**
A: Use a default value like 0.0, or integrate a sentiment analysis API.

**Q: Can I customize the health score weights?**
A: Yes! Edit the WEIGHTS dictionary in health_scorer.py

**Q: How do I add custom issue types?**
A: Add to IssueType enum in models.py, then add detection logic in performance_analyzer.py

**Q: Do I need the frontend?**
A: No! The backend works standalone. You can:
  - Run as CLI tool
  - Export reports as JSON
  - Send email reports
  - Build any frontend you want

## 📞 Need Help?

1. Run `python example_usage.py` to see it working
2. Read README.md for complete documentation
3. Check INTEGRATION_GUIDE.md for production setup
4. All code is heavily commented - read the docstrings!

## ✅ You're Ready!

The backend intelligence is **complete**. Just:
1. Map your call data → CallRecord
2. Run the analysis
3. Get insights!

No external dependencies required (pure Python stdlib).
