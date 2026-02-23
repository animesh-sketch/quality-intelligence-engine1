# ============================================================
# app.py  —  Quality Intelligence Engine v3
# Upload audit sheet or transcripts — app does everything.
# Run with: streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
import zipfile, io, os
from datetime import datetime

from file_parser     import parse_file, get_file_type_label
from smart_detector  import auto_prepare, get_score_columns
from tni_module      import validate_csv as tni_val, build_tni_summary, compute_agent_stats
from calibration_module import validate_csv as cal_val, build_calibration_summary
from ata_module      import validate_csv as ata_val, build_ata_summary
from redflag_module  import DEFAULT_FLAGS, parse_custom_rules, scan_transcript, build_redflag_summary
from scorecard_module import build_agent_profile, generate_scorecard_pdf, get_agent_list
from voicebot_module import validate_csv as vb_val, build_voicebot_summary
from viz_module      import (score_bar_chart, agent_radar_chart, trend_line_chart,
                              agent_league_table_chart, variance_heatmap,
                              auditor_accuracy_chart, flag_severity_donut, render_chart,
                              voicebot_kpi_gauge, voicebot_intent_chart,
                              voicebot_escalation_chart, voicebot_failure_chart)
from ai_engine       import (analyse_tni, analyse_calibration, analyse_red_flags,
                              analyse_voicebot,
                              generate_agent_scorecard, analyse_ata)

st.set_page_config(page_title="Quality Intelligence Engine", page_icon="🧠",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: #04070f;
}
.stApp {
    background: #04070f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0,245,212,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(247,37,133,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 50% 50%, rgba(114,9,183,0.04) 0%, transparent 70%);
    min-height: 100vh;
    color: #dce8ff;
}

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060c1a 0%, #040810 100%);
    border-right: 1px solid rgba(0,245,212,0.12);
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00f5d4, #7209b7, #f72585);
}

