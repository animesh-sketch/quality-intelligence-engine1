# ============================================================
# app.py  —  Quality Intelligence Engine
# Main Streamlit application. Run with: streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd

from tni_module import (
    validate_csv as tni_validate,
    build_tni_summary,
    compute_weak_parameters,
    compute_recurring_weaknesses,
    compute_trend,
    compute_agent_stats,
)
from calibration_module import (
    validate_csv as cal_validate,
    build_calibration_summary,
    compute_variance,
    detect_auditor_bias,
    compute_disputed_parameters,
)
from ai_engine import analyse_tni, analyse_calibration

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quality Intelligence Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,500;0,700;1,300&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }
  .stApp {
    background: #08090d;
    color: #e8eaf0;
  }
  section[data-testid="stSidebar"] {
    background: #0e1018;
    border-right: 1px solid #1e2235;
  }

  /* ── Metric cards ── */
  .qie-card {
    background: linear-gradient(135deg, #111420 0%, #161b2e 100%);
    border: 1px solid #1f2640;
    border-radius: 14px;
    padding: 20px 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .qie-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: var(--accent, #3b82f6);
  }
  .qie-card .val {
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--accent, #3b82f6);
    line-height: 1;
    margin-bottom: 6px;
  }
  .qie-card .lbl {
    font-size: 0.78rem;
    color: #6b7280;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  /* ── Section headers ── */
  .qie-section {
    background: linear-gradient(90deg, #1a2545 0%, #111420 100%);
    border-left: 4px solid #3b82f6;
    border-radius: 0 10px 10px 0;
    padding: 12px 20px;
    margin: 28px 0 12px;
    font-size: 1rem;
    font-weight: 700;
    color: #93c5fd;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .qie-section.amber { border-left-color: #f59e0b; color: #fcd34d; }
  .qie-section.green { border-left-color: #10b981; color: #6ee7b7; }
  .qie-section.red   { border-left-color: #ef4444; color: #fca5a5; }

  /* ── Severity badges ── */
  .badge-high   { background:#450a0a; color:#f87171; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; border:1px solid #7f1d1d; }
  .badge-medium { background:#431407; color:#fb923c; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; border:1px solid #7c2d12; }
  .badge-low    { background:#052e16; color:#4ade80; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; border:1px solid #14532d; }

  /* ── Dataframe styling ── */
  div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

  /* ── AI Output box ── */
  .ai-output {
    background: #0d1117;
    border: 1px solid #1f2640;
    border-radius: 12px;
    padding: 24px 28px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.92rem;
    line-height: 1.75;
    color: #c9d1e0;
  }
  .ai-output h2 {
    color: #60a5fa;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 22px 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1f2640;
  }
  .ai-output h3 { color: #93c5fd; font-size: 0.95rem; margin: 14px 0 4px; }
  .ai-output table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
  }
  .ai-output table th {
    background: #161d30;
    color: #93c5fd;
    padding: 8px 12px;
    text-align: left;
    font-size: 0.82rem;
    text-transform: uppercase;
  }
  .ai-output table td {
    padding: 8px 12px;
    border-bottom: 1px solid #1a2035;
    font-size: 0.88rem;
  }
  .ai-output ul { padding-left: 18px; }
  .ai-output li { margin-bottom: 5px; }
  .ai-output strong { color: #e2e8f0; }

  /* ── Buttons ── */
  div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1e40af, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    width: 100%;
    transition: opacity 0.2s;
  }
  div[data-testid="stButton"] > button:hover { opacity: 0.88 !important; }

  /* ── File uploader ── */
  div[data-testid="stFileUploader"] {
    background: #111420;
    border: 1.5px dashed #1f2640;
    border-radius: 12px;
    padding: 12px;
  }

  /* ── Expander ── */
  details { background: #111420 !important; border-radius: 10px !important; border: 1px solid #1f2640 !important; margin-bottom: 8px !important; }
  summary { padding: 12px 16px !important; color: #93c5fd !important; font-weight: 600 !important; }

  /* ── Divider ── */
  hr { border-color: #1a2035 !important; }

  /* ── Nav items in sidebar ── */
  .nav-item {
    padding: 10px 16px;
    border-radius: 10px;
    margin: 4px 0;
    cursor: pointer;
    transition: background 0.15s;
    color: #9ca3af;
    font-weight: 500;
  }
  .nav-item.active {
    background: #1a2545;
    color: #60a5fa;
    border-left: 3px solid #3b82f6;
  }
</style>
""", unsafe_allow_html=True)


# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 24px;">
        <div style="font-size:2rem;">🧠</div>
        <div style="font-size:1.1rem; font-weight:700; color:#e8eaf0; margin-top:6px;">Quality Intelligence</div>
        <div style="font-size:0.75rem; color:#4b5563; margin-top:2px; letter-spacing:0.08em;">ENGINE v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    nav = st.radio(
        "Navigation",
        ["🏠  Home", "📊  TNI Analysis", "⚖️  Calibration Analysis"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("""
    <div style="font-size:0.75rem; color:#374151; padding: 10px 4px;">
        <div style="color:#4b5563; font-weight:600; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.08em;">Setup</div>
        Add <code style="background:#1f2937;padding:2px 6px;border-radius:4px;">ANTHROPIC_API_KEY</code> 
        to a <code style="background:#1f2937;padding:2px 6px;border-radius:4px;">.env</code> file in the project folder.
    </div>
    """, unsafe_allow_html=True)


# ── Page: Home ────────────────────────────────────────────────────────────────
def page_home():
    st.markdown("""
    <div style="padding: 40px 0 20px; text-align:center;">
        <h1 style="font-size:2.6rem; font-weight:700; color:#e8eaf0; margin-bottom:10px;">
            Quality Intelligence Engine
        </h1>
        <p style="font-size:1.1rem; color:#6b7280; max-width:600px; margin:0 auto;">
            AI-powered QA analytics for call centre operations.<br>
            Detect training gaps. Fix calibration drift. Act on insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="qie-card" style="--accent:#3b82f6; text-align:left; padding:28px;">
            <div style="font-size:2rem; margin-bottom:12px;">📊</div>
            <div style="font-size:1.1rem; font-weight:700; color:#93c5fd; margin-bottom:8px;">TNI Analysis</div>
            <div style="font-size:0.88rem; color:#6b7280; line-height:1.6;">
                Upload agent audit scores. The engine detects weak parameters,
                recurring skill gaps, score trends, and delivers Claude-powered
                training recommendations with ready-to-use coaching scripts.
            </div>
            <div style="margin-top:16px; font-size:0.8rem; color:#374151;">
                📁 Input: CSV with agent scores<br>
                📤 Output: Training plan + coaching script
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="qie-card" style="--accent:#8b5cf6; text-align:left; padding:28px;">
            <div style="font-size:2rem; margin-bottom:12px;">⚖️</div>
            <div style="font-size:1.1rem; font-weight:700; color:#c4b5fd; margin-bottom:8px;">Calibration Analysis</div>
            <div style="font-size:0.88rem; color:#6b7280; line-height:1.6;">
                Upload auditor scoring data. The engine detects inter-rater variance,
                identifies strict and lenient auditors, flags disputed parameters,
                and generates guideline improvement suggestions.
            </div>
            <div style="margin-top:16px; font-size:0.8rem; color:#374151;">
                📁 Input: CSV with auditor scores<br>
                📤 Output: Calibration report + exec summary
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="qie-section">📋 CSV Format Guide</div>', unsafe_allow_html=True)

    col_t, col_c = st.columns(2)
    with col_t:
        st.markdown("**TNI CSV — Required columns:**")
        tni_eg = pd.DataFrame({
            "agent_name":  ["Akshata", "Sunil", "Ankit"],
            "audit_date":  ["2025-01-10", "2025-01-11", "2025-01-12"],
            "greeting":    [65, 80, 55],
            "empathy":     [60, 75, 50],
            "closing":     [70, 85, 65],
            "product_knowledge": [55, 90, 45],
        })
        st.dataframe(tni_eg, use_container_width=True, hide_index=True)
        st.caption("Add as many score columns as you like. Scores should be 0–100.")

    with col_c:
        st.markdown("**Calibration CSV — Required columns:**")
        cal_eg = pd.DataFrame({
            "auditor_name": ["QA_Priya", "QA_Rahul", "QA_Meena"],
            "agent_name":   ["Akshata", "Akshata", "Akshata"],
            "call_id":      ["C001", "C001", "C001"],
            "greeting":     [75, 55, 80],
            "empathy":      [80, 60, 85],
            "closing":      [70, 50, 75],
        })
        st.dataframe(cal_eg, use_container_width=True, hide_index=True)
        st.caption("Same call_id for multiple auditors enables precise disagreement detection.")


# ── Page: TNI Analysis ────────────────────────────────────────────────────────
def page_tni():
    st.markdown("""
    <h2 style="color:#e8eaf0; margin-bottom:4px;">📊 TNI Analysis</h2>
    <p style="color:#6b7280; font-size:0.92rem;">Training Needs Identification — powered by Claude AI</p>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload agent audit CSV",
        type=["csv"],
        key="tni_upload",
        help="CSV must have agent_name, audit_date, and numeric score columns"
    )

    if not uploaded:
        st.info("👆 Upload a CSV to begin TNI analysis.")
        return

    # Load & validate
    try:
        df = pd.read_csv(uploaded)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        return

    ok, err = tni_validate(df)
    if not ok:
        st.error(f"❌ CSV validation failed: {err}")
        return

    st.success(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")

    with st.expander("🔍 Preview raw data", expanded=False):
        st.dataframe(df.head(20), use_container_width=True, hide_index=True)

    # ── Run stats ──────────────────────────────────────────────────────────────
    summary   = build_tni_summary(df)
    weak_df   = summary["_weak_df"]
    recur_df  = summary["_recur_df"]
    trend_df  = summary["_trend_df"]
    agent_df  = summary["_agent_df"]

    # KPI cards
    from tni_module import _get_score_columns, SCORE_THRESHOLD
    score_cols  = _get_score_columns(df)
    n_weak      = len(weak_df)
    n_recurring = len(recur_df)
    n_agents    = df["agent_name"].nunique()
    lowest_avg  = round(weak_df["avg_score"].min(), 1) if not weak_df.empty else "—"

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, str(n_agents),    "#3b82f6", "Agents Analysed"),
        (c2, str(len(score_cols)), "#8b5cf6", "Parameters"),
        (c3, str(n_weak),      "#f59e0b", "Weak Parameters"),
        (c4, str(n_recurring), "#ef4444", "Recurring Failures"),
    ]
    for col, val, accent, label in cards:
        with col:
            st.markdown(f"""
            <div class="qie-card" style="--accent:{accent};">
                <div class="val">{val}</div>
                <div class="lbl">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Weak parameters ────────────────────────────────────────────────────────
    st.markdown('<div class="qie-section amber">⚠️ Weak Parameters (Score &lt; 70)</div>', unsafe_allow_html=True)
    if weak_df.empty:
        st.success("All parameters are above the threshold. No weak areas detected.")
    else:
        st.dataframe(
            weak_df.style.background_gradient(subset=["avg_score"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True
        )

    # ── Recurring weaknesses ───────────────────────────────────────────────────
    st.markdown('<div class="qie-section red">🔁 Recurring Weaknesses (3+ failures per agent)</div>', unsafe_allow_html=True)
    if recur_df.empty:
        st.success("No agent has failed the same parameter 3 or more times.")
    else:
        st.dataframe(recur_df, use_container_width=True, hide_index=True)

    # ── Trend ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="qie-section">📈 Score Trends Over Time</div>', unsafe_allow_html=True)
    if trend_df.empty:
        st.info("Need at least 2 audit dates to compute trends.")
    else:
        st.dataframe(trend_df, use_container_width=True, hide_index=True)

    # ── Agent stats ────────────────────────────────────────────────────────────
    with st.expander("👥 Agent-Level Statistics", expanded=False):
        st.dataframe(
            agent_df.style.background_gradient(subset=["overall_avg"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True
        )

    # ── Claude AI Analysis ─────────────────────────────────────────────────────
    st.markdown('<div class="qie-section">🤖 Claude AI — TNI Intelligence Report</div>', unsafe_allow_html=True)

    if st.button("🚀 Generate AI Training Analysis", key="tni_ai_btn"):
        with st.spinner("Claude is analysing your data… this takes 15–30 seconds"):
            try:
                ai_result = analyse_tni(summary)
                st.session_state["tni_ai_result"] = ai_result
            except Exception as e:
                st.error(f"AI Error: {e}")

    if "tni_ai_result" in st.session_state:
        with st.expander("📋 Root Cause Analysis", expanded=True):
            _render_ai_section(st.session_state["tni_ai_result"], "ROOT CAUSE")
        with st.expander("🎯 Skill Gap Summary", expanded=False):
            _render_ai_section(st.session_state["tni_ai_result"], "SKILL GAP")
        with st.expander("📌 Priority Matrix", expanded=False):
            _render_ai_section(st.session_state["tni_ai_result"], "PRIORITY")
        with st.expander("🎓 Training Recommendations", expanded=False):
            _render_ai_section(st.session_state["tni_ai_result"], "TRAINING")
        with st.expander("💬 Coaching Script", expanded=False):
            _render_ai_section(st.session_state["tni_ai_result"], "COACHING")

        # Full raw output
        with st.expander("📄 Full AI Report (raw)", expanded=False):
            st.markdown(
                f'<div class="ai-output">{_md_to_html(st.session_state["tni_ai_result"])}</div>',
                unsafe_allow_html=True
            )


# ── Page: Calibration Analysis ────────────────────────────────────────────────
def page_calibration():
    st.markdown("""
    <h2 style="color:#e8eaf0; margin-bottom:4px;">⚖️ Calibration Analysis</h2>
    <p style="color:#6b7280; font-size:0.92rem;">Inter-rater reliability — powered by Claude AI</p>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload auditor scoring CSV",
        type=["csv"],
        key="cal_upload",
        help="CSV must have auditor_name and numeric score columns"
    )

    if not uploaded:
        st.info("👆 Upload a CSV to begin Calibration analysis.")
        return

    try:
        df = pd.read_csv(uploaded)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        return

    ok, err = cal_validate(df)
    if not ok:
        st.error(f"❌ CSV validation failed: {err}")
        return

    st.success(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")

    with st.expander("🔍 Preview raw data", expanded=False):
        st.dataframe(df.head(20), use_container_width=True, hide_index=True)

    # ── Compute stats ─────────────────────────────────────────────────────────
    summary        = build_calibration_summary(df)
    variance_df    = summary["_variance_df"]
    strict_df      = summary["_strict_df"]
    lenient_df     = summary["_lenient_df"]
    disputed_df    = summary["_disputed_df"]
    auditor_df     = summary["_auditor_df"]
    overall_score  = summary["overall_score"]

    flagged_count  = variance_df["flagged"].sum()
    n_strict       = len(strict_df)
    n_lenient      = len(lenient_df)
    n_auditors     = df["auditor_name"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, str(n_auditors),   "#3b82f6", "Auditors"),
        (c2, str(int(flagged_count)), "#f59e0b", "High Variance Params"),
        (c3, str(n_strict),     "#ef4444", "Strict Auditors"),
        (c4, str(n_lenient),    "#10b981", "Lenient Auditors"),
    ]
    for col, val, accent, label in cards:
        with col:
            st.markdown(f"""
            <div class="qie-card" style="--accent:{accent};">
                <div class="val">{val}</div>
                <div class="lbl">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Calibration health
    st.markdown(f"""
    <div style="background:#111420; border:1px solid #1f2640; border-radius:10px;
                padding:14px 20px; margin-bottom:16px; font-size:0.92rem; color:#c9d1e0;">
        <strong style="color:#60a5fa;">Calibration Health:</strong> {overall_score}
    </div>
    """, unsafe_allow_html=True)

    # ── Variance table ────────────────────────────────────────────────────────
    st.markdown('<div class="qie-section amber">📉 Parameter Variance Analysis</div>', unsafe_allow_html=True)
    display_var = variance_df.copy()
    display_var["flagged"] = display_var["flagged"].map({True: "⚠️ Flagged", False: "✅ OK"})
    st.dataframe(
        display_var.style.background_gradient(subset=["variance_%"], cmap="RdYlGn_r"),
        use_container_width=True, hide_index=True
    )

    # ── Auditor bias ──────────────────────────────────────────────────────────
    col_s, col_l = st.columns(2)
    with col_s:
        st.markdown('<div class="qie-section red">🔴 Strict Auditors</div>', unsafe_allow_html=True)
        if strict_df.empty:
            st.success("No strict auditors detected.")
        else:
            st.dataframe(strict_df, use_container_width=True, hide_index=True)

    with col_l:
        st.markdown('<div class="qie-section green">🟢 Lenient Auditors</div>', unsafe_allow_html=True)
        if lenient_df.empty:
            st.success("No lenient auditors detected.")
        else:
            st.dataframe(lenient_df, use_container_width=True, hide_index=True)

    # ── Disputed parameters ───────────────────────────────────────────────────
    st.markdown('<div class="qie-section">🔥 Most Disputed Parameters</div>', unsafe_allow_html=True)
    st.dataframe(disputed_df.head(8), use_container_width=True, hide_index=True)

    # ── Auditor stats ─────────────────────────────────────────────────────────
    with st.expander("👁️ Auditor-Level Statistics", expanded=False):
        st.dataframe(auditor_df, use_container_width=True, hide_index=True)

    # ── Claude AI Analysis ─────────────────────────────────────────────────────
    st.markdown('<div class="qie-section">🤖 Claude AI — Calibration Intelligence Report</div>', unsafe_allow_html=True)

    if st.button("🚀 Generate AI Calibration Analysis", key="cal_ai_btn"):
        with st.spinner("Claude is analysing calibration data… 15–30 seconds"):
            try:
                ai_result = analyse_calibration(summary)
                st.session_state["cal_ai_result"] = ai_result
            except Exception as e:
                st.error(f"AI Error: {e}")

    if "cal_ai_result" in st.session_state:
        with st.expander("📊 Calibration Summary", expanded=True):
            _render_ai_section(st.session_state["cal_ai_result"], "CALIBRATION SUMMARY")
        with st.expander("🎯 Auditor Bias Analysis", expanded=False):
            _render_ai_section(st.session_state["cal_ai_result"], "AUDITOR BIAS")
        with st.expander("⚡ Parameter Disagreement Analysis", expanded=False):
            _render_ai_section(st.session_state["cal_ai_result"], "PARAMETER DISAGREEMENT")
        with st.expander("📝 Guideline Improvement Suggestions", expanded=False):
            _render_ai_section(st.session_state["cal_ai_result"], "GUIDELINE")
        with st.expander("📧 Executive Summary", expanded=False):
            _render_ai_section(st.session_state["cal_ai_result"], "EXECUTIVE")

        with st.expander("📄 Full AI Report (raw)", expanded=False):
            st.markdown(
                f'<div class="ai-output">{_md_to_html(st.session_state["cal_ai_result"])}</div>',
                unsafe_allow_html=True
            )


# ── Helper: render a specific section from AI output ─────────────────────────
def _render_ai_section(full_text: str, section_keyword: str):
    """Extract and render a section from Claude's markdown output."""
    lines     = full_text.split("\n")
    in_section = False
    buffer     = []

    for line in lines:
        if section_keyword.upper() in line.upper() and line.startswith("#"):
            in_section = True
            continue
        if in_section:
            if line.startswith("## ") and section_keyword.upper() not in line.upper():
                break
            buffer.append(line)

    content = "\n".join(buffer).strip()
    if content:
        st.markdown(
            f'<div class="ai-output">{_md_to_html(content)}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="ai-output">{_md_to_html(full_text)}</div>',
            unsafe_allow_html=True
        )


def _md_to_html(text: str) -> str:
    """
    Very lightweight markdown → HTML for the ai-output box.
    Handles bold, headers, and line breaks without heavy dependencies.
    """
    import re
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"##\s+(.*)", r"<h2>\1</h2>", text)
    text = re.sub(r"###\s+(.*)", r"<h3>\1</h3>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    text = text.replace("\n", "<br>")
    return text


# ── Router ────────────────────────────────────────────────────────────────────
if nav == "🏠  Home":
    page_home()
elif nav == "📊  TNI Analysis":
    page_tni()
elif nav == "⚖️  Calibration Analysis":
    page_calibration()
