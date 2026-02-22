# ============================================================
# app.py  —  Quality Intelligence Engine v3
# Upload audit sheet or transcripts — app does everything.
# Run with: streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
import zipfile, io, os
from datetime import datetime

from smart_detector  import auto_prepare, get_score_columns
from tni_module      import validate_csv as tni_val, build_tni_summary, compute_agent_stats
from calibration_module import validate_csv as cal_val, build_calibration_summary
from ata_module      import validate_csv as ata_val, build_ata_summary
from redflag_module  import DEFAULT_FLAGS, parse_custom_rules, scan_transcript, build_redflag_summary
from scorecard_module import build_agent_profile, generate_scorecard_pdf, get_agent_list
from viz_module      import (score_bar_chart, agent_radar_chart, trend_line_chart,
                              agent_league_table_chart, variance_heatmap,
                              auditor_accuracy_chart, flag_severity_donut, render_chart)
from ai_engine       import (analyse_tni, analyse_calibration, analyse_red_flags,
                              generate_agent_scorecard, analyse_ata)

st.set_page_config(page_title="Quality Intelligence Engine", page_icon="🧠",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif;}
.stApp{background:#070b14;color:#dde3f0;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a0f1e,#060a16);border-right:1px solid #0f1e3d;}
.qie-card{background:linear-gradient(135deg,#0d1426,#111c38);border:1px solid #152040;border-radius:16px;padding:20px 22px;text-align:center;position:relative;overflow:hidden;transition:transform .2s;}
.qie-card:hover{transform:translateY(-2px);border-color:var(--ac,#3b82f6);}
.qie-card::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--ac,#3b82f6);}
.qie-card .v{font-size:2.2rem;font-weight:800;color:var(--ac,#3b82f6);line-height:1;margin-bottom:5px;}
.qie-card .l{font-size:0.7rem;color:#475569;letter-spacing:.1em;text-transform:uppercase;font-weight:600;}
.sec{background:linear-gradient(90deg,#0f1e40,#070b14);border-left:3px solid var(--ac,#3b82f6);border-radius:0 10px 10px 0;padding:10px 16px;margin:22px 0 10px;font-size:0.8rem;font-weight:700;color:#7eb8ff;letter-spacing:.1em;text-transform:uppercase;}
.sec.amber{--ac:#f59e0b;border-left-color:#f59e0b;color:#fcd34d;}
.sec.red{--ac:#ef4444;border-left-color:#ef4444;color:#fca5a5;}
.sec.green{--ac:#10b981;border-left-color:#10b981;color:#6ee7b7;}
.sec.purple{--ac:#8b5cf6;border-left-color:#8b5cf6;color:#c4b5fd;}
.ai-box{background:#09101f;border:1px solid #152040;border-radius:14px;padding:22px 26px;font-size:0.88rem;line-height:1.8;color:#c8d5ea;}
.ai-box h2{color:#60a5fa;font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin:20px 0 7px;padding-bottom:5px;border-bottom:1px solid #152040;}
.ai-box h3{color:#93c5fd;font-size:0.88rem;margin:12px 0 4px;}
.ai-box strong{color:#e2e8f0;}.ai-box ul{padding-left:18px;}.ai-box li{margin-bottom:4px;}
.flag-row{background:#0d1426;border-left:4px solid var(--ac,#3b82f6);padding:9px 13px;border-radius:0 8px 8px 0;margin:4px 0;font-size:0.84rem;color:#c8d5ea;}
.flag-row.HIGH{--ac:#ef4444;}.flag-row.MEDIUM{--ac:#f59e0b;}.flag-row.LOW{--ac:#10b981;}
.badge-HIGH{background:#450a0a;color:#f87171;padding:2px 9px;border-radius:20px;font-size:0.7rem;font-weight:700;border:1px solid #7f1d1d;}
.badge-MEDIUM{background:#431407;color:#fb923c;padding:2px 9px;border-radius:20px;font-size:0.7rem;font-weight:700;border:1px solid #7c2d12;}
.badge-LOW{background:#052e16;color:#4ade80;padding:2px 9px;border-radius:20px;font-size:0.7rem;font-weight:700;border:1px solid #14532d;}
.auto-tag{background:#1a2545;color:#60a5fa;border:1px solid #1e3a8a;border-radius:6px;padding:3px 9px;font-size:0.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;}
div[data-testid="stButton"]>button{background:linear-gradient(135deg,#1e3a8a,#4338ca)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:700!important;padding:12px 28px!important;width:100%;transition:opacity .2s;}
div[data-testid="stButton"]>button:hover{opacity:.85!important;}
div[data-testid="stFileUploader"]{background:#0d1426;border:1.5px dashed #152040;border-radius:12px;padding:10px;}
details{background:#0d1426!important;border-radius:12px!important;border:1px solid #152040!important;margin-bottom:8px!important;}
summary{padding:11px 16px!important;color:#7eb8ff!important;font-weight:600!important;}
hr{border-color:#0f1e3d!important;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:20px 0 16px;">
        <div style="font-size:2rem;">🧠</div>
        <div style="font-size:1rem;font-weight:800;color:#e2e8f0;">Quality Intelligence</div>
        <div style="font-size:0.65rem;color:#334155;letter-spacing:.15em;text-transform:uppercase;margin-top:2px;">ENGINE V3.0</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    PAGE = st.radio("nav", ["🏠  Dashboard", "📂  Audit Sheet Analysis",
                             "🚨  Transcript Scanner", "🎯  Agent Scorecards"],
                    label_visibility="collapsed")
    st.divider()
    st.markdown("""<div style="font-size:0.7rem;color:#1e3a5f;padding:6px 4px;line-height:1.9;">
        <div style="color:#334155;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:5px;">Setup</div>
        Create <code style="background:#0f1e3d;padding:1px 5px;border-radius:3px;color:#60a5fa;">.env</code> file with:<br>
        <code style="background:#0f1e3d;padding:2px 6px;border-radius:3px;color:#60a5fa;font-size:0.67rem;">ANTHROPIC_API_KEY=sk-ant-...</code>
    </div>""", unsafe_allow_html=True)

def mcard(data):
    for col, val, ac, lbl in data:
        with col:
            st.markdown(f'<div class="qie-card" style="--ac:{ac};"><div class="v">{val}</div><div class="l">{lbl}</div></div>', unsafe_allow_html=True)

def sec(label, color=""):
    st.markdown(f'<div class="sec {color}">{label}</div>', unsafe_allow_html=True)

def ai_box(content):
    import re
    t = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    t = re.sub(r"##\s+(.*)",  r"<h2>\1</h2>", t)
    t = re.sub(r"###\s+(.*)", r"<h3>\1</h3>", t)
    t = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", t)
    t = t.replace("\n","<br>")
    st.markdown(f'<div class="ai-box">{t}</div>', unsafe_allow_html=True)

def ai_section(full, keyword):
    lines = full.split("\n"); in_s = False; buf = []
    for line in lines:
        if keyword.upper() in line.upper() and line.startswith("#"):
            in_s = True; continue
        if in_s:
            if line.startswith("## ") and keyword.upper() not in line.upper(): break
            buf.append(line)
    content = "\n".join(buf).strip()
    ai_box(content if content else full)

def load_csv(up):
    try:
        return pd.read_csv(up)
    except Exception as e:
        st.error(f"Could not read file: {e}"); return None

def make_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()

# ── PAGE: DASHBOARD ───────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown("""<div style="padding:28px 0 12px;text-align:center;">
        <h1 style="font-size:2.4rem;font-weight:800;color:#e2e8f0;letter-spacing:-.02em;margin-bottom:8px;">Quality Intelligence Engine</h1>
        <p style="font-size:1rem;color:#475569;max-width:560px;margin:0 auto;">
            Upload your audit sheet or call transcripts. The engine does the rest.</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="qie-card" style="--ac:#3b82f6;text-align:left;padding:26px;">
            <div style="font-size:1.8rem;margin-bottom:10px;">📂</div>
            <div style="font-size:1rem;font-weight:700;color:#93c5fd;margin-bottom:8px;">Audit Sheet Analysis</div>
            <div style="font-size:0.83rem;color:#c8d5ea;line-height:2;">
                ✅ Auto-detects file type<br>✅ TNI + Calibration + ATA<br>
                ✅ Charts and trend analysis<br>✅ AI coaching reports<br>✅ Batch agent scorecards</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="qie-card" style="--ac:#ef4444;text-align:left;padding:26px;">
            <div style="font-size:1.8rem;margin-bottom:10px;">🚨</div>
            <div style="font-size:1rem;font-weight:700;color:#fca5a5;margin-bottom:8px;">Transcript Scanner</div>
            <div style="font-size:0.83rem;color:#c8d5ea;line-height:2;">
                ✅ 100+ violation patterns<br>✅ HIGH / MEDIUM / LOW severity<br>
                ✅ Agent risk profiles<br>✅ AI compliance report<br>✅ Download reports</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec("📋 CSV Format Guide")
    t1, t2, t3 = st.tabs(["TNI / Agent Audit", "Calibration", "Audit the Auditor (ATA)"])
    with t1:
        st.caption("Needs: agent name + date + score columns. Column names are auto-detected.")
        st.dataframe(pd.DataFrame({"agent_name":["Akshata","Sunil"],"audit_date":["2025-01-10","2025-01-11"],"greeting":[65,80],"empathy":[60,75],"closing":[70,85]}), use_container_width=True, hide_index=True)
    with t2:
        st.caption("Needs: auditor name + call_id + score columns.")
        st.dataframe(pd.DataFrame({"auditor_name":["QA_Priya","QA_Rahul"],"call_id":["C001","C001"],"greeting":[75,55],"empathy":[80,60]}), use_container_width=True, hide_index=True)
    with t3:
        st.caption("Needs: auditor scores + master_ columns for same parameters.")
        st.dataframe(pd.DataFrame({"auditor_name":["QA_Priya","QA_Rahul"],"greeting":[75,55],"master_greeting":[78,78],"empathy":[80,60],"master_empathy":[82,82]}), use_container_width=True, hide_index=True)

# ── PAGE: AUDIT ANALYSIS ──────────────────────────────────────────────────────
def page_audit_analysis():
    st.markdown("<h2 style='color:#e2e8f0;margin-bottom:2px;'>📂 Audit Sheet Analysis</h2><p style='color:#475569;font-size:0.9rem;'>Upload once — engine auto-detects and runs all analyses</p>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload your audit CSV", type=["csv"], key="audit_up")
    if not uploaded:
        st.info("Upload your audit sheet. The engine auto-detects: TNI, Calibration, or ATA data.")
        return
    raw_df = load_csv(uploaded)
    if raw_df is None: return
    df, file_type, warnings, info = auto_prepare(raw_df)
    type_map = {"tni":("📊 TNI / Agent Audit Data","#3b82f6"),"calibration":("⚖️ Calibration Data","#8b5cf6"),"ata":("🔍 ATA Data","#10b981"),"unknown":("❓ Unknown","#f59e0b")}
    tlabel, tcolor = type_map.get(file_type, ("Unknown","#f59e0b"))
    st.markdown(f"<div style='background:#0d1426;border:1px solid #152040;border-radius:10px;padding:12px 18px;margin:10px 0;'><span class='auto-tag'>AUTO-DETECTED</span> <span style='color:{tcolor};font-weight:700;'>{tlabel}</span> <span style='color:#475569;font-size:0.82rem;'> · {info['rows']:,} rows · {len(info['score_cols'])} parameters</span></div>", unsafe_allow_html=True)
    if warnings:
        with st.expander(f"⚠️ {len(warnings)} data warning(s)"):
            for w in warnings: st.warning(w)
    with st.expander("Preview", expanded=False):
        st.write("Score columns:", ", ".join(info["score_cols"]))
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    if file_type == "unknown":
        st.error("Could not determine file type. Ensure CSV has agent_name, auditor_name, or master_ columns.")
        return

    with st.spinner("Running full analysis pipeline..."):
        tni_summary = cal_summary = ata_summary = None
        if file_type in ("tni","calibration"):
            ok, _ = tni_val(df)
            if ok: tni_summary = build_tni_summary(df)
        if file_type == "calibration":
            ok, _ = cal_val(df)
            if ok: cal_summary = build_calibration_summary(df)
        if file_type == "ata":
            ok, _ = ata_val(df)
            if ok:
                ata_summary = build_ata_summary(df)
                if "agent_name" in df.columns:
                    ok2, _ = tni_val(df)
                    if ok2: tni_summary = build_tni_summary(df)

    st.success("✅ Analysis complete")
    score_cols = info["score_cols"]
    cols4 = st.columns(4)

    if tni_summary:
        mcard([(cols4[0], info.get("agent_count",0),"#3b82f6","Agents"),
               (cols4[1], len(score_cols),"#8b5cf6","Parameters"),
               (cols4[2], len(tni_summary["_weak_df"]),"#f59e0b","Weak Params"),
               (cols4[3], len(tni_summary["_recur_df"]),"#ef4444","Recurring Fails")])
        st.markdown("<br>", unsafe_allow_html=True)
        sec("📊 Parameter Performance")
        cl, cr = st.columns(2)
        with cl: render_chart(score_bar_chart(df,"Average Scores by Parameter"), "bar1")
        with cr: render_chart(agent_league_table_chart(tni_summary["_agent_df"]), "league1")
        tf = trend_line_chart(df, score_cols[:6])
        if tf and tf.data:
            sec("📈 Score Trends Over Time")
            render_chart(tf, "trend1")
        sec("⚠️ Weak Parameters","amber")
        if not tni_summary["_weak_df"].empty:
            st.dataframe(tni_summary["_weak_df"].style.background_gradient(subset=["avg_score"],cmap="RdYlGn"), use_container_width=True, hide_index=True)
        else: st.success("All parameters above threshold.")
        sec("🔁 Recurring Weaknesses","red")
        if not tni_summary["_recur_df"].empty:
            st.dataframe(tni_summary["_recur_df"], use_container_width=True, hide_index=True)
        else: st.success("No recurring weaknesses.")
        with st.expander("👥 Agent Statistics", expanded=False):
            st.dataframe(tni_summary["_agent_df"].style.background_gradient(subset=["overall_avg"],cmap="RdYlGn"), use_container_width=True, hide_index=True)
        sec("🤖 AI Training Analysis","purple")
        if st.button("🚀 Generate AI Training + Coaching Report", key="tni_ai"):
            with st.spinner("Claude analysing..."):
                try:
                    r = analyse_tni(tni_summary); st.session_state["tni_ai_r"] = r
                except Exception as e: st.error(str(e))
        if "tni_ai_r" in st.session_state:
            r = st.session_state["tni_ai_r"]
            with st.expander("📌 Root Cause Analysis", expanded=True): ai_section(r,"ROOT CAUSE")
            with st.expander("🎯 Skill Gap Summary"): ai_section(r,"SKILL GAP")
            with st.expander("📊 Priority Matrix"): ai_section(r,"PRIORITY")
            with st.expander("🎓 Training Recommendations"): ai_section(r,"TRAINING")
            with st.expander("💬 Coaching Script"): ai_section(r,"COACHING")

    if cal_summary:
        sec("⚖️ Calibration Analysis","purple")
        render_chart(variance_heatmap(cal_summary["_variance_df"]), "var1")
        ca, cb = st.columns(2)
        with ca:
            st.markdown('<div class="sec red">🔴 Strict Auditors</div>', unsafe_allow_html=True)
            if not cal_summary["_strict_df"].empty: st.dataframe(cal_summary["_strict_df"], use_container_width=True, hide_index=True)
            else: st.success("None detected.")
        with cb:
            st.markdown('<div class="sec green">🟢 Lenient Auditors</div>', unsafe_allow_html=True)
            if not cal_summary["_lenient_df"].empty: st.dataframe(cal_summary["_lenient_df"], use_container_width=True, hide_index=True)
            else: st.success("None detected.")
        sec("🤖 AI Calibration Report","purple")
        if st.button("🚀 Generate AI Calibration Analysis", key="cal_ai"):
            with st.spinner("Claude analysing..."):
                try:
                    r = analyse_calibration(cal_summary); st.session_state["cal_ai_r"] = r
                except Exception as e: st.error(str(e))
        if "cal_ai_r" in st.session_state:
            r = st.session_state["cal_ai_r"]
            with st.expander("📊 Calibration Summary", expanded=True): ai_section(r,"CALIBRATION SUMMARY")
            with st.expander("🎯 Auditor Bias Analysis"): ai_section(r,"AUDITOR BIAS")
            with st.expander("📝 Guideline Improvements"): ai_section(r,"GUIDELINE")
            with st.expander("📧 Executive Summary"): ai_section(r,"EXECUTIVE")

    if ata_summary:
        sec("🔍 Audit the Auditor","green")
        render_chart(auditor_accuracy_chart(ata_summary["_accuracy_df"]), "acc1")
        if not ata_summary["_missed_df"].empty:
            sec("🚨 Missed Flags","red")
            st.dataframe(ata_summary["_missed_df"], use_container_width=True, hide_index=True)
        sec("🤖 AI ATA Report","purple")
        if st.button("🚀 Generate AI ATA Analysis", key="ata_ai"):
            with st.spinner("Claude analysing..."):
                try:
                    r = analyse_ata(ata_summary); st.session_state["ata_ai_r"] = r
                except Exception as e: st.error(str(e))
        if "ata_ai_r" in st.session_state:
            r = st.session_state["ata_ai_r"]
            with st.expander("Overall ATA Verdict", expanded=True): ai_section(r,"OVERALL ATA")
            with st.expander("Auditor Performance Ranking"): ai_section(r,"AUDITOR PERFORMANCE")
            with st.expander("Corrective Action Plan"): ai_section(r,"CORRECTIVE")

    if tni_summary: st.session_state["audit_df"] = df

# ── PAGE: TRANSCRIPT SCANNER ──────────────────────────────────────────────────
def page_transcripts():
    st.markdown("<h2 style='color:#e2e8f0;margin-bottom:2px;'>🚨 Transcript Scanner</h2><p style='color:#475569;font-size:0.9rem;'>Upload transcripts — auto-detects violations and generates compliance report</p>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("---")
        st.markdown("**⚙️ Custom Rules**")
        rules_txt = st.text_area("FORMAT: SEVERITY: phrase", height=150, placeholder="HIGH: your phrase\nMEDIUM: phrase", key="rf_rules")
    custom = parse_custom_rules(rules_txt) if rules_txt else []
    all_flags = DEFAULT_FLAGS + custom
    uploaded = st.file_uploader("Upload .txt transcript files (multiple allowed)", type=["txt"], accept_multiple_files=True, key="rf_up")
    if not uploaded:
        st.info("Upload one or more .txt transcript files.")
        return
    if st.button("🔍 Scan All Transcripts", key="rf_scan"):
        results = []
        bar = st.progress(0, text="Scanning...")
        for i, f in enumerate(uploaded):
            text = f.read().decode("utf-8", errors="ignore")
            results.append(scan_transcript(f.name, text, all_flags))
            bar.progress((i+1)/len(uploaded), text=f"{i+1}/{len(uploaded)}")
        bar.empty()
        st.session_state["rf_results"] = results
        st.success(f"✅ {len(results)} transcript(s) scanned.")
    if "rf_results" not in st.session_state: return
    results = st.session_state["rf_results"]
    total_f = sum(r["total"] for r in results)
    high_c  = sum(r["high"]   for r in results)
    med_c   = sum(r["medium"] for r in results)
    low_c   = sum(r["low"]    for r in results)
    c1,c2,c3,c4,c5 = st.columns(5)
    mcard([(c1,len(results),"#3b82f6","Transcripts"),(c2,total_f,"#ef4444","Total Flags"),
           (c3,high_c,"#ef4444","HIGH"),(c4,med_c,"#f59e0b","MEDIUM"),(c5,low_c,"#10b981","LOW")])
    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns(2)
    with cl: render_chart(flag_severity_donut(high_c, med_c, low_c), "donut1")
    with cr:
        import plotly.graph_objects as go
        agent_flags = {}
        for r in results:
            a = r["agent"]; agent_flags[a] = agent_flags.get(a,0) + r["total"]
        if agent_flags:
            af_df = pd.DataFrame(list(agent_flags.items()), columns=["agent","flags"]).sort_values("flags").tail(10)
            fig = go.Figure(go.Bar(x=af_df["flags"],y=af_df["agent"],orientation="h",marker_color="#ef4444",text=af_df["flags"],textposition="outside",textfont=dict(color="#c8d5ea")))
            fig.update_layout(paper_bgcolor="#0d1426",plot_bgcolor="#0d1426",font=dict(color="#c8d5ea"),height=300,title=dict(text="Top Flagged Agents",font=dict(color="#c8d5ea",size=13)),margin=dict(l=20,r=20,t=40,b=20),xaxis=dict(gridcolor="#152040"),yaxis=dict(gridcolor="#152040"))
            render_chart(fig, "agents_bar")
    sec("🔍 Violation Details")
    fa, fb = st.columns([3,1])
    with fa: search = st.text_input("Search agent or filename","")
    with fb: sev_f = st.selectbox("Severity",["All","HIGH","MEDIUM","LOW"])
    flagged = sorted([r for r in results if r["total"]>0], key=lambda x:(-x["high"],-x["medium"]))
    for r in flagged:
        flags = r["flags"]
        if search and search.lower() not in r["agent"].lower() and search.lower() not in r["filename"].lower(): continue
        if sev_f != "All":
            flags = [f for f in flags if f["severity"]==sev_f]
            if not flags: continue
        h=sum(1 for f in flags if f["severity"]=="HIGH"); m=sum(1 for f in flags if f["severity"]=="MEDIUM"); l=sum(1 for f in flags if f["severity"]=="LOW")
        with st.expander(f"🚨 {r['agent']}  |  {r['filename']}  |  🔴{h}  🟠{m}  🟡{l}"):
            for f in flags:
                s=f["severity"]; ctx=f["context"][:120].replace("**","")
                st.markdown(f'<div class="flag-row {s}"><span class="badge-{s}">{s}</span>&nbsp;<strong>{f["keyword"]}</strong> — {ctx}</div>', unsafe_allow_html=True)
    sec("🤖 AI Compliance Report","purple")
    if st.button("🚀 Generate AI Compliance Analysis", key="rf_ai"):
        with st.spinner("Claude reviewing violations..."):
            try:
                rfs = build_redflag_summary(results); r = analyse_red_flags(rfs); st.session_state["rf_ai_r"] = r
            except Exception as e: st.error(str(e))
    if "rf_ai_r" in st.session_state:
        r = st.session_state["rf_ai_r"]
        with st.expander("⚠️ Compliance Risk Assessment", expanded=True): ai_section(r,"COMPLIANCE RISK")
        with st.expander("👤 Agent Risk Profiles"): ai_section(r,"AGENT RISK")
        with st.expander("📋 Immediate Action Plan"): ai_section(r,"IMMEDIATE ACTION")
        with st.expander("🛡️ Prevention Recommendations"): ai_section(r,"PREVENTION")

# ── PAGE: AGENT SCORECARDS ────────────────────────────────────────────────────
def page_scorecards():
    st.markdown("<h2 style='color:#e2e8f0;margin-bottom:2px;'>🎯 Agent Scorecards</h2><p style='color:#475569;font-size:0.9rem;'>Individual AI performance reports + batch download</p>", unsafe_allow_html=True)
    df = st.session_state.get("audit_df", None)
    uploaded = st.file_uploader("Upload audit CSV (or reuse Audit Sheet Analysis data)", type=["csv"], key="sc_up")
    if uploaded:
        raw = load_csv(uploaded)
        if raw is not None:
            df, _, _, _ = auto_prepare(raw)
    if df is None:
        st.info("Upload a CSV or run Audit Sheet Analysis first — data is reused automatically.")
        return
    ok, err = tni_val(df)
    if not ok: st.error(f"CSV issue: {err}"); return
    agents = get_agent_list(df)
    if not agents: st.warning("No agents found."); return
    st.success(f"✅ {len(agents)} agents found")
    sec("🔍 Individual Agent Deep Dive")
    cs, cb = st.columns([3,1])
    with cs: chosen = st.selectbox("Select Agent", agents, key="sc_sel")
    with cb:
        st.markdown("<br>", unsafe_allow_html=True)
        gen = st.button("🎯 Generate Report", key="sc_gen")
    if gen:
        with st.spinner(f"Building scorecard for {chosen}..."):
            p = build_agent_profile(df, chosen)
            try:
                ai_rep = generate_agent_scorecard({"name":p["name"],"total_audits":p["total_audits"],"overall_avg":p["overall_avg"],"param_scores":p["param_scores"],"strengths":p["strengths"],"weaknesses":p["weaknesses"],"trend":p["trend"],"red_flags":0})
                p["ai_report"] = ai_rep
            except Exception as e:
                st.warning(f"AI unavailable: {e}"); p["ai_report"] = ""
            st.session_state["sc_profile"] = p
    if "sc_profile" in st.session_state:
        p = st.session_state["sc_profile"]
        if p.get("name") == chosen:
            rc = {"Exceeds Expectations":"#10b981","Meets Expectations":"#3b82f6","Needs Improvement":"#f59e0b"}.get(p["rating"],"#ef4444")
            st.markdown(f"<div style='background:linear-gradient(135deg,#0d1426,#111c38);border:1px solid #152040;border-radius:16px;padding:22px;margin:10px 0;display:flex;align-items:center;gap:20px;'><div style='text-align:center;min-width:90px;'><div style='font-size:2.6rem;font-weight:800;color:{rc};'>{p['overall_avg']}</div><div style='font-size:0.65rem;color:#475569;text-transform:uppercase;'>Score</div></div><div><div style='font-size:1.1rem;font-weight:700;color:#e2e8f0;'>{p['name']}</div><div style='color:{rc};font-weight:600;margin:4px 0;'>{p['rating']}</div><div style='font-size:0.78rem;color:#475569;'>Audits: {p['total_audits']}  |  Trend: {p['trend']}</div></div></div>", unsafe_allow_html=True)
            cl, cr = st.columns(2)
            with cl: render_chart(agent_radar_chart(p["param_avgs"], p["name"]), "radar1")
            with cr:
                st.markdown('<div class="sec green">💪 Strengths</div>', unsafe_allow_html=True)
                st.dataframe(p["strengths_df"], use_container_width=True, hide_index=True)
                st.markdown('<div class="sec red">📉 Dev Areas</div>', unsafe_allow_html=True)
                st.dataframe(p["weaknesses_df"], use_container_width=True, hide_index=True)
            if p.get("ai_report"):
                sec("🤖 AI Coaching Plan","purple")
                r = p["ai_report"]
                with st.expander("📋 Performance Summary", expanded=True): ai_section(r,"PERFORMANCE SUMMARY")
                with st.expander("💪 Strengths"): ai_section(r,"STRENGTHS")
                with st.expander("📉 Development Areas"): ai_section(r,"DEVELOPMENT")
                with st.expander("🗓️ 4-Week Coaching Plan"): ai_section(r,"COACHING PLAN")
                with st.expander("🗒️ Manager Notes"): ai_section(r,"MANAGER NOTES")
            try:
                pdf_bytes = generate_scorecard_pdf(p)
                st.download_button(f"⬇️ Download {p['name']} Scorecard PDF", data=pdf_bytes,
                    file_name=f"Scorecard_{p['name'].replace(' ','_')}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e: st.error(f"PDF error: {e}")
    st.markdown("---")
    sec("📦 Batch — All Agent Scorecards")
    st.write(f"Generate PDF scorecards for all **{len(agents)} agents** and download as ZIP.")
    if st.button("📦 Generate All Scorecards (ZIP)", key="sc_batch"):
        files = {}
        bar = st.progress(0)
        for i, agent in enumerate(agents):
            try:
                p2 = build_agent_profile(df, agent)
                files[f"Scorecard_{agent.replace(' ','_')}.pdf"] = generate_scorecard_pdf(p2)
            except: pass
            bar.progress((i+1)/len(agents))
        bar.empty()
        if files:
            zb = make_zip(files)
            st.download_button(f"⬇️ Download All {len(files)} Scorecards (ZIP)", data=zb,
                file_name=f"All_Scorecards_{datetime.today().strftime('%Y%m%d')}.zip",
                mime="application/zip", use_container_width=True)
    sec("👥 Team Overview")
    render_chart(agent_league_table_chart(compute_agent_stats(df)), "league2")

# ── Router ────────────────────────────────────────────────────────────────────
if   PAGE == "🏠  Dashboard":            page_dashboard()
elif PAGE == "📂  Audit Sheet Analysis": page_audit_analysis()
elif PAGE == "🚨  Transcript Scanner":   page_transcripts()
elif PAGE == "🎯  Agent Scorecards":     page_scorecards()
