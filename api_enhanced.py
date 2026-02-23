"""
Enhanced API Endpoint for Sales Intelligence Dashboard
Includes LLM integration, advanced analytics, and real-time features
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import json
from collections import defaultdict, Counter

# Import intelligence engine
import sys
sys.path.append('.')
from models import CallRecord, CallStatus, DropOffStage, CampaignConfig
from intelligence_engine import VoiceBotIntelligence
from revenue_calculator import RevenueCalculator

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Store for caching reports
report_cache = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'sales-intelligence-api',
        'version': '3.0.0'
    })

@app.route('/api/sales-intelligence/analyze', methods=['POST'])
def analyze_sales_data():
    """
    Main analysis endpoint
    
    Accepts: CSV, XLSX files via multipart/form-data
    Returns: Complete intelligence report with all visualizations
    """
    
    try:
        print("\n" + "="*80)
        print("📊 NEW ANALYSIS REQUEST")
        print("="*80)
        
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        print(f"📁 File: {file.filename}")
        
        # Get optional parameters
        campaign_name = request.form.get('campaign_name', 'Sales Campaign')
        target_conversion = float(request.form.get('target_conversion_rate', 0.15))
        avg_deal_value = float(request.form.get('avg_deal_value', 500))
        
        print(f"🎯 Campaign: {campaign_name}")
        print(f"🎯 Target Conversion: {target_conversion:.1%}")
        print(f"💰 Avg Deal Value: ${avg_deal_value}")
        
        # Read the file
        print("📖 Reading file...")
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Unsupported file format. Use CSV or XLSX'}), 400
        
        print(f"✓ Loaded {len(df)} rows")
        print(f"✓ Columns: {', '.join(df.columns.tolist())}")
        
        # Convert DataFrame to CallRecord objects
        print("🔄 Converting to CallRecord format...")
        calls = convert_dataframe_to_calls(df)
        
        if not calls:
            return jsonify({'error': 'No valid call records found in file'}), 400
        
        print(f"✓ Converted {len(calls)} calls")
        
        # Auto-detect campaign ID
        campaign_id = calls[0].campaign_id if calls else "CAMPAIGN_001"
        
        # Calculate date range
        min_date = min(c.timestamp for c in calls)
        max_date = max(c.timestamp for c in calls)
        print(f"📅 Date Range: {min_date.date()} to {max_date.date()}")
        
        # Create campaign configuration
        config = CampaignConfig(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            start_date=min_date,
            target_calls_per_day=max(200, len(calls) // 7),  # Estimate from data
            target_conversion_rate=target_conversion,
            target_revenue_per_call=avg_deal_value * target_conversion,
            avg_deal_value=avg_deal_value,
            compliance_rules=["disclosure_required", "dnc_respect"],
            script_versions=list(set(c.script_version for c in calls if c.script_version))
        )
        
        # Run intelligence analysis
        print("\n🧠 Running Intelligence Analysis...")
        print("-" * 80)
        intelligence = VoiceBotIntelligence(config)
        report = intelligence.analyze_campaign(current_calls=calls)
        print("-" * 80)
        print("✅ Analysis Complete!\n")
        
        # Calculate additional analytics for frontend
        print("📊 Generating visualizations...")
        
        # Conversion trends (daily)
        conversion_trends = calculate_conversion_trends(calls)
        print(f"✓ Conversion trends: {len(conversion_trends)} data points")
        
        # Revenue leakage breakdown
        revenue_calc = RevenueCalculator(config)
        leakage = revenue_calc.calculate_leakage(calls, report.performance_metrics)
        print(f"✓ Revenue leakage: ${leakage.total_leakage:,.0f}")
        
        # Escalation analysis
        escalation_breakdown = get_escalation_breakdown(calls)
        print(f"✓ Escalation reasons: {len(escalation_breakdown)}")
        
        # Build comprehensive response
        result = {
            'success': True,
            'generated_at': datetime.now().isoformat(),
            
            # Campaign info
            'campaign_info': {
                'id': campaign_id,
                'name': campaign_name,
                'period': {
                    'start': min_date.isoformat(),
                    'end': max_date.isoformat(),
                    'days': (max_date - min_date).days + 1
                },
                'total_calls': len(calls),
                'calls_per_day': len(calls) / max(1, (max_date - min_date).days + 1)
            },
            
            # Health Score
            'health_score': {
                'overall': report.health_score.overall_score,
                'status': report.health_score.health_status(),
                'trend': report.health_score.trend,
                'week_over_week_change': report.health_score.week_over_week_change,
                'components': {
                    'conversion': report.health_score.conversion_health,
                    'revenue': report.health_score.revenue_health,
                    'compliance': report.health_score.compliance_health,
                    'efficiency': report.health_score.efficiency_health,
                    'quality': report.health_score.quality_health
                }
            },
            
            # Key Metrics
            'metrics': {
                'total_calls': report.performance_metrics.total_calls,
                'completed_calls': report.performance_metrics.completed_calls,
                'dropped_calls': report.performance_metrics.dropped_calls,
                'escalated_calls': report.performance_metrics.escalated_calls,
                'failed_calls': report.performance_metrics.failed_calls,
                'compliance_violations': report.performance_metrics.compliance_violations,
                
                'conversion_rate': round(report.performance_metrics.conversion_rate * 100, 1),
                'conversions': report.performance_metrics.conversions,
                
                'total_revenue': round(report.performance_metrics.total_revenue, 2),
                'expected_revenue': round(report.performance_metrics.expected_revenue, 2),
                'revenue_leakage': round(report.performance_metrics.revenue_leakage, 2),
                'revenue_leakage_percentage': round(report.performance_metrics.revenue_leakage_percentage, 1),
                
                'avg_call_duration': round(report.performance_metrics.avg_call_duration, 0),
                'avg_sentiment': round(report.performance_metrics.avg_sentiment_score, 2),
                
                'completion_rate': round(report.performance_metrics.completion_rate() * 100, 1),
                'escalation_rate': round(report.performance_metrics.escalation_rate() * 100, 1),
                'drop_off_rate': round((report.performance_metrics.dropped_calls / report.performance_metrics.total_calls * 100), 1) if report.performance_metrics.total_calls > 0 else 0
            },
            
            # Revenue Leakage Breakdown
            'revenue_leakage_breakdown': {
                'total': leakage.total_leakage,
                'by_source': [
                    {'source': source.replace('_', ' ').title(), 'amount': round(amount, 2)}
                    for source, amount in leakage.top_3_reasons
                ],
                'by_stage': {k: round(v, 2) for k, v in leakage.leakage_by_stage.items()},
                'recoverable': round(leakage.recoverable_amount, 2),
                'difficulty': leakage.recovery_difficulty,
                'scenarios': {
                    'if_conversion_improved': round(leakage.if_conversion_improved, 2),
                    'if_dropoff_reduced': round(leakage.if_dropoff_reduced, 2),
                    'if_escalations_handled': round(leakage.if_escalations_handled, 2)
                }
            },
            
            # Win/Loss Analysis
            'win_loss_analysis': {
                'wins': report.performance_metrics.conversions,
                'losses': report.performance_metrics.total_calls - report.performance_metrics.conversions,
                'win_rate': round(report.performance_metrics.conversion_rate * 100, 1),
                'avg_win_value': avg_deal_value,
                'avg_loss_value': 0,
                'total_won_revenue': round(report.performance_metrics.total_revenue, 2),
                'total_lost_revenue': round(report.performance_metrics.revenue_leakage, 2)
            },
            
            # Escalation Impact
            'escalation_impact': {
                'total_escalations': report.performance_metrics.escalated_calls,
                'escalation_rate': round(report.performance_metrics.escalation_rate() * 100, 1),
                'cost_per_escalation': 50,
                'total_cost': report.performance_metrics.escalated_calls * 50,
                'reasons': escalation_breakdown
            },
            
            # Conversion Trends (for charts)
            'conversion_trends': conversion_trends,
            
            # Drop-off by Stage
            'drop_off_by_stage': [
                {'stage': stage.value.replace('_', ' ').title(), 'count': count}
                for stage, count in report.performance_metrics.drop_off_by_stage.items()
            ],
            
            # Issues
            'issues': [
                {
                    'id': issue.issue_id,
                    'type': issue.issue_type.value,
                    'severity': issue.severity.value,
                    'title': issue.issue_type.value.replace('_', ' ').title(),
                    'root_cause': issue.root_cause,
                    'revenue_impact': round(issue.revenue_impact, 2),
                    'affected_calls': issue.affected_calls,
                    'contributing_factors': issue.contributing_factors,
                    'problematic_stage': issue.problematic_stage.value if issue.problematic_stage else None
                }
                for issue in report.issues
            ],
            
            # Recommendations
            'recommendations': [
                {
                    'id': rec.recommendation_id,
                    'priority': rec.priority,
                    'action': rec.action,
                    'expected_impact': rec.expected_impact,
                    'expected_revenue_recovery': round(rec.expected_revenue_recovery, 2),
                    'expected_conversion_lift': round(rec.expected_conversion_lift, 2),
                    'implementation_effort': rec.implementation_effort,
                    'estimated_time': rec.estimated_time,
                    'confidence': round(rec.confidence_score, 2),
                    'steps': rec.steps,
                    'resources_needed': rec.resources_needed
                }
                for rec in report.recommendations
            ],
            
            # Alerts
            'alerts': [
                {
                    'id': alert.alert_id,
                    'type': alert.alert_type,
                    'severity': alert.severity.value,
                    'title': alert.title,
                    'message': alert.message,
                    'metric_name': alert.metric_name,
                    'current_value': alert.current_value,
                    'previous_value': alert.previous_value,
                    'percentage_change': round(alert.percentage_change, 1),
                    'triggered_at': alert.triggered_at.isoformat()
                }
                for alert in report.active_alerts
            ],
            
            # Summary for AI
            'ai_summary': {
                'executive_summary': report.summary,
                'key_insights': report.key_insights,
                'urgent_actions': report.urgent_actions,
                'context': f"Campaign '{campaign_name}' analyzed {len(calls)} calls from {min_date.date()} to {max_date.date()}. "
                          f"Health score: {report.health_score.overall_score}/100. "
                          f"Conversion rate: {report.performance_metrics.conversion_rate:.1%}. "
                          f"Revenue leakage: ${report.performance_metrics.revenue_leakage:,.0f}."
            }
        }
        
        # Cache the report
        report_cache[campaign_id] = result
        
        print("="*80)
        print("📤 RESPONSE SUMMARY")
        print("="*80)
        print(f"✓ Health Score: {result['health_score']['overall']}/100")
        print(f"✓ Total Revenue: ${result['metrics']['total_revenue']:,.0f}")
        print(f"✓ Revenue Leakage: ${result['metrics']['revenue_leakage']:,.0f}")
        print(f"✓ Issues: {len(result['issues'])}")
        print(f"✓ Recommendations: {len(result['recommendations'])}")
        print(f"✓ Alerts: {len(result['alerts'])}")
        print("="*80 + "\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), 500


def convert_dataframe_to_calls(df):
    """Convert uploaded CSV/Excel to CallRecord objects"""
    
    calls = []
    errors = 0
    
    for idx, row in df.iterrows():
        try:
            # Parse status
            status_str = str(row.get('status', 'completed')).lower()
            if status_str in ['completed', 'complete', 'success', 'won']:
                status = CallStatus.COMPLETED
            elif status_str in ['dropped', 'drop', 'hangup', 'abandoned']:
                status = CallStatus.DROPPED
            elif status_str in ['escalated', 'escalate', 'transfer', 'transferred']:
                status = CallStatus.ESCALATED
            elif status_str in ['failed', 'fail', 'error']:
                status = CallStatus.FAILED
            elif 'compliance' in status_str or 'violation' in status_str:
                status = CallStatus.COMPLIANCE_VIOLATION
            else:
                status = CallStatus.COMPLETED
            
            # Parse drop-off stage
            drop_stage = None
            if pd.notna(row.get('drop_off_stage')) or pd.notna(row.get('stage')):
                stage_str = str(row.get('drop_off_stage') or row.get('stage', '')).lower()
                if 'intro' in stage_str:
                    drop_stage = DropOffStage.INTRO
                elif 'qual' in stage_str:
                    drop_stage = DropOffStage.QUALIFICATION
                elif 'pitch' in stage_str:
                    drop_stage = DropOffStage.PITCH
                elif 'object' in stage_str:
                    drop_stage = DropOffStage.OBJECTION_HANDLING
                elif 'clos' in stage_str:
                    drop_stage = DropOffStage.CLOSING
                elif 'follow' in stage_str:
                    drop_stage = DropOffStage.FOLLOW_UP
            
            # Parse timestamp
            timestamp_str = row.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp_str, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    timestamp = pd.to_datetime(timestamp_str)
            else:
                timestamp = pd.to_datetime(timestamp_str)
            
            # Parse compliance flags
            compliance_flags = []
            if pd.notna(row.get('compliance_flags')):
                flags_str = str(row.get('compliance_flags'))
                compliance_flags = [f.strip() for f in flags_str.split(',') if f.strip()]
            
            call = CallRecord(
                call_id=str(row.get('call_id', f"CALL_{len(calls):06d}")),
                campaign_id=str(row.get('campaign_id', 'CAMPAIGN_001')),
                timestamp=timestamp,
                duration_seconds=int(row.get('duration_seconds', row.get('duration', 0))),
                status=status,
                drop_off_stage=drop_stage,
                escalation_reason=str(row.get('escalation_reason', '')) if pd.notna(row.get('escalation_reason')) else None,
                compliance_flags=compliance_flags,
                conversion_value=float(row.get('conversion_value', row.get('expected_value', 500))),
                actual_revenue=float(row.get('actual_revenue', row.get('revenue', 0))),
                sentiment_score=float(row.get('sentiment_score', row.get('sentiment', 0))),
                script_version=str(row.get('script_version', 'v1.0')),
                agent_id=str(row.get('agent_id', '')) if pd.notna(row.get('agent_id')) else None
            )
            
            calls.append(call)
            
        except Exception as e:
            errors += 1
            if errors <= 5:  # Only print first 5 errors
                print(f"⚠️ Row {idx + 1}: {str(e)}")
    
    if errors > 0:
        print(f"⚠️ Skipped {errors} invalid rows")
    
    return calls


def calculate_conversion_trends(calls):
    """Calculate daily conversion trends for visualization"""
    
    # Group by date
    daily = defaultdict(lambda: {'calls': 0, 'conversions': 0, 'revenue': 0})
    
    for call in calls:
        date_key = call.timestamp.date().isoformat()
        daily[date_key]['calls'] += 1
        if call.actual_revenue > 0:
            daily[date_key]['conversions'] += 1
            daily[date_key]['revenue'] += call.actual_revenue
    
    # Calculate rates and format for charts
    trends = []
    for date_str in sorted(daily.keys()):
        data = daily[date_str]
        rate = (data['conversions'] / data['calls'] * 100) if data['calls'] > 0 else 0
        trends.append({
            'date': date_str,
            'calls': data['calls'],
            'conversions': data['conversions'],
            'conversion_rate': round(rate, 1),
            'revenue': round(data['revenue'], 2)
        })
    
    return trends


def get_escalation_breakdown(calls):
    """Get breakdown of escalation reasons for visualization"""
    
    escalated = [c for c in calls if c.status == CallStatus.ESCALATED and c.escalation_reason]
    reasons = Counter(c.escalation_reason for c in escalated)
    
    return [
        {
            'reason': reason.replace('_', ' ').title(),
            'count': count,
            'percentage': round(count / len(escalated) * 100, 1) if escalated else 0
        }
        for reason, count in reasons.most_common(10)
    ]


if __name__ == '__main__':
    print("="*80)
    print("🚀 SALES INTELLIGENCE API SERVER")
    print("="*80)
    print("📡 Endpoint: http://localhost:5000")
    print("📊 Analyze: POST /api/sales-intelligence/analyze")
    print("💊 Health: GET /api/health")
    print("="*80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