/* ── Sidebar nav pills ─────────────────────────────────────── */
div[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    margin: 3px 0 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #647595 !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
div[data-testid="stRadio"] label:hover {
    background: rgba(0,245,212,0.07) !important;
    color: #00f5d4 !important;
}
div[data-testid="stRadio"] [aria-checked="true"] + label,
div[data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(135deg, rgba(0,245,212,0.12), rgba(114,9,183,0.08)) !important;
    color: #00f5d4 !important;
    border: 1px solid rgba(0,245,212,0.2) !important;
}

/* ── KPI Cards ─────────────────────────────────────────────── */
.qie-card {
    position: relative;
    background: rgba(10,18,40,0.85);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 22px 20px 18px;
    text-align: center;
    overflow: hidden;
    backdrop-filter: blur(10px);
    transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
}
.qie-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    padding: 1px;
    background: linear-gradient(135deg, var(--ac, #00f5d4), transparent 60%);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
    opacity: 0.5;
}
.qie-card::after {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    border-radius: 50%;
    background: radial-gradient(circle, var(--ac, #00f5d4) 0%, transparent 70%);
    opacity: 0.08;
}
.qie-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255,255,255,0.1);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(0,245,212,0.05);
}
.qie-card .v {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--ac, #00f5d4);
    line-height: 1;
    margin-bottom: 6px;
    letter-spacing: -0.03em;
}
.qie-card .l {
    font-size: 0.68rem;
    color: #3d5070;
    letter-spacing: .12em;
    text-transform: uppercase;
    font-weight: 600;
}

/* ── Section Headers ──────────────────────────────────────── */
.sec {
    position: relative;
    margin: 28px 0 12px;
    padding: 0;
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #00f5d4;
}
.sec::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,245,212,0.3), transparent);
}
.sec.amber { color: #ffd60a; }
.sec.amber::after { background: linear-gradient(90deg, rgba(255,214,10,0.3), transparent); }
.sec.red   { color: #f72585; }
.sec.red::after   { background: linear-gradient(90deg, rgba(247,37,133,0.3), transparent); }
.sec.green { color: #06d6a0; }
.sec.green::after { background: linear-gradient(90deg, rgba(6,214,160,0.3), transparent); }
.sec.purple{ color: #b14cf0; }
.sec.purple::after{ background: linear-gradient(90deg, rgba(177,76,240,0.3), transparent); }

/* ── AI Output Box ─────────────────────────────────────────── */
.ai-box {
    background: linear-gradient(135deg, rgba(8,15,35,0.95), rgba(12,20,45,0.9));
    border: 1px solid rgba(0,245,212,0.12);
    border-radius: 18px;
    padding: 26px 30px;
    font-size: 0.88rem;
    line-height: 1.85;
    color: #c4d8ff;
    position: relative;
    overflow: hidden;
}
.ai-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #00f5d4, transparent);
    opacity: 0.5;
}
.ai-box h2 {
    font-family: 'Syne', sans-serif;
    color: #00f5d4;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .12em;
    margin: 22px 0 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0,245,212,0.1);
}
.ai-box h3 { color: #7dd3fc; font-size: 0.9rem; margin: 14px 0 5px; }
.ai-box strong { color: #f0f7ff; }
.ai-box ul { padding-left: 20px; }
.ai-box li { margin-bottom: 5px; }

/* ── Flag Rows ─────────────────────────────────────────────── */
.flag-row {
    background: rgba(10,15,30,0.7);
    border-left: 3px solid var(--ac, #00f5d4);
    padding: 10px 14px;
    border-radius: 0 10px 10px 0;
    margin: 5px 0;
    font-size: 0.83rem;
    color: #c4d8ff;
    backdrop-filter: blur(5px);
    transition: background 0.2s;
}
.flag-row:hover { background: rgba(15,25,50,0.9); }
.flag-row.HIGH   { --ac: #f72585; }
.flag-row.MEDIUM { --ac: #ffd60a; }
.flag-row.LOW    { --ac: #06d6a0; }
.badge-HIGH   { background: rgba(247,37,133,0.15); color: #f9a8d4; padding: 2px 10px; border-radius: 20px; font-size: 0.68rem; font-weight: 700; border: 1px solid rgba(247,37,133,0.3); }
.badge-MEDIUM { background: rgba(255,214,10,0.12); color: #fef08a; padding: 2px 10px; border-radius: 20px; font-size: 0.68rem; font-weight: 700; border: 1px solid rgba(255,214,10,0.3); }
.badge-LOW    { background: rgba(6,214,160,0.12);  color: #6ee7b7; padding: 2px 10px; border-radius: 20px; font-size: 0.68rem; font-weight: 700; border: 1px solid rgba(6,214,160,0.3); }

/* ── Auto-tag ─────────────────────────────────────────────── */
.auto-tag {
    background: linear-gradient(135deg, rgba(0,245,212,0.15), rgba(114,9,183,0.1));
    color: #00f5d4;
    border: 1px solid rgba(0,245,212,0.25);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Feature Cards (Dashboard) ─────────────────────────────── */
.feat-card {
    position: relative;
    border-radius: 24px;
    padding: 32px 28px;
    overflow: hidden;
    transition: transform 0.3s, box-shadow 0.3s;
    cursor: default;
}
.feat-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 30px 60px rgba(0,0,0,0.5);
}
.feat-card .icon { font-size: 2.4rem; margin-bottom: 14px; display: block; }
.feat-card .title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; }
.feat-card .desc  { font-size: 0.83rem; line-height: 1.75; opacity: 0.8; }
.feat-card .list  { font-size: 0.8rem; line-height: 2.1; margin-top: 12px; }

/* ── Buttons ───────────────────────────────────────────────── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #00f5d4 0%, #0891b2 50%, #7209b7 100%) !important;
    color: #04070f !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: .04em !important;
    padding: 13px 28px !important;
    width: 100% !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(0,245,212,0.2) !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    box-shadow: 0 8px 30px rgba(0,245,212,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Download buttons ─────────────────────────────────────── */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, rgba(0,245,212,0.1), rgba(114,9,183,0.1)) !important;
    color: #00f5d4 !important;
    border: 1px solid rgba(0,245,212,0.3) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    width: 100% !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: rgba(0,245,212,0.15) !important;
    border-color: rgba(0,245,212,0.5) !important;
}

/* ── File uploader ─────────────────────────────────────────── */
div[data-testid="stFileUploader"] {
    background: rgba(8,15,35,0.6);
    border: 1.5px dashed rgba(0,245,212,0.2);
    border-radius: 16px;
    padding: 12px;
    transition: border-color 0.2s;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(0,245,212,0.4);
}

/* ── Expanders ─────────────────────────────────────────────── */
details {
    background: rgba(8,15,35,0.7) !important;
    border: 1px solid rgba(0,245,212,0.1) !important;
    border-radius: 14px !important;
    margin-bottom: 8px !important;
    backdrop-filter: blur(5px) !important;
}
summary {
    padding: 13px 18px !important;
    color: #7dd3fc !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}
summary:hover { color: #00f5d4 !important; }

/* ── Tabs ──────────────────────────────────────────────────── */
div[data-testid="stTabs"] button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: #475569 !important;
    border-radius: 8px 8px 0 0 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #00f5d4 !important;
    border-bottom-color: #00f5d4 !important;
}

/* ── DataFrames ─────────────────────────────────────────────── */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,245,212,0.1);
    border-radius: 12px;
    overflow: hidden;
}
.stDataFrame thead tr th {
    background: rgba(0,245,212,0.08) !important;
    color: #00f5d4 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
}

/* ── Alerts ─────────────────────────────────────────────────── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ── Progress bar ───────────────────────────────────────────── */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #00f5d4, #7209b7) !important;
    border-radius: 4px !important;
}
div[data-testid="stProgress"] > div {
    background: rgba(0,245,212,0.1) !important;
    border-radius: 4px !important;
}

hr { border-color: rgba(0,245,212,0.08) !important; }

/* ── Spinner ─────────────────────────────────────────────────── */
div[data-testid="stSpinner"] > div {
    border-color: #00f5d4 !important;
}

/* ── Scrollbar ───────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #04070f; }
::-webkit-scrollbar-thumb { background: rgba(0,245,212,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,245,212,0.5); }

/* ── Success/Info overrides ──────────────────────────────────── */
.stSuccess { background: rgba(6,214,160,0.08) !important; border-left-color: #06d6a0 !important; }
.stInfo    { background: rgba(0,245,212,0.06) !important; border-left-color: #00f5d4 !important; }
.stError   { background: rgba(247,37,133,0.08) !important; border-left-color: #f72585 !important; }
.stWarning { background: rgba(255,214,10,0.08) !important; border-left-color: #ffd60a !important; }

/* ── Select box ──────────────────────────────────────────────── */
div[data-testid="stSelectbox"] > div > div {
    background: rgba(8,15,35,0.8) !important;
    border: 1px solid rgba(0,245,212,0.15) !important;
    border-radius: 10px !important;
    color: #c4d8ff !important;
}

/* ── Text input ──────────────────────────────────────────────── */
div[data-testid="stTextInput"] input {
    background: rgba(8,15,35,0.8) !important;
    border: 1px solid rgba(0,245,212,0.15) !important;
    border-radius: 10px !important;
    color: #c4d8ff !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(0,245,212,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,245,212,0.08) !important;
}

</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:28px 0 20px;">
        <div style="position:relative;display:inline-block;margin-bottom:14px;">
            <div style="width:62px;height:62px;border-radius:18px;
                background:linear-gradient(135deg,#00f5d4,#7209b7);
                display:flex;align-items:center;justify-content:center;
                margin:0 auto;font-size:1.8rem;
                box-shadow:0 8px 24px rgba(0,245,212,0.3);">🧠</div>
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;
            background:linear-gradient(135deg,#00f5d4,#b14cf0);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;letter-spacing:-.01em;">Quality Intelligence</div>
        <div style="font-size:0.6rem;color:#1e3a5f;letter-spacing:.2em;
            text-transform:uppercase;margin-top:3px;font-family:'JetBrains Mono',monospace;">ENGINE V3.0</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    PAGE = st.radio("nav", ["🏠  Dashboard", "📂  Audit Sheet Analysis",
                             "🚨  Transcript Scanner", "🎯  Agent Scorecards",
                             "🤖  Voicebot Audit"],
                    label_visibility="collapsed")
    st.divider()
    st.markdown("""
    <div style="margin:4px 6px;padding:14px 16px;
        background:rgba(0,245,212,0.04);border:1px solid rgba(0,245,212,0.1);
        border-radius:12px;font-size:0.72rem;line-height:1.9;">
        <div style="color:#00f5d4;font-weight:700;letter-spacing:.1em;
            text-transform:uppercase;margin-bottom:7px;font-family:'Syne',sans-serif;font-size:0.65rem;">⚙️ Setup</div>
        <div style="color:#3d5070;">Create <code style="background:rgba(0,245,212,0.1);
            padding:1px 6px;border-radius:4px;color:#00f5d4;font-family:'JetBrains Mono',monospace;">.env</code> file:</div>
        <code style="background:rgba(0,0,0,0.4);padding:4px 8px;border-radius:6px;
            color:#00f5d4;font-size:0.65rem;font-family:'JetBrains Mono',monospace;
            display:block;margin-top:6px;">ANTHROPIC_API_KEY=sk-ant-...</code>
    </div>""", unsafe_allow_html=True)

def mcard(data):
    for col, val, ac, lbl in data:
        with col:
            st.markdown(
                f'<div class="qie-card" style="--ac:{ac};">' +
                f'<div class="v">{val}</div>' +
                f'<div class="l">{lbl}</div>' +
                f'</div>',
                unsafe_allow_html=True
            )

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

def load_file(up) -> pd.DataFrame | None:
    """Universal loader — handles CSV, Excel, PDF, Word, TXT."""
    if up is None:
        return None
    up.seek(0)
    df, ftype, msg = parse_file(up)
    label = get_file_type_label(ftype)
    if df is not None:
        st.markdown(
            f"<div style='background:#0a1a0a;border:1px solid #14532d;border-radius:8px;"
            f"padding:8px 14px;margin:6px 0;font-size:0.82rem;color:#4ade80;'>"
            f"✅ {label} — {msg}</div>",
            unsafe_allow_html=True
        )
    else:
        st.error(f"{label} — {msg}")
    return df

# Keep load_csv as alias for backwards compat
def load_csv(up):
    return load_file(up)

def make_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()

# ── PAGE: DASHBOARD ──────────────────────────────────────────
def page_dashboard():
    # Hero
    st.markdown("""
    <div style="padding:48px 0 32px;text-align:center;position:relative;">
        <div style="position:absolute;top:20px;left:50%;transform:translateX(-50%);
            width:600px;height:300px;
            background:radial-gradient(ellipse,rgba(0,245,212,0.06) 0%,transparent 70%);
            pointer-events:none;"></div>
        <div style="display:inline-block;background:linear-gradient(135deg,rgba(0,245,212,0.1),rgba(114,9,183,0.1));
            border:1px solid rgba(0,245,212,0.2);border-radius:50px;
            padding:5px 16px;font-size:0.7rem;color:#00f5d4;font-weight:700;
            letter-spacing:.12em;text-transform:uppercase;margin-bottom:20px;
            font-family:'JetBrains Mono',monospace;">✦ AI-Powered QA Analytics</div>
        <h1 style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;
            background:linear-gradient(135deg,#ffffff 0%,#00f5d4 40%,#b14cf0 80%,#f72585 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;letter-spacing:-0.03em;line-height:1.1;margin-bottom:16px;">
            Quality Intelligence<br>Engine
        </h1>
        <p style="font-size:1.05rem;color:#4a6080;max-width:480px;margin:0 auto 32px;line-height:1.6;">
            Upload your audit data. The engine detects, analyses,<br>and delivers AI-powered insights instantly.
        </p>
    </div>""", unsafe_allow_html=True)

    # Feature cards
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("""
        <div class="feat-card" style="background:linear-gradient(135deg,rgba(0,245,212,0.08) 0%,rgba(8,145,178,0.06) 50%,rgba(114,9,183,0.08) 100%);
            border:1px solid rgba(0,245,212,0.15);">
            <span class="icon">📂</span>
            <div class="title" style="color:#00f5d4;">Audit Sheet Analysis</div>
            <div class="desc" style="color:#4a6080;">Upload once. Auto-detects your data format and runs all analyses simultaneously.</div>
            <div class="list" style="color:#c4d8ff;">
                ✦ &nbsp;Training Needs Identification<br>
                ✦ &nbsp;Calibration & Inter-rater Analysis<br>
                ✦ &nbsp;Audit the Auditor (ATA)<br>
                ✦ &nbsp;Agent Performance Scorecards<br>
                ✦ &nbsp;AI-generated coaching reports
            </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feat-card" style="background:linear-gradient(135deg,rgba(247,37,133,0.08) 0%,rgba(114,9,183,0.06) 50%,rgba(255,214,10,0.05) 100%);
            border:1px solid rgba(247,37,133,0.15);">
            <span class="icon">🚨</span>
            <div class="title" style="color:#f72585;">Transcript + Voicebot Scanner</div>
            <div class="desc" style="color:#4a6080;">Drop transcripts or voicebot audit dumps — full compliance and performance analysis.</div>
            <div class="list" style="color:#c4d8ff;">
                ✦ &nbsp;100+ violation pattern library<br>
                ✦ &nbsp;HIGH / MEDIUM / LOW severity<br>
                ✦ &nbsp;Voicebot containment & intent audit<br>
                ✦ &nbsp;Agent risk profiles<br>
                ✦ &nbsp;AI compliance + optimisation report
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats row
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:8px 0 32px;">
        <div style="text-align:center;padding:20px;background:rgba(0,245,212,0.04);
            border:1px solid rgba(0,245,212,0.08);border-radius:16px;">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#00f5d4;">6</div>
            <div style="font-size:0.7rem;color:#3d5070;text-transform:uppercase;letter-spacing:.1em;margin-top:4px;">Analysis Modules</div>
        </div>
        <div style="text-align:center;padding:20px;background:rgba(247,37,133,0.04);
            border:1px solid rgba(247,37,133,0.08);border-radius:16px;">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#f72585;">100+</div>
            <div style="font-size:0.7rem;color:#3d5070;text-transform:uppercase;letter-spacing:.1em;margin-top:4px;">Violation Patterns</div>
        </div>
        <div style="text-align:center;padding:20px;background:rgba(177,76,240,0.04);
            border:1px solid rgba(177,76,240,0.08);border-radius:16px;">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#b14cf0;">5</div>
            <div style="font-size:0.7rem;color:#3d5070;text-transform:uppercase;letter-spacing:.1em;margin-top:4px;">File Formats</div>
        </div>
        <div style="text-align:center;padding:20px;background:rgba(255,214,10,0.04);
            border:1px solid rgba(255,214,10,0.08);border-radius:16px;">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#ffd60a;">AI</div>
            <div style="font-size:0.7rem;color:#3d5070;text-transform:uppercase;letter-spacing:.1em;margin-top:4px;">Claude Powered</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Format guide
    st.markdown('<div class="sec">📋 Accepted File Formats & CSV Structure</div>', unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["📊 TNI / Audit", "⚖️ Calibration", "🔍 ATA", "🤖 Voicebot"])
    with t1:
        st.caption("Needs: agent name + date + score columns. Column names auto-detected.")
        st.dataframe(pd.DataFrame({"agent_name":["Akshata","Sunil"],"audit_date":["2025-01-10","2025-01-11"],"greeting":[65,80],"empathy":[60,75],"closing":[70,85]}), use_container_width=True, hide_index=True)
    with t2:
        st.caption("Needs: auditor name + call_id + score columns.")
        st.dataframe(pd.DataFrame({"auditor_name":["QA_Priya","QA_Rahul"],"call_id":["C001","C001"],"greeting":[75,55],"empathy":[80,60]}), use_container_width=True, hide_index=True)
    with t3:
        st.caption("Needs: auditor scores + master_ columns for same parameters.")
        st.dataframe(pd.DataFrame({"auditor_name":["QA_Priya","QA_Rahul"],"greeting":[75,55],"master_greeting":[78,78],"empathy":[80,60],"master_empathy":[82,82]}), use_container_width=True, hide_index=True)
    with t4:
        st.caption("Needs: bot_name + interaction_id + any performance columns.")
        st.dataframe(pd.DataFrame({"bot_name":["SalesBot"],"interaction_id":["I001"],"containment_result":["yes"],"intent_detected":["check_balance"],"intent_expected":["check_balance"],"csat_score":[4.5]}), use_container_width=True, hide_index=True)


# ── PAGE: AUDIT ANALYSIS ──────────────────────────────────────────────────────
def page_audit_analysis():
    st.markdown("<h2 style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#00f5d4,#0891b2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:2px;'>📂 Audit Sheet Analysis</h2><p style='color:#3d5070;font-size:0.88rem;margin-top:0;'>Upload once — engine auto-detects and runs all analyses automatically</p>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload audit file (CSV, Excel, PDF, Word)", type=["csv","xlsx","xls","pdf","docx","txt"], key="audit_up")
    if not uploaded:
        st.info("Upload your audit sheet. The engine auto-detects: TNI, Calibration, or ATA data.")
        return
    raw_df = load_file(uploaded)
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
    st.markdown("<h2 style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#f72585,#ffd60a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:2px;'>🚨 Transcript Scanner</h2><p style='color:#3d5070;font-size:0.88rem;margin-top:0;'>Upload call transcripts — auto-detects violations, generates compliance report</p>", unsafe_allow_html=True)
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
    st.markdown("<h2 style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#b14cf0,#f72585);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:2px;'>🎯 Agent Scorecards</h2><p style='color:#3d5070;font-size:0.88rem;margin-top:0;'>Individual AI-powered performance reports — download as PDF or batch ZIP</p>", unsafe_allow_html=True)
    df = st.session_state.get("audit_df", None)
    uploaded = st.file_uploader("Upload audit file (CSV, Excel, PDF, Word) or reuse Audit Sheet data", type=["csv","xlsx","xls","pdf","docx","txt"], key="sc_up")
    if uploaded:
        raw = load_file(uploaded)
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



# PAGE: VOICEBOT AUDIT
def page_voicebot():
    st.markdown(
        "<h2 style='color:#e2e8f0;margin-bottom:2px;'>🤖 Voicebot Audit</h2>"
        "<p style='color:#475569;font-size:0.9rem;'>Upload your voicebot audit dump — AI analyses containment, intent accuracy, failures and more</p>",
        unsafe_allow_html=True
    )

    with st.expander("📋 How to prepare your Voicebot Audit CSV", expanded=False):
        st.markdown("""
        Your CSV needs at minimum: **bot_name** and **interaction_id**

        Add any columns you have from this list — the engine uses whatever is available:

        | Column | What it means |
        |---|---|
        | `containment_result` | yes/no — did bot resolve without human? |
        | `escalation_reason` | why user was transferred to human |
        | `intent_detected` | what the bot thought user wanted |
        | `intent_expected` | what user actually wanted |
        | `intent_accuracy` | % correct intent (0-100) |
        | `response_accuracy` | % correct responses (0-100) |
        | `fallback_rate` | % of utterances bot couldn't handle |
        | `csat_score` | customer satisfaction (0-5) |
        | `dead_air_rate` | % of call with silence |
        | `avg_handle_time` | average call duration (seconds) |
        | `sentiment` | positive/neutral/negative |
        | Any score column | e.g. greeting_score, resolution_score |
        """)
        eg = pd.DataFrame({
            "bot_name":          ["SalesBot","SalesBot","SupportBot"],
            "interaction_id":    ["I001","I002","I003"],
            "containment_result":["yes","no","yes"],
            "escalation_reason": [None,"Complex query",None],
            "intent_detected":   ["check_balance","apply_loan","reset_password"],
            "intent_expected":   ["check_balance","check_balance","reset_password"],
            "csat_score":        [4.5, 2.0, 4.0],
            "response_accuracy": [92, 55, 88],
        })
        st.dataframe(eg, use_container_width=True, hide_index=True)

    uploaded = st.file_uploader("Upload Voicebot Audit file (CSV, Excel, PDF, Word)", type=["csv","xlsx","xls","pdf","docx","txt"], key="vb_up")
    if not uploaded:
        st.info("Upload your voicebot audit dump CSV to begin.")
        return

    raw_df = load_file(uploaded)
    if raw_df is None:
        return

    # Auto-normalise columns
    raw_df.columns = (raw_df.columns.str.strip().str.lower()
                      .str.replace(r"[\s\-/\\]+", "_", regex=True)
                      .str.replace(r"[^\w]", "", regex=True))

    ok, err = vb_val(raw_df)
    if not ok:
        st.error(f"CSV issue: {err}")
        return

    st.success(f"✅ {len(raw_df):,} interactions loaded")

    with st.expander("Preview data", expanded=False):
        st.dataframe(raw_df.head(10), use_container_width=True, hide_index=True)

    with st.spinner("Analysing voicebot performance..."):
        summary   = build_voicebot_summary(raw_df)
        kpis      = summary["_kpis"]
        intent_df = summary["_intent_df"]
        escal_df  = summary["_escal_df"]
        fail_df   = summary["_failures_df"]
        bot_df    = summary["_bot_perf_df"]
        sentiment = summary["_sentiment"]

    # ── KPI Cards ──────────────────────────────────────────────────────────────
    kpi_items = []
    cols5 = st.columns(5)

    containment = kpis.get("containment_rate")
    escalation  = kpis.get("escalation_rate")
    intent_acc  = kpis.get("intent_accuracy")
    csat        = kpis.get("csat_score")
    fallback    = kpis.get("fallback_rate")

    if containment is not None:
        kpi_items.append((cols5[0], f"{containment}%",
                         "#10b981" if containment >= 70 else "#ef4444", "Containment Rate"))
    if escalation is not None:
        kpi_items.append((cols5[1], f"{escalation}%",
                         "#ef4444" if escalation > 30 else "#10b981", "Escalation Rate"))
    if intent_acc is not None:
        kpi_items.append((cols5[2], f"{intent_acc}%",
                         "#10b981" if intent_acc >= 85 else "#f59e0b", "Intent Accuracy"))
    if csat is not None:
        kpi_items.append((cols5[3], f"{csat}/5",
                         "#10b981" if csat >= 3.5 else "#ef4444", "CSAT Score"))
    if fallback is not None:
        kpi_items.append((cols5[4], f"{fallback}%",
                         "#ef4444" if fallback > 20 else "#10b981", "Fallback Rate"))

    if kpi_items:
        mcard(kpi_items[:5])
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauge Row ──────────────────────────────────────────────────────────────
    gauge_items = []
    if containment is not None: gauge_items.append(("containment_rate", 70, "Containment Rate", "%"))
    if intent_acc  is not None: gauge_items.append(("intent_accuracy",  85, "Intent Accuracy",  "%"))
    if csat        is not None: gauge_items.append(("csat_score",       3.5,"CSAT Score",        "/5"))

    if gauge_items:
        sec("📊 Key Performance Gauges")
        gcols = st.columns(len(gauge_items))
        for i, (key, target, label, unit) in enumerate(gauge_items):
            val = kpis.get(key, 0)
            with gcols[i]:
                render_chart(voicebot_kpi_gauge(val, target, label, unit), f"gauge_{i}")

    # ── Intent Analysis ────────────────────────────────────────────────────────
    if not intent_df.empty:
        sec("🧠 Intent Recognition Analysis", "amber")
        cl, cr = st.columns([3,2])
        with cl:
            render_chart(voicebot_intent_chart(intent_df), "intent_chart")
        with cr:
            st.dataframe(intent_df.style.background_gradient(subset=["accuracy_%"], cmap="RdYlGn"),
                         use_container_width=True, hide_index=True)

    # ── Escalation ────────────────────────────────────────────────────────────
    if not escal_df.empty:
        sec("📞 Escalation Analysis", "red")
        cl, cr = st.columns([2,3])
        with cl:
            render_chart(voicebot_escalation_chart(escal_df), "escal_chart")
        with cr:
            st.dataframe(escal_df, use_container_width=True, hide_index=True)

    # ── Failure Patterns ──────────────────────────────────────────────────────
    if not fail_df.empty:
        sec("⚠️ Failure Patterns", "amber")
        render_chart(voicebot_failure_chart(fail_df), "fail_chart")
        st.dataframe(fail_df, use_container_width=True, hide_index=True)

    # ── Bot Performance Comparison ────────────────────────────────────────────
    if not bot_df.empty and len(bot_df) > 1:
        sec("🤖 Bot Performance Comparison")
        st.dataframe(
            bot_df.style.background_gradient(subset=["overall_score"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True
        )

    # ── Sentiment ─────────────────────────────────────────────────────────────
    if sentiment:
        sec("😊 Sentiment Distribution")
        scols = st.columns(len(sentiment))
        sentiment_colors = {"positive":"#10b981","neutral":"#3b82f6","negative":"#ef4444"}
        for i, (label, count) in enumerate(sentiment.items()):
            pct = round(count / len(raw_df) * 100, 1)
            ac  = sentiment_colors.get(label.lower(), "#8b5cf6")
            with scols[i]:
                st.markdown(f'<div class="qie-card" style="--ac:{ac};"><div class="v">{pct}%</div><div class="l">{label.title()}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Additional KPI Details ────────────────────────────────────────────────
    extra_kpis = {k: v for k, v in kpis.items()
                  if k not in {"containment_rate","escalation_rate","intent_accuracy",
                                "csat_score","fallback_rate","containment_target",
                                "containment_status","csat_target","silence_warning"}
                  and not isinstance(v, str)}
    if extra_kpis:
        with st.expander("📋 All KPI Details", expanded=False):
            kpi_df = pd.DataFrame(list(extra_kpis.items()), columns=["Metric","Value"])
            st.dataframe(kpi_df, use_container_width=True, hide_index=True)

    # ── AI Analysis ───────────────────────────────────────────────────────────
    sec("🤖 Claude AI — Voicebot Intelligence Report", "purple")
    if st.button("🚀 Generate AI Voicebot Analysis", key="vb_ai_btn"):
        with st.spinner("Claude analysing voicebot performance data...  ~25 seconds"):
            try:
                result = analyse_voicebot(summary)
                st.session_state["vb_ai"] = result
            except Exception as e:
                st.error(str(e))

    if "vb_ai" in st.session_state:
        r = st.session_state["vb_ai"]
        with st.expander("🏆 Performance Verdict",       expanded=True):  ai_section(r, "PERFORMANCE VERDICT")
        with st.expander("📞 Containment Analysis",      expanded=False): ai_section(r, "CONTAINMENT ANALYSIS")
        with st.expander("🧠 Intent & NLU Analysis",     expanded=False): ai_section(r, "INTENT")
        with st.expander("🔁 Conversation Flow Failures",expanded=False): ai_section(r, "CONVERSATION FLOW")
        with st.expander("🗺️ Optimisation Roadmap",      expanded=False): ai_section(r, "OPTIMISATION")
        with st.expander("📧 Executive Summary",          expanded=False): ai_section(r, "EXECUTIVE SUMMARY")
        with st.expander("📄 Full Report",                expanded=False): ai_box(r)

# ── Router ────────────────────────────────────────────────────────────────────
if   PAGE == "🏠  Dashboard":            page_dashboard()
elif PAGE == "📂  Audit Sheet Analysis": page_audit_analysis()
elif PAGE == "🚨  Transcript Scanner":   page_transcripts()
elif PAGE == "🎯  Agent Scorecards":     page_scorecards()
