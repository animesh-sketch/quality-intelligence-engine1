# ============================================================
# app.py  —  Quality Intelligence Engine v2
# Unified platform: TNI + Calibration + Red Flag + Scorecard
# Run with: streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd

from tni_module         import validate_csv as tni_val, build_tni_summary
from calibration_module import validate_csv as cal_val, build_calibration_summary
from redflag_module     import (DEFAULT_FLAGS, parse_custom_rules,
                                scan_transcript, build_redflag_summary)
from scorecard_module   import (get_agent_list, build_agent_profile,
                                generate_scorecard_pdf)
from ata_module         import validate_csv as ata_val, build_ata_summary
from ai_engine          import (analyse_tni, analyse_calibration,
                                analyse_red_flags, generate_agent_scorecard, analyse_ata)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quality Intelligence Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: #070b14; color: #dde3f0; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #060a16 100%);
    border-right: 1px solid #0f1e3d;
}

/* Cards */
.qie-card {
    background: linear-gradient(135deg, #0d1426 0%, #111c38 100%);
    border: 1px solid #152040;
    border-radius: 16px; padding: 22px 26px;
    text-align: center; position: relative; overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.qie-card:hover { transform: translateY(-2px); border-color: var(--ac, #3b82f6); }
.qie-card::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--ac, #3b82f6);
}
.qie-card .v { font-size: 2.6rem; font-weight: 800;
    color: var(--ac, #3b82f6); line-height: 1; margin-bottom: 6px; }
.qie-card .l { font-size: 0.72rem; color: #475569;
    letter-spacing: 0.1em; text-transform: uppercase; font-weight: 600; }

/* Section header */
.sec {
    background: linear-gradient(90deg, #0f1e40 0%, #070b14 100%);
    border-left: 3px solid var(--ac, #3b82f6);
    border-radius: 0 10px 10px 0;
    padding: 11px 18px; margin: 26px 0 10px;
    font-size: 0.82rem; font-weight: 700; color: #7eb8ff;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.sec.amber { --ac: #f59e0b; border-left-color: #f59e0b; color: #fcd34d; }
.sec.red   { --ac: #ef4444; border-left-color: #ef4444; color: #fca5a5; }
.sec.green { --ac: #10b981; border-left-color: #10b981; color: #6ee7b7; }
.sec.purple{ --ac: #8b5cf6; border-left-color: #8b5cf6; color: #c4b5fd; }

/* AI output */
.ai-box {
    background: #09101f;
    border: 1px solid #152040;
    border-radius: 14px;
    padding: 26px 30px;
    font-size: 0.9rem; line-height: 1.8; color: #c8d5ea;
}
.ai-box h2 {
    color: #60a5fa; font-size: 0.88rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 22px 0 8px; padding-bottom: 6px;
    border-bottom: 1px solid #152040;
}
.ai-box h3 { color: #93c5fd; font-size: 0.9rem; margin: 14px 0 4px; }
.ai-box strong { color: #e2e8f0; }
.ai-box ul { padding-left: 20px; }
.ai-box li { margin-bottom: 5px; }
.ai-box table { width:100%; border-collapse:collapse; margin:10px 0; }
.ai-box table th { background:#0f1e3d; color:#93c5fd; padding:8px 12px;
    text-align:left; font-size:0.8rem; text-transform:uppercase; }
.ai-box table td { padding:7px 12px; border-bottom:1px solid #152040; font-size:0.87rem; }

/* Flag rows */
.flag-row { background:#0d1426; border-left:4px solid var(--ac,#3b82f6);
    padding:10px 14px; border-radius:0 8px 8px 0; margin:5px 0;
    font-size:0.86rem; color:#c8d5ea; }
.flag-row.HIGH   { --ac: #ef4444; }
.flag-row.MEDIUM { --ac: #f59e0b; }
.flag-row.LOW    { --ac: #10b981; }

.badge-HIGH   { background:#450a0a; color:#f87171; padding:2px 9px; border-radius:20px; font-size:0.72rem; font-weight:700; border:1px solid #7f1d1d; }
.badge-MEDIUM { background:#431407; color:#fb923c; padding:2px 9px; border-radius:20px; font-size:0.72rem; font-weight:700; border:1px solid #7c2d12; }
.badge-LOW    { background:#052e16; color:#4ade80; padding:2px 9px; border-radius:20px; font-size:0.72rem; font-weight:700; border:1px solid #14532d; }

/* Buttons */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1e3a8a, #4338ca) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    padding: 12px 28px !important; width: 100%;
    letter-spacing: 0.03em; transition: opacity 0.2s;
}
div[data-testid="stButton"] > button:hover { opacity: 0.85 !important; }

/* File uploader */
div[data-testid="stFileUploader"] {
    background: #0d1426; border: 1.5px dashed #152040;
    border-radius: 12px; padding: 10px;
}

/* Expander */
details { background: #0d1426 !important; border-radius: 12px !important;
    border: 1px solid #152040 !important; margin-bottom: 8px !important; }
summary { padding: 12px 18px !important; color: #7eb8ff !important; font-weight: 600 !important; }

hr { border-color: #0f1e3d !important; }
div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:24px 0 20px;">
        <div style="font-size:2.2rem;margin-bottom:8px;">🧠</div>
        <div style="font-size:1rem;font-weight:800;color:#e2e8f0;letter-spacing:0.02em;">
            Quality Intelligence
        </div>
        <div style="font-size:0.68rem;color:#334155;letter-spacing:0.15em;
                    text-transform:uppercase;margin-top:3px;">ENGINE v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    PAGE = st.radio(
        "nav",
        ["🏠  Home",
         "📊  TNI Analysis",
         "⚖️  Calibration",
         "🚨  Red Flag Scan",
         "🎯  Agent Scorecard",
         "🔍  Audit the Auditor"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("""
    <div style="font-size:0.72rem;color:#1e3a5f;padding:8px 4px;line-height:1.8;">
        <div style="color:#334155;font-weight:700;letter-spacing:0.1em;
                    text-transform:uppercase;margin-bottom:6px;">Setup</div>
        Create a <code style="background:#0f1e3d;padding:1px 5px;
        border-radius:3px;color:#60a5fa;">.env</code> file:<br>
        <code style="background:#0f1e3d;padding:2px 6px;border-radius:3px;
        color:#60a5fa;font-size:0.68rem;">ANTHROPIC_API_KEY=sk-ant-...</code>
    </div>
    """, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def cards(data):
    """Render metric cards. data = list of (col, value, accent_color, label)"""
    for col, val, ac, lbl in data:
        with col:
            st.markdown(f"""
            <div class="qie-card" style="--ac:{ac};">
                <div class="v">{val}</div>
                <div class="l">{lbl}</div>
            </div>""", unsafe_allow_html=True)


def ai_box(content: str):
    import re
    text = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    text = re.sub(r"##\s+(.*)",  r"<h2>\1</h2>", text)
    text = re.sub(r"###\s+(.*)", r"<h3>\1</h3>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*",     r"<em>\1</em>", text)
    text = text.replace("\n", "<br>")
    st.markdown(f'<div class="ai-box">{text}</div>', unsafe_allow_html=True)


def ai_section(full: str, keyword: str):
    """Extract and display one section from AI output."""
    lines = full.split("\n")
    in_s, buf = False, []
    for line in lines:
        if keyword.upper() in line.upper() and line.startswith("#"):
            in_s = True; continue
        if in_s:
            if line.startswith("## ") and keyword.upper() not in line.upper(): break
            buf.append(line)
    content = "\n".join(buf).strip()
    ai_box(content if content else full)


def load_csv(uploaded) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(uploaded)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown("""
    <div style="padding:36px 0 16px;text-align:center;">
        <h1 style="font-size:2.8rem;font-weight:800;color:#e2e8f0;
                   letter-spacing:-0.02em;margin-bottom:10px;">
            Quality Intelligence Engine
        </h1>
        <p style="font-size:1.05rem;color:#475569;max-width:580px;margin:0 auto;line-height:1.7;">
            AI-powered QA analytics for call centre operations.<br>
            Four modules. One platform. Instant insights.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    modules = [
        ("📊", "TNI Analysis",        "#3b82f6", "#1d4ed8",
         "Upload agent audit scores to detect weak parameters, recurring skill gaps, and score trends. Get AI-generated training plans and ready-to-use coaching scripts.",
         "agent_name, audit_date, + score columns"),
        ("⚖️", "Calibration",          "#8b5cf6", "#6d28d9",
         "Detect inter-rater variance, identify strict/lenient auditors, and flag disputed parameters. Get scoring guideline improvements and executive summaries.",
         "auditor_name, agent_name, call_id, + score columns"),
        ("🚨", "Red Flag Scan",        "#ef4444", "#b91c1c",
         "Upload call transcripts (.txt). The engine scans for 100+ violation patterns and classifies each as HIGH, MEDIUM, or LOW. Download Excel + PDF reports.",
         "Text files (.txt) with 'Agent: Name' line"),
        ("🎯", "Agent Scorecard",      "#10b981", "#047857",
         "Select any agent from your TNI data and generate a personalised performance scorecard with AI coaching plan, downloadable as a professional PDF.",
         "Uses your TNI CSV — no extra upload needed"),
    ]

    c1, c2 = st.columns(2)
    for i, (icon, title, ac, ac2, desc, fmt) in enumerate(modules):
        col = c1 if i % 2 == 0 else c2
        with col:
            st.markdown(f"""
            <div class="qie-card" style="--ac:{ac};text-align:left;padding:26px;margin-bottom:16px;">
                <div style="font-size:1.8rem;margin-bottom:10px;">{icon}</div>
                <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:8px;">{title}</div>
                <div style="font-size:0.85rem;color:#475569;line-height:1.65;margin-bottom:12px;">{desc}</div>
                <div style="font-size:0.75rem;color:#1e3a5f;background:#0a1628;
                            padding:6px 10px;border-radius:6px;font-family:'JetBrains Mono',monospace;">
                    📁 {fmt}
                </div>
            </div>""", unsafe_allow_html=True)

    # Quick start guide
    st.markdown('<div class="sec">⚡ Quick Start</div>', unsafe_allow_html=True)
    steps = [
        ("1", "Create `.env` file", "Add `ANTHROPIC_API_KEY=sk-ant-...` in the project folder"),
        ("2", "Prepare your CSV",   "Use the format shown above for each module"),
        ("3", "Upload & analyse",   "Pick a module from the sidebar and upload your file"),
        ("4", "Generate AI report", "Click the blue button — Claude analyses in ~20 seconds"),
        ("5", "Download reports",   "Export Excel, PDF scorecard, or copy the coaching script"),
    ]
    c1, c2, c3 = st.columns(3)
    cols_cycle = [c1, c2, c3, c1, c2]
    for (num, title, desc), col in zip(steps, cols_cycle):
        with col:
            st.markdown(f"""
            <div style="background:#0d1426;border:1px solid #152040;border-radius:10px;
                        padding:16px 18px;margin-bottom:10px;">
                <div style="font-size:1.4rem;font-weight:800;color:#1e40af;margin-bottom:6px;">{num}</div>
                <div style="font-size:0.88rem;font-weight:700;color:#93c5fd;margin-bottom:4px;">{title}</div>
                <div style="font-size:0.8rem;color:#475569;line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TNI
# ══════════════════════════════════════════════════════════════════════════════
def page_tni():
    st.markdown("""
    <h2 style="color:#e2e8f0;margin-bottom:2px;">📊 TNI Analysis</h2>
    <p style="color:#475569;font-size:0.9rem;">Training Needs Identification — powered by Claude AI</p>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload agent audit CSV", type=["csv"], key="tni_up")
    if not uploaded:
        st.info("Upload a CSV with columns: `agent_name`, `audit_date`, and any numeric score columns.")
        return

    df = load_csv(uploaded)
    if df is None: return

    ok, err = tni_val(df)
    if not ok:
        st.error(f"CSV issue: {err}")
        return

    st.success(f"✅ {len(df):,} rows · {len(df.columns)} columns loaded")

    with st.expander("Preview data", expanded=False):
        st.dataframe(df.head(15), use_container_width=True, hide_index=True)

    # Store for scorecard page reuse
    st.session_state["tni_df"] = df

    summary      = build_tni_summary(df)
    weak_df      = summary["_weak_df"]
    recur_df     = summary["_recur_df"]
    trend_df     = summary["_trend_df"]
    agent_df     = summary["_agent_df"]

    from tni_module import _score_cols
    sc = _score_cols(df)

    c1,c2,c3,c4 = st.columns(4)
    cards([
        (c1, df["agent_name"].nunique(), "#3b82f6", "Agents"),
        (c2, len(sc),                   "#8b5cf6", "Parameters"),
        (c3, len(weak_df),              "#f59e0b", "Weak Params"),
        (c4, len(recur_df),             "#ef4444", "Recurring Fails"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="sec amber">⚠️ Weak Parameters  (avg < 70)</div>', unsafe_allow_html=True)
    if weak_df.empty:
        st.success("All parameters above threshold.")
    else:
        st.dataframe(
            weak_df.style.background_gradient(subset=["avg_score"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True
        )

    st.markdown('<div class="sec red">🔁 Recurring Weaknesses  (3+ failures per agent)</div>', unsafe_allow_html=True)
    if recur_df.empty:
        st.success("No recurring weaknesses found.")
    else:
        st.dataframe(recur_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="sec">📈 Score Trend</div>', unsafe_allow_html=True)
    if trend_df.empty:
        st.info("Need 2+ audit dates to compute trend.")
    else:
        st.dataframe(trend_df, use_container_width=True, hide_index=True)

    with st.expander("👥 Agent Statistics", expanded=False):
        st.dataframe(
            agent_df.style.background_gradient(subset=["overall_avg"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True
        )

    st.markdown('<div class="sec purple">🤖 Claude AI — TNI Report</div>', unsafe_allow_html=True)
    if st.button("🚀 Generate AI Training Analysis", key="tni_btn"):
        with st.spinner("Claude is analysing training data…  ~20 seconds"):
            try:
                result = analyse_tni(summary)
                st.session_state["tni_ai"] = result
            except Exception as e:
                st.error(str(e))

    if "tni_ai" in st.session_state:
        r = st.session_state["tni_ai"]
        with st.expander("📌 Root Cause Analysis",        expanded=True):  ai_section(r, "ROOT CAUSE")
        with st.expander("🎯 Skill Gap Summary",           expanded=False): ai_section(r, "SKILL GAP")
        with st.expander("📊 Priority Matrix",             expanded=False): ai_section(r, "PRIORITY")
        with st.expander("🎓 Training Recommendations",    expanded=False): ai_section(r, "TRAINING")
        with st.expander("💬 Coaching Script",             expanded=False): ai_section(r, "COACHING")
        with st.expander("📄 Full Report",                 expanded=False): ai_box(r)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CALIBRATION
# ══════════════════════════════════════════════════════════════════════════════
def page_calibration():
    st.markdown("""
    <h2 style="color:#e2e8f0;margin-bottom:2px;">⚖️ Calibration Analysis</h2>
    <p style="color:#475569;font-size:0.9rem;">Inter-rater reliability — powered by Claude AI</p>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload auditor scoring CSV", type=["csv"], key="cal_up")
    if not uploaded:
        st.info("Upload a CSV with columns: `auditor_name`, `call_id` (optional), and score columns.")
        return

    df = load_csv(uploaded)
    if df is None: return

    ok, err = cal_val(df)
    if not ok:
        st.error(f"CSV issue: {err}")
        return

    st.success(f"✅ {len(df):,} rows · {len(df.columns)} columns loaded")

    with st.expander("Preview data", expanded=False):
        st.dataframe(df.head(15), use_container_width=True, hide_index=True)

    summary   = build_calibration_summary(df)
    var_df    = summary["_variance_df"]
    strict_df = summary["_strict_df"]
    leni_df   = summary["_lenient_df"]
    disp_df   = summary["_disputed_df"]
    aud_df    = summary["_auditor_df"]

    c1,c2,c3,c4 = st.columns(4)
    cards([
        (c1, df["auditor_name"].nunique(),         "#3b82f6", "Auditors"),
        (c2, int(var_df["flagged"].sum()),          "#f59e0b", "High Variance"),
        (c3, len(strict_df),                        "#ef4444", "Strict Auditors"),
        (c4, len(leni_df),                          "#10b981", "Lenient Auditors"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#0d1426;border:1px solid #152040;border-radius:10px;
                padding:12px 18px;margin-bottom:16px;font-size:0.88rem;color:#c8d5ea;">
        <strong style="color:#60a5fa;">Calibration Health:</strong>  {summary['overall_score']}
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec amber">📉 Parameter Variance</div>', unsafe_allow_html=True)
    display = var_df.copy()
    display["flagged"] = display["flagged"].map({True: "⚠️ Flagged", False: "✅ OK"})
    st.dataframe(
        display.style.background_gradient(subset=["variance_%"], cmap="RdYlGn_r"),
        use_container_width=True, hide_index=True
    )

    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div class="sec red">🔴 Strict Auditors</div>', unsafe_allow_html=True)
        st.dataframe(strict_df, use_container_width=True, hide_index=True) \
            if not strict_df.empty else st.success("None detected.")
    with cb:
        st.markdown('<div class="sec green">🟢 Lenient Auditors</div>', unsafe_allow_html=True)
        st.dataframe(leni_df, use_container_width=True, hide_index=True) \
            if not leni_df.empty else st.success("None detected.")

    st.markdown('<div class="sec">🔥 Most Disputed Parameters</div>', unsafe_allow_html=True)
    st.dataframe(disp_df.head(8), use_container_width=True, hide_index=True)

    with st.expander("👁️ Auditor Statistics", expanded=False):
        st.dataframe(aud_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="sec purple">🤖 Claude AI — Calibration Report</div>', unsafe_allow_html=True)
    if st.button("🚀 Generate AI Calibration Analysis", key="cal_btn"):
        with st.spinner("Claude is analysing calibration data…  ~20 seconds"):
            try:
                result = analyse_calibration(summary)
                st.session_state["cal_ai"] = result
            except Exception as e:
                st.error(str(e))

    if "cal_ai" in st.session_state:
        r = st.session_state["cal_ai"]
        with st.expander("📊 Calibration Summary",          expanded=True):  ai_section(r, "CALIBRATION SUMMARY")
        with st.expander("🎯 Auditor Bias Analysis",         expanded=False): ai_section(r, "AUDITOR BIAS")
        with st.expander("⚡ Parameter Disagreement",         expanded=False): ai_section(r, "PARAMETER DISAGREEMENT")
        with st.expander("📝 Guideline Improvements",         expanded=False): ai_section(r, "GUIDELINE")
        with st.expander("📧 Executive Summary",              expanded=False): ai_section(r, "EXECUTIVE")
        with st.expander("📄 Full Report",                   expanded=False): ai_box(r)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RED FLAG
# ══════════════════════════════════════════════════════════════════════════════
def page_redflag():
    st.markdown("""
    <h2 style="color:#e2e8f0;margin-bottom:2px;">🚨 Red Flag Scan</h2>
    <p style="color:#475569;font-size:0.9rem;">Transcript violation detection — powered by Claude AI</p>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("---")
        st.markdown("**⚙️ Custom Rules**")
        rules_txt = st.text_area(
            "Add extra rules (SEVERITY: phrase)",
            height=180,
            placeholder="HIGH: your phrase here\nMEDIUM: another phrase\nLOW: informal word",
            key="rf_rules"
        )

    custom = parse_custom_rules(rules_txt) if rules_txt else []
    all_flags = DEFAULT_FLAGS + custom

    uploaded = st.file_uploader(
        "Upload transcript .txt files (multiple allowed)",
        type=["txt"], accept_multiple_files=True, key="rf_up"
    )
    if not uploaded:
        st.info("Upload one or more `.txt` transcripts. Each file must include `Agent: Name` on a line.")
        return

    run = st.button("🔍 Scan All Transcripts", key="rf_btn_scan")
    if run:
        results = []
        bar = st.progress(0, text="Scanning…")
        for i, f in enumerate(uploaded):
            text = f.read().decode("utf-8", errors="ignore")
            results.append(scan_transcript(f.name, text, all_flags))
            bar.progress((i + 1) / len(uploaded), text=f"{i+1}/{len(uploaded)} scanned")
        bar.empty()
        st.session_state["rf_results"] = results
        st.success(f"✅ {len(results)} transcript(s) scanned.")

    if "rf_results" not in st.session_state:
        return

    results    = st.session_state["rf_results"]
    total_f    = sum(r["total"]  for r in results)
    high_c     = sum(r["high"]   for r in results)
    med_c      = sum(r["medium"] for r in results)
    low_c      = sum(r["low"]    for r in results)
    clean_c    = sum(1 for r in results if r["total"] == 0)

    c1,c2,c3,c4,c5 = st.columns(5)
    cards([
        (c1, len(results), "#3b82f6", "Transcripts"),
        (c2, total_f,      "#ef4444", "Total Flags"),
        (c3, high_c,       "#ef4444", "HIGH"),
        (c4, med_c,        "#f59e0b", "MEDIUM"),
        (c5, low_c,        "#10b981", "LOW"),
    ])

    if clean_c:
        st.info(f"✅ {clean_c} transcript(s) had zero flags.")

    # Filters
    st.markdown('<div class="sec">🔍 Results</div>', unsafe_allow_html=True)
    fa, fb = st.columns([3, 1])
    with fa: search = st.text_input("Search agent or filename", "")
    with fb: sev_f  = st.selectbox("Severity", ["All", "HIGH", "MEDIUM", "LOW"])

    flagged = [r for r in results if r["total"] > 0]
    flagged.sort(key=lambda x: (-x["high"], -x["medium"], -x["low"]))

    for r in flagged:
        flags = r["flags"]
        if search and search.lower() not in r["agent"].lower() and search.lower() not in r["filename"].lower():
            continue
        if sev_f != "All":
            flags = [f for f in flags if f["severity"] == sev_f]
            if not flags: continue

        h = sum(1 for f in flags if f["severity"]=="HIGH")
        m = sum(1 for f in flags if f["severity"]=="MEDIUM")
        l = sum(1 for f in flags if f["severity"]=="LOW")

        with st.expander(f"🚨 {r['agent']}  |  {r['filename']}  |  🔴{h}  🟠{m}  🟡{l}"):
            for f in flags:
                s = f["severity"]
                ctx = f["context"][:120].replace("**", "")
                st.markdown(
                    f'<div class="flag-row {s}">'
                    f'<span class="badge-{s}">{s}</span>&nbsp; '
                    f'<strong>{f["keyword"]}</strong> — {ctx}</div>',
                    unsafe_allow_html=True
                )

    # ── AI Analysis ────────────────────────────────────────────────────────────
    st.markdown('<div class="sec purple">🤖 Claude AI — Compliance Report</div>', unsafe_allow_html=True)
    if st.button("🚀 Generate AI Compliance Analysis", key="rf_ai_btn"):
        with st.spinner("Claude is reviewing violations…  ~20 seconds"):
            try:
                rf_summary = build_redflag_summary(results)
                ai_result  = analyse_red_flags(rf_summary)
                st.session_state["rf_ai"] = ai_result
            except Exception as e:
                st.error(str(e))

    if "rf_ai" in st.session_state:
        r = st.session_state["rf_ai"]
        with st.expander("⚠️ Compliance Risk Assessment", expanded=True):  ai_section(r, "COMPLIANCE RISK")
        with st.expander("👤 Agent Risk Profiles",        expanded=False): ai_section(r, "AGENT RISK")
        with st.expander("🔍 Violation Patterns",         expanded=False): ai_section(r, "VIOLATION PATTERN")
        with st.expander("📋 Immediate Action Plan",      expanded=False): ai_section(r, "IMMEDIATE ACTION")
        with st.expander("🛡️ Prevention Recommendations", expanded=False): ai_section(r, "PREVENTION")
        with st.expander("📄 Full Report",                expanded=False): ai_box(r)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AGENT SCORECARD
# ══════════════════════════════════════════════════════════════════════════════
def page_scorecard():
    st.markdown("""
    <h2 style="color:#e2e8f0;margin-bottom:2px;">🎯 Agent Scorecard</h2>
    <p style="color:#475569;font-size:0.9rem;">Individual agent performance report — downloadable PDF</p>
    """, unsafe_allow_html=True)

    # Accept a fresh CSV or reuse TNI data
    uploaded = st.file_uploader("Upload agent audit CSV (or reuse TNI data if already loaded)", type=["csv"], key="sc_up")

    df = None
    if uploaded:
        df = load_csv(uploaded)
    elif "tni_df" in st.session_state:
        df = st.session_state["tni_df"]
        st.info("Using TNI data already loaded. Upload a new file to switch.")

    if df is None:
        st.info("Upload a CSV or load data from the TNI module first.")
        return

    from tni_module import validate_csv as tv
    ok, err = tv(df)
    if not ok:
        st.error(f"CSV issue: {err}")
        return

    agents = get_agent_list(df)
    if not agents:
        st.warning("No agents found in data.")
        return

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        chosen = st.selectbox("Select Agent", agents)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_btn = st.button("🎯 Generate Scorecard", key="sc_gen")

    if not gen_btn and "sc_profile" not in st.session_state:
        return

    if gen_btn:
        with st.spinner(f"Building scorecard for {chosen}…"):
            profile = build_agent_profile(df, chosen)
            try:
                ai_rep = generate_agent_scorecard({
                    "name":         profile["name"],
                    "total_audits": profile["total_audits"],
                    "overall_avg":  profile["overall_avg"],
                    "param_scores": profile["param_scores"],
                    "strengths":    profile["strengths"],
                    "weaknesses":   profile["weaknesses"],
                    "trend":        profile["trend"],
                    "red_flags":    profile.get("red_flags", 0),
                })
                profile["ai_report"] = ai_rep
            except Exception as e:
                st.warning(f"AI report unavailable: {e}")
                profile["ai_report"] = ""
            st.session_state["sc_profile"] = profile

    if "sc_profile" not in st.session_state:
        return

    p = st.session_state["sc_profile"]
    if p.get("name") != chosen:
        # stale profile from a different agent
        st.info("Click 'Generate Scorecard' to build this agent's report.")
        return

    # ── Display scorecard ──────────────────────────────────────────────────────
    r_color_map = {
        "Exceeds Expectations":              "#10b981",
        "Meets Expectations":                "#3b82f6",
        "Needs Improvement":                 "#f59e0b",
        "Critical -- Immediate Action Required": "#ef4444",
    }
    ac = r_color_map.get(p["rating"], "#3b82f6")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1426,#111c38);
                border:1px solid #152040;border-radius:16px;padding:28px;
                margin-bottom:20px;display:flex;align-items:center;gap:24px;">
        <div style="text-align:center;min-width:110px;">
            <div style="font-size:3rem;font-weight:800;color:{ac};line-height:1;">
                {p['overall_avg']}
            </div>
            <div style="font-size:0.7rem;color:#475569;letter-spacing:0.1em;
                        text-transform:uppercase;margin-top:4px;">Overall Score</div>
        </div>
        <div>
            <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin-bottom:6px;">
                {p['name']}
            </div>
            <div style="font-size:0.9rem;font-weight:600;color:{ac};margin-bottom:8px;">
                {p['rating']}
            </div>
            <div style="font-size:0.82rem;color:#475569;">
                Audits: <strong style="color:#94a3b8;">{p['total_audits']}</strong>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                Trend: <strong style="color:#94a3b8;">{p['trend']}</strong>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div class="sec green">💪 Strengths</div>', unsafe_allow_html=True)
        st.dataframe(p["strengths_df"], use_container_width=True, hide_index=True)
    with cb:
        st.markdown('<div class="sec red">📉 Development Areas</div>', unsafe_allow_html=True)
        st.dataframe(p["weaknesses_df"], use_container_width=True, hide_index=True)

    st.markdown('<div class="sec">📊 All Parameters</div>', unsafe_allow_html=True)
    param_df = p["param_avgs"].reset_index()
    param_df.columns = ["parameter", "score"]
    st.dataframe(
        param_df.style.background_gradient(subset=["score"], cmap="RdYlGn"),
        use_container_width=True, hide_index=True
    )

    if p.get("ai_report"):
        st.markdown('<div class="sec purple">🤖 AI Coaching Plan</div>', unsafe_allow_html=True)
        r = p["ai_report"]
        with st.expander("📋 Performance Summary",     expanded=True):  ai_section(r, "PERFORMANCE SUMMARY")
        with st.expander("💪 Strengths",               expanded=False): ai_section(r, "STRENGTHS")
        with st.expander("📉 Development Areas",       expanded=False): ai_section(r, "DEVELOPMENT")
        with st.expander("🗓️ 4-Week Coaching Plan",    expanded=False): ai_section(r, "COACHING PLAN")
        with st.expander("🗒️ Manager Notes",           expanded=False): ai_section(r, "MANAGER NOTES")

    # ── PDF Download ────────────────────────────────────────────────────────────
    st.markdown('<div class="sec">⬇️ Download</div>', unsafe_allow_html=True)
    try:
        pdf_bytes = generate_scorecard_pdf(p)
        safe_name = p["name"].replace(" ", "_")
        st.download_button(
            label=f"📄 Download Scorecard PDF — {p['name']}",
            data=pdf_bytes,
            file_name=f"Scorecard_{safe_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"PDF generation error: {e}")



# PAGE: AUDIT THE AUDITOR
def page_ata():
    st.markdown(
        "<h2 style='color:#e2e8f0;margin-bottom:2px;'>Audit the Auditor</h2>"
        "<p style='color:#475569;font-size:0.9rem;'>Master auditor accuracy check powered by Claude AI</p>",
        unsafe_allow_html=True
    )

    with st.expander("How to prepare your ATA CSV", expanded=False):
        st.markdown(
            "Your CSV needs: **auditor_name**, **call_id**, score columns (e.g. greeting, empathy), "
            "and master score columns with prefix master_ (e.g. master_greeting, master_empathy)"
        )
        eg = pd.DataFrame({
            "auditor_name":    ["QA_Priya","QA_Rahul","QA_Meena"],
            "call_id":         ["C001","C001","C002"],
            "greeting":        [75, 55, 80],
            "empathy":         [80, 60, 85],
            "master_greeting": [78, 78, 76],
            "master_empathy":  [82, 82, 80],
        })
        st.dataframe(eg, use_container_width=True, hide_index=True)

    uploaded = st.file_uploader("Upload ATA CSV", type=["csv"], key="ata_up")
    if not uploaded:
        st.info("Upload a CSV with auditor scores AND master scores to begin.")
        return

    df = load_csv(uploaded)
    if df is None:
        return

    ok, err = ata_val(df)
    if not ok:
        st.error(f"CSV issue: {err}")
        return

    st.success(f"Loaded {len(df):,} rows")

    summary     = build_ata_summary(df)
    accuracy_df = summary["_accuracy_df"]
    param_df    = summary["_param_gaps_df"]
    missed_df   = summary["_missed_df"]

    avg_acc  = round(accuracy_df["accuracy_%"].mean(), 1) if not accuracy_df.empty else 0
    below    = int((accuracy_df["accuracy_%"] < 85).sum()) if not accuracy_df.empty else 0
    missed_ct = len(missed_df)
    n_aud    = df["auditor_name"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    cards([
        (c1, n_aud,            "#3b82f6", "Auditors Reviewed"),
        (c2, f"{avg_acc}%",    "#10b981" if avg_acc >= 85 else "#ef4444", "Avg Accuracy"),
        (c3, below,            "#f59e0b", "Below Threshold"),
        (c4, missed_ct,        "#ef4444", "Missed Flags"),
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    health = summary["overall_score"]
    col    = "#10b981" if "Excellent" in health else ("#3b82f6" if "Good" in health else "#ef4444")
    st.markdown(
        f"<div style='background:#0d1426;border:1px solid #152040;border-radius:10px;"
        f"padding:12px 18px;margin-bottom:16px;font-size:0.88rem;color:#c8d5ea;'>"
        f"<strong style='color:{col};'>ATA Health:</strong> {health}</div>",
        unsafe_allow_html=True
    )

    st.markdown('<div class="sec">Auditor Accuracy vs Master</div>', unsafe_allow_html=True)
    if not accuracy_df.empty:
        st.dataframe(
            accuracy_df.style.background_gradient(subset=["accuracy_%"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True
        )

    st.markdown('<div class="sec amber">Parameter Gaps</div>', unsafe_allow_html=True)
    if not param_df.empty:
        disp = param_df.copy()
        disp["flagged"] = disp["flagged"].map({True: "Flagged", False: "OK"})
        st.dataframe(
            disp.style.background_gradient(subset=["abs_avg_gap"], cmap="RdYlGn_r"),
            use_container_width=True, hide_index=True
        )

    st.markdown('<div class="sec red">Missed Flags (auditor 15+ pts above master)</div>', unsafe_allow_html=True)
    if not missed_df.empty:
        st.dataframe(missed_df, use_container_width=True, hide_index=True)
    else:
        st.success("No serious missed flags detected.")

    st.markdown('<div class="sec purple">Claude AI - ATA Report</div>', unsafe_allow_html=True)
    if st.button("Generate AI ATA Analysis", key="ata_ai_btn"):
        with st.spinner("Claude is reviewing auditor accuracy..."):
            try:
                ai_result = analyse_ata(summary)
                st.session_state["ata_ai"] = ai_result
            except Exception as e:
                st.error(str(e))

    if "ata_ai" in st.session_state:
        r = st.session_state["ata_ai"]
        with st.expander("Overall ATA Verdict",        expanded=True):  ai_section(r, "OVERALL ATA")
        with st.expander("Auditor Performance Ranking", expanded=False): ai_section(r, "AUDITOR PERFORMANCE")
        with st.expander("Missed Flags Analysis",       expanded=False): ai_section(r, "MISSED FLAGS")
        with st.expander("Parameter Blind Spots",       expanded=False): ai_section(r, "BLIND SPOTS")
        with st.expander("Corrective Action Plan",      expanded=False): ai_section(r, "CORRECTIVE")
        with st.expander("Full Report",                 expanded=False): ai_box(r)


# ── Router ─────────────────────────────────────────────────────────────────────
if   PAGE == "🏠  Home":               page_home()
elif PAGE == "📊  TNI Analysis":        page_tni()
elif PAGE == "⚖️  Calibration":         page_calibration()
elif PAGE == "🚨  Red Flag Scan":       page_redflag()
elif PAGE == "🎯  Agent Scorecard":     page_scorecard()
elif PAGE == "🔍  Audit the Auditor":   page_ata()
