import streamlit as st

st.set_page_config(page_title="Quality Intelligence Engine", page_icon="🎯", layout="wide")

# Simple CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a0a2e 50%, #0a0e1a 100%);
    }
    h1, h2, h3 {
        color: #00f5ff !important;
    }
</style>
""", unsafe_allow_html=True)


# Title
st.title("🎯 Quality Intelligence Engine V3.0")
st.markdown("### Real-time Analytics Dashboard")

st.markdown("---")

# Navigation
st.sidebar.title("📊 Navigation")
PAGE = st.sidebar.radio(
    "Select Module",
    ["🏠 Dashboard", "📄 Audit Sheet", "🔍 Transcript Scanner", "📊 Agent Scorecards", "🤖 Voicebot Audit"]
)

st.sidebar.markdown("---")
st.sidebar.info("Quality Intelligence Engine V3.0")

# Pages
if PAGE == "🏠 Dashboard":
    st.markdown("## 📈 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📞 Total Calls", "1,234", delta="+12%")
    with col2:
        st.metric("⭐ Quality Score", "87.5%", delta="+2.3%")
    with col3:
        st.metric("✅ Compliance", "95.2%", delta="+1.1%")
    
    st.success("✅ All systems operational")
    st.info("💡 Dashboard is working! Add your modules using the sidebar.")

elif PAGE == "📄 Audit Sheet":
    st.markdown("## 📄 Audit Sheet Analysis")
    st.info("Upload audit sheets for analysis")
    uploaded = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'])
    if uploaded:
        st.success("File uploaded successfully!")

elif PAGE == "🔍 Transcript Scanner":
    st.markdown("## 🔍 AI-Powered Transcript Scanner")
    st.markdown("Custom red flag detection • Profanity monitoring • Compliance tracking")
    st.markdown("---")
    
    with st.sidebar:
        st.markdown("### ⚙️ Scanner Settings")
        st.markdown("#### 📋 Scan For:")
        check_profanity = st.checkbox("Profanity & Abuse", value=True)
        check_rude = st.checkbox("Rude Behavior", value=True)
        check_unprofessional = st.checkbox("Unprofessional Language", value=True)
        check_deceptive = st.checkbox("Deceptive Language", value=True)
        check_pii = st.checkbox("PII Exposure", value=True)
    
    transcript = st.text_area("📝 Paste Transcript:", height=300, placeholder="Enter transcript...")
    
    if st.button("🔍 Scan for Violations", type="primary", use_container_width=True):
        if transcript:
            with st.spinner("🤖 Analyzing..."):
                import re
                violations = []
                transcript_lower = transcript.lower()
                
                # PROFANITY
                if check_profanity:
                    profanity = ['chodu', 'gandu', 'bhosad', 'bhosada', 'bhosadi', 'bhosadike', 
                                 'bhosadika', 'bhosadiki', 'bakarichod', 'balatakar', 'behen ke laude',
                                 'betichod', 'behenachod', 'bhenachod', 'bahanachod', 'chutiya',
                                 'chutiye', 'chut', 'gand', 'jhatu', 'jhantu', 'madarachod',
                                 'randi', 'teri man ki chut', 'bhadava', 'bhadave', 'kamina', 'kamine',
                                 'harami', 'kutte', 'laude', 'lavade', 'lodu', 'gadde', 'ullu ke patthe',
                                 'hijade', 'bhosadi wala', 'bhosari wala', 'bloody full', 'fucker',
                                 'bhenchod', 'mother fucker', 'man ki chut']
                    
                    for word in profanity:
                        if word in transcript_lower:
                            violations.append({'type': f'Profanity: "{word}"', 'severity': 'CRITICAL', 
                                             'emoji': '🔴', 'confidence': 99, 'category': 'Profanity'})
                
                # RUDE BEHAVIOR
                if check_rude:
                    rude_patterns = [
                        (r'rudely\s+bat|bat\s+rudely', 'Rude Communication'),
                        (r'rude\s+behave|very\s+rude|bahut\s+rude', 'Rude Behavior'),
                        (r'sounding\s+rude|spoke.*rudely|talking.*rudely', 'Speaking Rudely'),
                        (r'behaviour.*issue|behaviour.*bad|not\s+good\s+behaviour', 'Bad Behavior'),
                        (r'behaviour.*not\s+acceptable|agent.*rude', 'Unacceptable Behavior')
                    ]
                    
                    for pattern, desc in rude_patterns:
                        if re.search(pattern, transcript_lower):
                            violations.append({'type': desc, 'severity': 'HIGH', 
                                             'emoji': '🟠', 'confidence': 94, 'category': 'Rude Behavior'})
                
                # UNPROFESSIONAL
                if check_unprofessional:
                    unprofessional = {'stupid': 95, 'mad': 88, 'pagal': 92, 'dumb': 93, 'anapadh': 90}
                    for word, conf in unprofessional.items():
                        if word in transcript_lower:
                            violations.append({'type': f'Unprofessional: "{word}"', 'severity': 'MEDIUM',
                                             'emoji': '🟡', 'confidence': conf, 'category': 'Unprofessional'})
                
                # DECEPTIVE
                if check_deceptive:
                    deceptive = {'jhuth': ('Lie', 96), 'natak': ('Drama', 89), 
                                'falatu': ('Useless', 85), 'galat': ('Wrong', 82)}
                    for word, (desc, conf) in deceptive.items():
                        if word in transcript_lower:
                            violations.append({'type': f'Deceptive: {desc}', 'severity': 'HIGH',
                                             'emoji': '🟠', 'confidence': conf, 'category': 'Deceptive'})
                
                # PII
                if check_pii:
                    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', transcript):
                        violations.append({'type': 'SSN Exposure', 'severity': 'CRITICAL',
                                         'emoji': '🔴', 'confidence': 99, 'category': 'PII'})
                
                # RESULTS
                st.markdown("---")
                st.markdown("## 📊 Results")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total", len(violations))
                with col2:
                    critical = sum(1 for v in violations if v['severity'] == 'CRITICAL')
                    st.metric("Critical", critical, delta=None if critical == 0 else f"-{critical}")
                with col3:
                    high = sum(1 for v in violations if v['severity'] == 'HIGH')
                    st.metric("High", high)
                with col4:
                    if violations:
                        avg = sum(v['confidence'] for v in violations) / len(violations)
                        st.metric("Confidence", f"{avg:.0f}%")
                
                if violations:
                    st.markdown("### 🔍 Violations")
                    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
                    sorted_v = sorted(violations, key=lambda x: severity_order[x['severity']])
                    
                    for i, v in enumerate(sorted_v, 1):
                        with st.expander(f"{v['emoji']} {v['type']} - {v['severity']}", expanded=(i<=5)):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**Category:** {v['category']}")
                                st.markdown(f"**Severity:** {v['severity']}")
                            with col2:
                                st.metric("Confidence", f"{v['confidence']}%")
                            
                            if v['severity'] == 'CRITICAL':
                                st.error("🚨 IMMEDIATE ACTION: Escalate to supervisor")
                            elif v['severity'] == 'HIGH':
                                st.warning("⚠️ ACTION: Coach agent immediately")
                    
                    import pandas as pd
                    df = pd.DataFrame(violations)
                    csv = df.to_csv(index=False)
                    st.download_button("📥 Download Report", csv, 
                                      f"violations_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                      "text/csv", use_container_width=True)
                else:
                    st.success("✅ No violations detected!")
                    st.balloons()
        else:
            st.warning("⚠️ Paste transcript first")
    
    with st.expander("🧪 Test"):
        if st.button("Load Test"):
            st.code("Agent: Aap chutiya ho! Yeh galat hai!\nCustomer: Rude behaviour!\nAgent: Pagal ho tum!")

elif PAGE == "📊 Agent Scorecards":
    st.markdown("## 📊 Agent Scorecards")
    st.info("Agent performance tracking")
    st.write("Feature coming soon!")

elif PAGE == "🤖 Voicebot Audit":
    st.markdown("## 🤖 Voicebot Audit")
    st.info("Voicebot performance analysis")
    st.write("Feature coming soon!")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>Quality Intelligence Engine V3.0</p>", unsafe_allow_html=True)
