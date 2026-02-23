# Voice Bot Intelligence Tool - Integration & Deployment Guide

## 🚀 From Backend to Full System

This guide shows you how to turn the core intelligence logic into a production system with frontend, database, and API.

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │    Alerts    │  │    Reports   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │ REST API
┌─────────────────────────────────────────────────────────────┐
│                       API Layer (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   /analyze   │  │   /health    │  │   /alerts    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│              Intelligence Engine (Your Backend)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Analyzer    │  │  Calculator  │  │    Scorer    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Database Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Call Records │  │   Reports    │  │  Campaigns   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Step 1: Database Integration

### Create Database Schema

```sql
-- Campaigns table
CREATE TABLE campaigns (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_name VARCHAR(200) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    target_calls_per_day INTEGER,
    target_conversion_rate DECIMAL(5,4),
    target_revenue_per_call DECIMAL(10,2),
    avg_deal_value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Call records table
CREATE TABLE call_records (
    call_id VARCHAR(100) PRIMARY KEY,
    campaign_id VARCHAR(50) REFERENCES campaigns(campaign_id),
    timestamp TIMESTAMP NOT NULL,
    duration_seconds INTEGER,
    status VARCHAR(50),
    drop_off_stage VARCHAR(50),
    escalation_reason VARCHAR(200),
    compliance_flags TEXT[],
    conversion_value DECIMAL(10,2),
    actual_revenue DECIMAL(10,2),
    sentiment_score DECIMAL(4,3),
    script_version VARCHAR(20),
    agent_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_campaign_timestamp (campaign_id, timestamp)
);

-- Intelligence reports table
CREATE TABLE intelligence_reports (
    report_id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(50) REFERENCES campaigns(campaign_id),
    report_date TIMESTAMP NOT NULL,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    health_score INTEGER,
    total_revenue DECIMAL(12,2),
    revenue_leakage DECIMAL(12,2),
    conversion_rate DECIMAL(5,4),
    report_data JSONB,  -- Store full report as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE alerts (
    alert_id VARCHAR(100) PRIMARY KEY,
    campaign_id VARCHAR(50) REFERENCES campaigns(campaign_id),
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    title VARCHAR(200),
    message TEXT,
    triggered_at TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Integration Code

```python
# database.py
from typing import List
import psycopg2
from datetime import datetime
from models import CallRecord, CallStatus, DropOffStage

class DatabaseConnector:
    """Database integration for voice bot intelligence"""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def load_calls(
        self,
        campaign_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[CallRecord]:
        """Load call records from database"""
        
        query = """
            SELECT 
                call_id, campaign_id, timestamp, duration_seconds,
                status, drop_off_stage, escalation_reason,
                compliance_flags, conversion_value, actual_revenue,
                sentiment_score, script_version, agent_id
            FROM call_records
            WHERE campaign_id = %s
              AND timestamp >= %s
              AND timestamp < %s
            ORDER BY timestamp
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (campaign_id, start_date, end_date))
        
        calls = []
        for row in cursor.fetchall():
            call = CallRecord(
                call_id=row[0],
                campaign_id=row[1],
                timestamp=row[2],
                duration_seconds=row[3],
                status=CallStatus(row[4]),
                drop_off_stage=DropOffStage(row[5]) if row[5] else None,
                escalation_reason=row[6],
                compliance_flags=row[7] or [],
                conversion_value=float(row[8]),
                actual_revenue=float(row[9]),
                sentiment_score=float(row[10]),
                script_version=row[11],
                agent_id=row[12]
            )
            calls.append(call)
        
        return calls
    
    def save_report(self, report):
        """Save intelligence report to database"""
        import json
        
        query = """
            INSERT INTO intelligence_reports
            (campaign_id, report_date, period_start, period_end,
             health_score, total_revenue, revenue_leakage,
             conversion_rate, report_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING report_id
        """
        
        # Convert report to JSON
        report_data = {
            "health_score": {
                "overall": report.health_score.overall_score,
                "components": {
                    "conversion": report.health_score.conversion_health,
                    "revenue": report.health_score.revenue_health,
                    "compliance": report.health_score.compliance_health
                }
            },
            "issues": [
                {
                    "type": i.issue_type.value,
                    "severity": i.severity.value,
                    "impact": i.revenue_impact,
                    "root_cause": i.root_cause
                }
                for i in report.issues
            ],
            "recommendations": [
                {
                    "priority": r.priority,
                    "action": r.action,
                    "impact": r.expected_revenue_recovery
                }
                for r in report.recommendations
            ]
        }
        
        cursor = self.conn.cursor()
        cursor.execute(
            query,
            (
                report.campaign_id,
                report.report_date,
                report.performance_metrics.period_start,
                report.performance_metrics.period_end,
                report.health_score.overall_score,
                report.performance_metrics.total_revenue,
                report.performance_metrics.revenue_leakage,
                report.performance_metrics.conversion_rate,
                json.dumps(report_data)
            )
        )
        
        self.conn.commit()
        return cursor.fetchone()[0]
```

## 🌐 Step 2: REST API Layer

### FastAPI Implementation

```python
# api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from intelligence_engine import VoiceBotIntelligence
from database import DatabaseConnector
from models import CampaignConfig

app = FastAPI(title="Voice Bot Intelligence API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = DatabaseConnector("postgresql://user:pass@localhost/voicebot")

class AnalyzeRequest(BaseModel):
    campaign_id: str
    days_back: int = 7
    compare_previous: bool = True

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "voice-bot-intelligence"}

@app.get("/campaigns")
def list_campaigns():
    """List all campaigns"""
    # Query from database
    query = "SELECT campaign_id, campaign_name FROM campaigns ORDER BY start_date DESC"
    cursor = db.conn.cursor()
    cursor.execute(query)
    
    campaigns = [
        {"id": row[0], "name": row[1]}
        for row in cursor.fetchall()
    ]
    
    return {"campaigns": campaigns}

@app.post("/analyze/{campaign_id}")
def analyze_campaign(campaign_id: str, request: AnalyzeRequest):
    """
    Generate intelligence report for a campaign
    
    Returns complete analysis with issues, recommendations, alerts
    """
    
    try:
        # Load campaign config
        config = load_campaign_config(campaign_id)
        
        # Load call data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days_back)
        
        current_calls = db.load_calls(campaign_id, start_date, end_date)
        
        previous_calls = None
        if request.compare_previous:
            prev_end = start_date
            prev_start = prev_end - timedelta(days=request.days_back)
            previous_calls = db.load_calls(campaign_id, prev_start, prev_end)
        
        # Run intelligence analysis
        intelligence = VoiceBotIntelligence(config)
        report = intelligence.analyze_campaign(current_calls, previous_calls)
        
        # Save report to database
        report_id = db.save_report(report)
        
        # Convert report to JSON response
        return {
            "report_id": report_id,
            "campaign_id": campaign_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "health_score": {
                "overall": report.health_score.overall_score,
                "status": report.health_score.health_status(),
                "conversion": report.health_score.conversion_health,
                "revenue": report.health_score.revenue_health,
                "compliance": report.health_score.compliance_health,
                "trend": report.health_score.trend
            },
            "metrics": {
                "total_calls": report.performance_metrics.total_calls,
                "conversion_rate": report.performance_metrics.conversion_rate,
                "total_revenue": report.performance_metrics.total_revenue,
                "revenue_leakage": report.performance_metrics.revenue_leakage
            },
            "issues": [
                {
                    "type": i.issue_type.value,
                    "severity": i.severity.value,
                    "root_cause": i.root_cause,
                    "revenue_impact": i.revenue_impact,
                    "affected_calls": i.affected_calls
                }
                for i in report.issues
            ],
            "recommendations": [
                {
                    "priority": r.priority,
                    "action": r.action,
                    "expected_impact": r.expected_impact,
                    "effort": r.implementation_effort,
                    "estimated_time": r.estimated_time
                }
                for r in report.recommendations[:5]  # Top 5
            ],
            "alerts": [
                {
                    "severity": a.severity.value,
                    "title": a.title,
                    "message": a.message,
                    "triggered_at": a.triggered_at.isoformat()
                }
                for a in report.active_alerts
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/{campaign_id}")
def get_campaign_health(campaign_id: str):
    """Quick health check for a campaign"""
    
    config = load_campaign_config(campaign_id)
    
    # Load last 7 days of calls
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    calls = db.load_calls(campaign_id, start_date, end_date)
    
    # Quick status
    intelligence = VoiceBotIntelligence(config)
    status = intelligence.get_quick_status(calls)
    
    return status

@app.get("/alerts/{campaign_id}")
def get_alerts(
    campaign_id: str,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = False
):
    """Get active alerts for a campaign"""
    
    query = """
        SELECT alert_id, alert_type, severity, title, message, triggered_at
        FROM alerts
        WHERE campaign_id = %s
          AND acknowledged = %s
    """
    
    params = [campaign_id, acknowledged]
    
    if severity:
        query += " AND severity = %s"
        params.append(severity)
    
    query += " ORDER BY triggered_at DESC LIMIT 50"
    
    cursor = db.conn.cursor()
    cursor.execute(query, params)
    
    alerts = [
        {
            "id": row[0],
            "type": row[1],
            "severity": row[2],
            "title": row[3],
            "message": row[4],
            "triggered_at": row[5].isoformat()
        }
        for row in cursor.fetchall()
    ]
    
    return {"alerts": alerts}

def load_campaign_config(campaign_id: str) -> CampaignConfig:
    """Load campaign configuration from database"""
    
    query = """
        SELECT campaign_name, start_date, target_calls_per_day,
               target_conversion_rate, target_revenue_per_call, avg_deal_value
        FROM campaigns
        WHERE campaign_id = %s
    """
    
    cursor = db.conn.cursor()
    cursor.execute(query, (campaign_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return CampaignConfig(
        campaign_id=campaign_id,
        campaign_name=row[0],
        start_date=row[1],
        target_calls_per_day=row[2],
        target_conversion_rate=float(row[3]),
        target_revenue_per_call=float(row[4]),
        avg_deal_value=float(row[5]),
        compliance_rules=[],
        script_versions=[]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Run the API

```bash
# Install dependencies
pip install fastapi uvicorn psycopg2-binary

# Run server
python api.py

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## 💻 Step 3: Frontend Dashboard

### React Dashboard (Example)

```jsx
// Dashboard.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function Dashboard() {
  const [campaignId, setCampaignId] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeCapaign = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/analyze/${campaignId}`, {
        days_back: 7,
        compare_previous: true
      });
      setReport(response.data);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
    setLoading(false);
  };

  return (
    <div className="dashboard">
      <h1>Voice Bot Intelligence</h1>
      
      {/* Campaign Selector */}
      <div className="selector">
        <input 
          type="text"
          placeholder="Campaign ID"
          value={campaignId}
          onChange={(e) => setCampaignId(e.target.value)}
        />
        <button onClick={analyzeCapaign} disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {/* Health Score */}
      {report && (
        <>
          <div className="health-card">
            <h2>Health Score</h2>
            <div className="score-circle" style={{
              backgroundColor: report.health_score.overall >= 70 ? '#22c55e' : '#ef4444'
            }}>
              {report.health_score.overall}/100
            </div>
            <p>{report.health_score.status}</p>
            <p className="trend">
              {report.health_score.trend === 'improving' ? '📈' : '📉'}
              {report.health_score.trend}
            </p>
          </div>

          {/* Key Metrics */}
          <div className="metrics-grid">
            <div className="metric">
              <h3>Total Calls</h3>
              <p>{report.metrics.total_calls.toLocaleString()}</p>
            </div>
            <div className="metric">
              <h3>Conversion Rate</h3>
              <p>{(report.metrics.conversion_rate * 100).toFixed(1)}%</p>
            </div>
            <div className="metric">
              <h3>Revenue</h3>
              <p>${report.metrics.total_revenue.toLocaleString()}</p>
            </div>
            <div className="metric">
              <h3>Revenue Leakage</h3>
              <p className="warning">
                ${report.metrics.revenue_leakage.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Alerts */}
          {report.alerts.length > 0 && (
            <div className="alerts">
              <h2>🚨 Active Alerts ({report.alerts.length})</h2>
              {report.alerts.map((alert, i) => (
                <div key={i} className={`alert alert-${alert.severity}`}>
                  <strong>{alert.title}</strong>
                  <p>{alert.message}</p>
                </div>
              ))}
            </div>
          )}

          {/* Issues */}
          {report.issues.length > 0 && (
            <div className="issues">
              <h2>Detected Issues</h2>
              {report.issues.map((issue, i) => (
                <div key={i} className="issue">
                  <span className={`badge badge-${issue.severity}`}>
                    {issue.severity}
                  </span>
                  <div>
                    <strong>{issue.type.replace(/_/g, ' ')}</strong>
                    <p>{issue.root_cause}</p>
                    <p className="impact">
                      Impact: ${issue.revenue_impact.toLocaleString()} 
                      ({issue.affected_calls} calls)
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recommendations */}
          {report.recommendations.length > 0 && (
            <div className="recommendations">
              <h2>💡 Top Recommendations</h2>
              {report.recommendations.map((rec, i) => (
                <div key={i} className="recommendation">
                  <div className="priority">P{rec.priority}</div>
                  <div>
                    <h3>{rec.action}</h3>
                    <p>{rec.expected_impact}</p>
                    <div className="meta">
                      <span>Effort: {rec.effort}</span>
                      <span>Time: {rec.estimated_time}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Dashboard;
```

## 🔄 Step 4: Automated Reporting

### Scheduled Job (Celery)

```python
# tasks.py
from celery import Celery
from datetime import datetime, timedelta

app = Celery('voice_bot_intelligence')

@app.task
def generate_weekly_report(campaign_id: str):
    """
    Generate weekly intelligence report
    Runs every Monday at 9 AM
    """
    
    # Load campaign
    config = load_campaign_config(campaign_id)
    
    # Load data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    current_calls = db.load_calls(campaign_id, start_date, end_date)
    
    prev_end = start_date
    prev_start = prev_end - timedelta(days=7)
    previous_calls = db.load_calls(campaign_id, prev_start, prev_end)
    
    # Generate report
    intelligence = VoiceBotIntelligence(config)
    report = intelligence.analyze_campaign(current_calls, previous_calls)
    
    # Save to database
    report_id = db.save_report(report)
    
    # Send email
    send_email_report(report, config.campaign_name)
    
    # Trigger Slack notifications for critical alerts
    critical_alerts = [a for a in report.active_alerts if a.is_critical()]
    if critical_alerts:
        send_slack_alert(campaign_id, critical_alerts)
    
    return report_id

# Schedule
app.conf.beat_schedule = {
    'weekly-reports': {
        'task': 'tasks.generate_weekly_report',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
        'args': ('CAMP_001',)
    }
}
```

## 📱 Step 5: Notifications

### Slack Integration

```python
# notifications.py
import requests

def send_slack_alert(campaign_id: str, alerts: list):
    """Send critical alerts to Slack"""
    
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 Critical Alert - Campaign {campaign_id}"
            }
        }
    ]
    
    for alert in alerts:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{alert.title}*\n{alert.message}"
            }
        })
    
    payload = {"blocks": blocks}
    requests.post(webhook_url, json=payload)
```

## 🚀 Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/voicebot
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=voicebot
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  worker:
    build: .
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - db
      - redis
  
  redis:
    image: redis:7

volumes:
  postgres_data:
```

### Deploy

```bash
# Build and run
docker-compose up -d

# API available at http://localhost:8000
```

## 📊 Complete Flow Example

```bash
# 1. User visits dashboard
# 2. Frontend calls: GET /campaigns
# 3. User selects campaign
# 4. Frontend calls: POST /analyze/{campaign_id}
# 5. API loads calls from database
# 6. Intelligence engine analyzes data
# 7. Results saved to database
# 8. JSON response sent to frontend
# 9. Dashboard displays health, issues, recommendations
# 10. If critical alerts, Slack notification sent
```

## ✅ Success!

You now have:
- ✅ Complete backend intelligence logic
- ✅ Database schema and integration
- ✅ REST API layer
- ✅ Frontend dashboard example
- ✅ Automated reporting
- ✅ Notification system
- ✅ Docker deployment

Ready for production! 🎉
