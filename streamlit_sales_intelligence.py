"""
Sales Intelligence Module for Quality Intelligence Engine
Analyzes voice bot campaign performance with AI-powered insights
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Add the voice_bot_intelligence folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'voice_bot_intelligence'))

from models import CallRecord, CallStatus, DropOffStage, CampaignConfig
from intelligence_engine import VoiceBotIntelligence

# Page config
st.set_page_config(page_title="Sales Intelligence", page_icon="📊", layout="wide")

# Custom CSS - Neon Noir Theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a0a2e 50%, #0a0e1a 100%);
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #00f5ff;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    /* Cards with glassmorphism */
    .css-1r6slb0 {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    /* Headers with neon glow */
    h1, h2, h3 {
        color: #00f5ff !important;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed #00f5ff;
        border-radius: 12px;
        padding: 2rem;
    }
    
    /* Success/Error boxes */
    .stAlert {
        background: rgba(0, 245, 255, 0.1);
        border-left: 4px solid #00f5ff;
    }
</style>
""", unsafe_allow_html=True)

# Title with gradient
st.markdown("""
<h1 style='background: linear-gradient(90deg, #00f5ff 0%, #ff00ff 100%); 
           -webkit-background-clip: text; 
           -webkit-text-fill-color: transparent;
           font-size: 3rem;
           font-weight: bold;
           margin-bottom: 0;'>
📊 Sales Intelligence
</h1>
<p style='color: #888; font-size: 1.2rem; margin-top: 0;'>
Upload sales call data — revenue leakage, win/loss patterns, campaign performance
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar info
with st.sidebar:
    st.markdown("### 📋 What this module analyzes")
    st.markdown("""
    ✅ Campaign health scores  
    ✅ Revenue leakage by source  
    ✅ Win/loss analysis  
    ✅ Escalation impact on revenue  
    ✅ Conversion rate trends  
    ✅ AI recommendations
    """)
    
    st.markdown("### 📊 Supported CSV Format")
    st.code("""
call_id,timestamp,duration_seconds,
status,conversion_value,
actual_revenue,sentiment_score
    """, language="csv")
    
    st.markdown("### 🎯 Campaign Settings")
    target_conversion = st.slider("Target Conversion Rate (%)", 5, 50, 15) / 100
    avg_deal_value = st.number_input("Avg Deal Value ($)", 100, 10000, 500, 100)

# File uploader
st.markdown("### 📤 Upload Your Sales Campaign Data")
uploaded_file = st.file_uploader(
    "Drag and drop your CSV or Excel file here",
    type=['csv', 'xlsx', 'xls'],
    help="Upload your sales call data with call_id, timestamp, status, revenue, etc."
)

if uploaded_file is not None:
    try:
        # Load data
        with st.spinner("📖 Reading file..."):
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Loaded {len(df)} calls from {uploaded_file.name}")
        
        # Show preview
        with st.expander("👀 Preview Data", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Convert to CallRecord objects
        with st.spinner("🔄 Converting to CallRecord format..."):
            calls = []
            for idx, row in df.iterrows():
                try:
                    # Parse status
                    status_str = str(row.get('status', 'completed')).lower()
                    if 'complet' in status_str:
                        status = CallStatus.COMPLETED
                    elif 'drop' in status_str:
                        status = CallStatus.DROPPED
                    elif 'escal' in status_str:
                        status = CallStatus.ESCALATED
                    elif 'fail' in status_str:
                        status = CallStatus.FAILED
                    else:
                        status = CallStatus.COMPLETED
                    
                    # Parse timestamp
                    timestamp = pd.to_datetime(row.get('timestamp', datetime.now()))
                    
                    call = CallRecord(
                        call_id=str(row.get('call_id', f"CALL_{idx:06d}")),
                        campaign_id=str(row.get('campaign_id', 'CAMPAIGN_001')),
                        timestamp=timestamp,
                        duration_seconds=int(row.get('duration_seconds', row.get('duration', 0))),
                        status=status,
                        drop_off_stage=None,
                        escalation_reason=str(row.get('escalation_reason', '')) if pd.notna(row.get('escalation_reason')) else None,
                        compliance_flags=[],
                        conversion_value=float(row.get('conversion_value', avg_deal_value)),
                        actual_revenue=float(row.get('actual_revenue', 0)),
                        sentiment_score=float(row.get('sentiment_score', 0)),
                        script_version=str(row.get('script_version', 'v1.0')),
                        agent_id=None
                    )
                    calls.append(call)
                except Exception as e:
                    continue
            
            st.success(f"✅ Converted {len(calls)} valid calls")
        
        if len(calls) == 0:
            st.error("❌ No valid calls found in file. Check your data format.")
            st.stop()
        
        # Create config
        campaign_id = calls[0].campaign_id
        min_date = min(c.timestamp for c in calls)
        
        config = CampaignConfig(
            campaign_id=campaign_id,
            campaign_name=uploaded_file.name.replace('.csv', '').replace('.xlsx', ''),
            start_date=min_date,
            target_calls_per_day=200,
            target_conversion_rate=target_conversion,
            target_revenue_per_call=avg_deal_value * target_conversion,
            avg_deal_value=avg_deal_value,
            compliance_rules=[],
            script_versions=[]
        )
        
        # Run analysis
        with st.spinner("🧠 Running AI intelligence analysis..."):
            intelligence = VoiceBotIntelligence(config)
            report = intelligence.analyze_campaign(current_calls=calls)
        
        st.success("✅ Analysis complete!")
        
        # === DISPLAY RESULTS ===
        
        st.markdown("---")
        st.markdown("## 📊 Campaign Overview")
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🏥 Health Score",
                f"{report.health_score.overall_score}/100",
                delta=f"{report.health_score.trend}",
                help="Overall campaign health based on conversion, revenue, compliance, efficiency, quality"
            )
        
        with col2:
            st.metric(
                "📞 Total Calls",
                f"{report.performance_metrics.total_calls:,}",
                help="Total number of calls in this campaign"
            )
        
        with col3:
            st.metric(
                "🎯 Conversion Rate",
                f"{report.performance_metrics.conversion_rate*100:.1f}%",
                delta=f"{(report.performance_metrics.conversion_rate - target_conversion)*100:.1f}%",
                help="Percentage of calls that converted to sales"
            )
        
        with col4:
            st.metric(
                "💰 Total Revenue",
                f"${report.performance_metrics.total_revenue:,.0f}",
                help="Total revenue generated from conversions"
            )
        
        # Revenue Leakage Alert
        if report.performance_metrics.revenue_leakage > 0:
            st.markdown("---")
            st.error(f"""
            **⚠️ Revenue Leakage Detected**  
            You're losing **${report.performance_metrics.revenue_leakage:,.0f}** 
            ({report.performance_metrics.revenue_leakage_percentage:.1f}% of potential revenue)
            """)
        
        # Health Score Breakdown
        st.markdown("---")
        st.markdown("## 🏥 Health Score Breakdown")
        
        fig_health = go.Figure()
        
        categories = ['Conversion', 'Revenue', 'Compliance', 'Efficiency', 'Quality']
        values = [
            report.health_score.conversion_health,
            report.health_score.revenue_health,
            report.health_score.compliance_health,
            report.health_score.efficiency_health,
            report.health_score.quality_health
        ]
        
        fig_health.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Health Components',
            line=dict(color='#00f5ff', width=2),
            fillcolor='rgba(0, 245, 255, 0.3)'
        ))
        
        fig_health.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255, 255, 255, 0.2)'
                ),
                angularaxis=dict(
                    tickfont=dict(color='white', size=12),
                    gridcolor='rgba(255, 255, 255, 0.2)'
                ),
                bgcolor='rgba(0, 0, 0, 0)'
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        st.plotly_chart(fig_health, use_container_width=True)
        
        # Metrics Grid
        st.markdown("---")
        st.markdown("## 📈 Key Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Completion Rates")
            completion_rate = report.performance_metrics.completion_rate() * 100
            st.progress(completion_rate / 100)
            st.write(f"**{completion_rate:.1f}%** of calls completed")
            
            st.markdown("### Drop-off Rate")
            dropoff_rate = (report.performance_metrics.dropped_calls / report.performance_metrics.total_calls) * 100
            st.progress(dropoff_rate / 100)
            st.write(f"**{dropoff_rate:.1f}%** of calls dropped")
        
        with col2:
            st.markdown("### Escalation Rate")
            escalation_rate = report.performance_metrics.escalation_rate() * 100
            st.progress(escalation_rate / 100)
            st.write(f"**{escalation_rate:.1f}%** escalated to agents")
            
            st.markdown("### Avg Call Duration")
            st.write(f"**{report.performance_metrics.avg_call_duration:.0f}** seconds")
        
        with col3:
            st.markdown("### Sentiment Score")
            sentiment_normalized = (report.performance_metrics.avg_sentiment_score + 1) / 2
            st.progress(sentiment_normalized)
            st.write(f"**{report.performance_metrics.avg_sentiment_score:.2f}** average sentiment")
            
            st.markdown("### Compliance Rate")
            compliance_rate = ((report.performance_metrics.total_calls - report.performance_metrics.compliance_violations) / report.performance_metrics.total_calls) * 100
            st.progress(compliance_rate / 100)
            st.write(f"**{compliance_rate:.1f}%** compliant")
        
        # Issues Panel
        st.markdown("---")
        st.markdown("## 🔍 Detected Issues")
        
        if report.issues:
            for issue in report.issues[:5]:
                severity_color = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }
                
                with st.expander(f"{severity_color.get(issue.severity.value, '⚪')} **{issue.issue_type.value.replace('_', ' ').title()}** - ${issue.revenue_impact:,.0f} impact"):
                    st.markdown(f"**Root Cause:** {issue.root_cause}")
                    st.markdown(f"**Severity:** {issue.severity.value.upper()}")
                    st.markdown(f"**Affected Calls:** {issue.affected_calls}")
                    st.markdown(f"**Revenue Impact:** ${issue.revenue_impact:,.0f}")
                    if issue.contributing_factors:
                        st.markdown("**Contributing Factors:**")
                        for factor in issue.contributing_factors:
                            st.markdown(f"  • {factor}")
        else:
            st.success("✅ No issues detected - Great job!")
        
        # Recommendations Panel
        st.markdown("---")
        st.markdown("## 💡 AI-Powered Recommendations")
        
        if report.recommendations:
            for rec in report.recommendations[:5]:
                priority_color = {
                    1: '🔴',
                    2: '🟠',
                    3: '🟡',
                    4: '🟢',
                    5: '⚪'
                }
                
                with st.expander(f"{priority_color.get(rec.priority, '⚪')} **Priority {rec.priority}:** {rec.action}"):
                    st.markdown(f"**Expected Impact:** {rec.expected_impact}")
                    st.markdown(f"**Revenue Recovery:** ${rec.expected_revenue_recovery:,.0f}")
                    st.markdown(f"**Conversion Lift:** +{rec.expected_conversion_lift:.1f}%")
                    st.markdown(f"**Implementation Effort:** {rec.implementation_effort}")
                    st.markdown(f"**Estimated Time:** {rec.estimated_time}")
                    st.markdown(f"**Confidence:** {rec.confidence_score:.0%}")
                    
                    if rec.steps:
                        st.markdown("**Steps:**")
                        for i, step in enumerate(rec.steps, 1):
                            st.markdown(f"{i}. {step}")
        else:
            st.info("No recommendations available at this time")
        
        # Export Section
        st.markdown("---")
        st.markdown("## 📥 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export summary as text
            summary = intelligence.export_report_summary(report)
            st.download_button(
                "📄 Download Text Report",
                summary,
                file_name=f"intelligence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        with col2:
            # Export data as CSV
            export_data = {
                'Health Score': [report.health_score.overall_score],
                'Total Calls': [report.performance_metrics.total_calls],
                'Conversion Rate': [f"{report.performance_metrics.conversion_rate*100:.1f}%"],
                'Total Revenue': [report.performance_metrics.total_revenue],
                'Revenue Leakage': [report.performance_metrics.revenue_leakage],
                'Issues Count': [len(report.issues)],
                'Recommendations Count': [len(report.recommendations)]
            }
            export_df = pd.DataFrame(export_data)
            
            st.download_button(
                "📊 Download Summary CSV",
                export_df.to_csv(index=False),
                file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"❌ Error analyzing data: {str(e)}")
        import traceback
        with st.expander("🔍 Error Details"):
            st.code(traceback.format_exc())

else:
    # Show instructions when no file uploaded
    st.info("""
    👆 **Upload your sales campaign data to get started**
    
    The system will analyze:
    - Campaign health and performance
    - Revenue leakage sources
    - Win/loss patterns
    - Escalation impact
    - AI-powered recommendations
    """)
    
    # Sample data format
    st.markdown("### 📋 Example Data Format")
    sample_df = pd.DataFrame({
        'call_id': ['CALL_001', 'CALL_002', 'CALL_003'],
        'timestamp': ['2025-02-20T09:00:00', '2025-02-20T10:00:00', '2025-02-20T11:00:00'],
        'duration_seconds': [240, 180, 300],
        'status': ['completed', 'dropped', 'escalated'],
        'conversion_value': [500, 500, 500],
        'actual_revenue': [500, 0, 500],
        'sentiment_score': [0.7, -0.3, 0.4]
    })
    st.dataframe(sample_df, use_container_width=True)
