elif PAGE == "🔍 Transcript Scanner":
    st.markdown("## 🔍 AI-Powered Transcript Scanner")
    st.markdown("Custom red flag detection • Profanity monitoring • Compliance tracking")
    st.markdown("---")
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### ⚙️ Scanner Settings")
        st.markdown("#### 📋 Scan For:")
        check_profanity = st.checkbox("Profanity & Abuse", value=True)
        check_rude = st.checkbox("Rude Behavior", value=True)
        check_unprofessional = st.checkbox("Unprofessional Language", value=True)
        check_deceptive = st.checkbox("Deceptive Language", value=True)
        check_compliance = st.checkbox("Compliance Violations", value=True)
        check_pii = st.checkbox("PII Exposure", value=True)
    
    # Main scanner
    transcript = st.text_area(
        "📝 Paste Transcript Below:",
        height=300,
        placeholder="Enter the call transcript here to scan for violations..."
    )
    
    if st.button("🔍 Scan for Violations", type="primary", use_container_width=True):
        if transcript:
            with st.spinner("🤖 AI analyzing transcript..."):
                import re
                violations = []
                transcript_lower = transcript.lower()
                
                # ===== PROFANITY & ABUSE (CRITICAL) =====
                if check_profanity:
                    profanity_words = [
                        'chodu', 'gandu', 'bhosad', 'bhosada', 'bhosadi', 'bhosadike', 
                        'bhosadika', 'bhosadiki', 'bakarichod', 'balatakar', 'behen ke laude',
                        'betichod', 'behenachod', 'bhenachod', 'bahanachod', 'chutiya',
                        'chutiye', 'chut', 'gand', 'jhatu', 'jhantu', 'madarachod',
                        'aulad', 'randi', 'teri man ki chut', 'bhadava', 'bhadave',
                        'kamina', 'kamine', 'harami', 'kutte', 'laude', 'lavade',
                        'lodu', 'gadde', 'ullu ke patthe', 'hijade', 'bhosadi wala',
                        'bhosari wala', 'bloody full', 'fucker', 'bhenchod', 'mother fucker',
                        'trotnational trot', 'man ki chut'
                    ]
                    
                    for word in profanity_words:
                        if word in transcript_lower:
                            violations.append({
                                'type': f'Severe Profanity: "{word}"',
                                'severity': 'CRITICAL',
                                'emoji': '🔴',
                                'confidence': 99,
                                'category': 'Profanity & Abuse'
                            })
                
                # ===== RUDE BEHAVIOR (HIGH) =====
                if check_rude:
                    rude_patterns = [
                        (r'rudely\s+bat', 'Rude Communication'),
                        (r'bat\s+rudely', 'Rude Communication'),
                        (r'rude\s+behave', 'Rude Behavior'),
                        (r'very\s+rude', 'Very Rude'),
                        (r'bahut\s+rude', 'Very Rude (Hindi)'),
                        (r'sounding\s+rude', 'Sounding Rude'),
                        (r'spoke.*very\s+rudely', 'Speaking Rudely'),
                        (r'talking\s+very\s+rudely', 'Talking Rudely'),
                        (r'behaviour.*issue', 'Behavior Issue'),
                        (r'behaviour.*bad', 'Bad Behavior'),
                        (r'not\s+good\s+behaviour', 'Not Good Behavior'),
                        (r'behaviour.*not\s+acceptable', 'Unacceptable Behavior'),
                        (r'rude\s+at\s+you', 'Being Rude'),
                        (r'agent.*rude', 'Agent Rudeness'),
                    ]
                    
                    for pattern, desc in rude_patterns:
                        if re.search(pattern, transcript_lower):
                            violations.append({
                                'type': desc,
                                'severity': 'HIGH',
                                'emoji': '🟠',
                                'confidence': 94,
                                'category': 'Rude Behavior'
                            })
                
                # ===== UNPROFESSIONAL LANGUAGE (MEDIUM) =====
                if check_unprofessional:
                    unprofessional_words = {
                        'stupid': 95,
                        'mad': 88,
                        'pagal': 92,
                        'dumb': 93,
                        'anapadh': 90
                    }
                    
                    for word, conf in unprofessional_words.items():
                        if word in transcript_lower:
                            violations.append({
                                'type': f'Unprofessional: "{word}"',
                                'severity': 'MEDIUM',
                                'emoji': '🟡',
                                'confidence': conf,
                                'category': 'Unprofessional Language'
                            })
                
                # ===== DECEPTIVE LANGUAGE (HIGH) =====
                if check_deceptive:
                    deceptive_words = {
                        'jhuth': ('Lie/Falsehood', 96),
                        'natak': ('Drama/Acting', 89),
                        'falatu': ('Useless/Wasteful', 85),
                        'galat': ('Wrong/Incorrect', 82)
                    }
                    
                    for word, (desc, conf) in deceptive_words.items():
                        if word in transcript_lower:
                            violations.append({
                                'type': f'Deceptive Language: {desc}',
                                'severity': 'HIGH',
                                'emoji': '🟠',
                                'confidence': conf,
                                'category': 'Deceptive Language'
                            })
                
                # ===== COMPLIANCE VIOLATIONS (HIGH) =====
                if check_compliance:
                    if re.search(r'\b(guarantee|promise|assure you will)\b', transcript_lower):
                        violations.append({
                            'type': 'Unauthorized Guarantee',
                            'severity': 'HIGH',
                            'emoji': '🔴',
                            'confidence': 92,
                            'category': 'Compliance'
                        })
                    if re.search(r'\b(must|have to) (buy|purchase)\b', transcript_lower):
                        violations.append({
                            'type': 'Pressure Language',
                            'severity': 'MEDIUM',
                            'emoji': '🟡',
                            'confidence': 85,
                            'category': 'Compliance'
                        })
                
                # ===== PII EXPOSURE (CRITICAL) =====
                if check_pii:
                    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', transcript):
                        violations.append({
                            'type': 'SSN Exposure',
                            'severity': 'CRITICAL',
                            'emoji': '🔴',
                            'confidence': 99,
                            'category': 'PII Exposure'
                        })
                    if re.search(r'\b\d{16}\b', transcript):
                        violations.append({
                            'type': 'Credit Card Number',
                            'severity': 'CRITICAL',
                            'emoji': '🔴',
                            'confidence': 99,
                            'category': 'PII Exposure'
                        })
                
                # ===== DISPLAY RESULTS =====
                st.markdown("---")
                st.markdown("## 📊 Scan Results")
                
                # Summary Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Violations", len(violations))
                with col2:
                    critical = sum(1 for v in violations if v['severity'] == 'CRITICAL')
                    st.metric("Critical", critical, delta=None if critical == 0 else f"-{critical}")
                with col3:
                    high = sum(1 for v in violations if v['severity'] == 'HIGH')
                    st.metric("High", high)
                with col4:
                    if violations:
                        avg_conf = sum(v['confidence'] for v in violations) / len(violations)
                        st.metric("Avg Confidence", f"{avg_conf:.0f}%")
                    else:
                        st.metric("Avg Confidence", "N/A")
                
                # Category Breakdown
                if violations:
                    st.markdown("### 📊 Violations by Category")
                    
                    from collections import Counter
                    category_counts = Counter(v['category'] for v in violations)
                    
                    cols = st.columns(len(category_counts))
                    for i, (cat, count) in enumerate(category_counts.items()):
                        with cols[i]:
                            st.metric(cat, count)
                
                # Detailed Violations
                if violations:
                    st.markdown("### 🔍 Detected Violations")
                    
                    # Sort by severity
                    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                    sorted_violations = sorted(violations, key=lambda x: severity_order[x['severity']])
                    
                    for i, v in enumerate(sorted_violations, 1):
                        with st.expander(f"{v['emoji']} {v['type']} - {v['severity']}", expanded=(i <= 5)):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Category:** {v['category']}")
                                st.markdown(f"**Severity:** {v['severity']}")
                            
                            with col2:
                                st.metric("Confidence", f"{v['confidence']}%")
                            
                            # Action recommendations
                            if v['severity'] == 'CRITICAL':
                                st.error("🚨 **IMMEDIATE ACTION:** Remove agent from calls. Escalate to supervisor.")
                            elif v['severity'] == 'HIGH':
                                st.warning("⚠️ **ACTION NEEDED:** Coach agent immediately. Review recording.")
                            else:
                                st.info("💡 **RECOMMENDATION:** Add to training queue.")
                    
                    # Export
                    st.markdown("---")
                    import pandas as pd
                    df_violations = pd.DataFrame(violations)
                    csv = df_violations.to_csv(index=False)
                    
                    st.download_button(
                        "📥 Download Violation Report",
                        csv,
                        f"violations_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                else:
                    st.success("✅ **No violations detected!** This transcript is compliant.")
                    st.balloons()
        else:
            st.warning("⚠️ Please paste a transcript to scan")
    
    # Test data
    with st.expander("🧪 Test with Sample Violations"):
        if st.button("Load Hindi Profanity Test"):
            st.code("""Agent: Aap chutiya ho kya? Yeh bahut galat hai!
Customer: Kya bol rahe ho?
Agent: Tum pagal ho! Yeh natak band karo!
Customer: Yeh kaisa behaviour hai?
Agent: Bloody full gandu! Randi rona band karo!""")
            st.warning("⚠️ This contains severe violations - use for testing only!")
        
        if st.button("Load Rude Behavior Test"):
            st.code("""Agent: You are being very rude right now.
Customer: No, you are talking very rudely to me!
Agent: This is not good behaviour from you.
Customer: Your behaviour is not acceptable.
Agent: Stop being so stupid and mad!""")
            st.info("💡 This tests rude behavior and unprofessional language detection")
