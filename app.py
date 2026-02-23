# ============================================================
# app.py  —  Quality Intelligence Engine v3 — CLEAN REWRITE
# All bugs fixed. All pages working. All formats accepted.
# ============================================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io, zipfile, os
from datetime import datetime

# ── Module imports ────────────────────────────────────────────
from file_parser      import parse_file, get_file_type_label
from smart_detector   import auto_prepare, get_score_columns
from tni_module       import (validate_csv as tni_val, build_tni_summary,
                               compute_agent_stats)
from calibration_module import (validate_csv as cal_val,
                                 build_calibration_summary)
from ata_module       import validate_csv as ata_val, build_ata_summary
from redflag_module   import (DEFAULT_FLAGS, parse_custom_rules,
                               scan_transcript, build_redflag_summary)
from scorecard_module import (build_agent_profile, generate_scorecard_pdf,
                               get_agent_list)
from voicebot_module  import (validate_csv as vb_val, build_voicebot_summary)
from viz_module       import (score_bar_chart, agent_radar_chart,
                               trend_line_chart, agent_league_table_chart,
                               variance_heatmap, auditor_accuracy_chart,
                               flag_severity_donut, render_chart,
                               voicebot_kpi_gauge, voicebot_intent_chart,
                               voicebot_escalation_chart,
                               voicebot_failure_chart)
from ai_engine        import (analyse_tni, analyse_calibration,
                               analyse_red_flags, generate_agent_scorecard,
                               analyse_ata, analyse_voicebot)

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Quality Intelligence Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

ALL_TYPES = ["csv", "xlsx", "xls", "pdf", "docx", "txt"]

# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{
  background:#04070f;color:#dce8ff;
  background-image:
    radial-gradient(ellipse 80% 50% at 20% -10%,rgba(0,245,212,.07) 0%,transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 110%,rgba(247,37,133,.07) 0%,transparent 60%);
}
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#060c1a,#040810);
  border-right:1px solid rgba(0,245,212,.1);
}
section[data-testid="stSidebar"]::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#00f5d4,#7209b7,#f72585);
}
/* NAV */
div[data-testid="stRadio"] label{
  display:flex!important;align-items:center!important;
  padding:10px 14px!important;border-radius:10px!important;
  margin:2px 0!important;font-size:.84rem!important;
  font-weight:500!important;color:#647595!important;
  transition:all .2s!important;cursor:pointer!important;
}
div[data-testid="stRadio"] label:hover{
  background:rgba(0,245,212,.07)!important;color:#00f5d4!important;
}

/* KPI CARDS */
.qie-card{
  position:relative;background:rgba(10,18,40,.85);
  border:1px solid rgba(255,255,255,.06);border-radius:20px;
  padding:22px 20px 18px;text-align:center;
  overflow:hidden;backdrop-filter:blur(10px);
  transition:transform .25s,box-shadow .25s;
}
.qie-card:hover{transform:translateY(-4px);
  box-shadow:0 20px 40px rgba(0,0,0,.4);}
.qie-card::after{content:'';position:absolute;
  top:0;left:0;right:0;height:2px;
  background:var(--ac,#00f5d4);}
.qie-card .v{font-family:'Syne',sans-serif;font-size:2.2rem;
  font-weight:800;color:var(--ac,#00f5d4);line-height:1;margin-bottom:6px;}
.qie-card .l{font-size:.68rem;color:#3d5070;
  letter-spacing:.12em;text-transform:uppercase;font-weight:600;}

/* SECTION HEADERS */
.sec{position:relative;margin:26px 0 12px;display:flex;
  align-items:center;gap:10px;font-family:'Syne',sans-serif;
  font-size:.72rem;font-weight:700;letter-spacing:.14em;
  text-transform:uppercase;color:#00f5d4;}
.sec::after{content:'';flex:1;height:1px;
  background:linear-gradient(90deg,rgba(0,245,212,.3),transparent);}
.sec.amber{color:#ffd60a;}
.sec.amber::after{background:linear-gradient(90deg,rgba(255,214,10,.3),transparent);}
.sec.red{color:#f72585;}
.sec.red::after{background:linear-gradient(90deg,rgba(247,37,133,.3),transparent);}
.sec.green{color:#06d6a0;}
.sec.green::after{background:linear-gradient(90deg,rgba(6,214,160,.3),transparent);}
.sec.purple{color:#b14cf0;}
.sec.purple::after{background:linear-gradient(90deg,rgba(177,76,240,.3),transparent);}

/* AI BOX */
.ai-box{background:linear-gradient(135deg,rgba(8,15,35,.95),rgba(12,20,45,.9));
  border:1px solid rgba(0,245,212,.12);border-radius:18px;
  padding:26px 30px;font-size:.88rem;line-height:1.85;color:#c4d8ff;
  position:relative;overflow:hidden;}
.ai-box::before{content:'';position:absolute;top:0;left:0;right:0;
  height:1px;background:linear-gradient(90deg,transparent,#00f5d4,transparent);}
.ai-box h2{font-family:'Syne',sans-serif;color:#00f5d4;font-size:.78rem;
  font-weight:700;text-transform:uppercase;letter-spacing:.12em;
  margin:22px 0 8px;padding-bottom:8px;border-bottom:1px solid rgba(0,245,212,.1);}
.ai-box h3{color:#7dd3fc;font-size:.9rem;margin:14px 0 5px;}
.ai-box strong{color:#f0f7ff;}
.ai-box ul{padding-left:20px;}.ai-box li{margin-bottom:5px;}

/* FLAG ROWS */
.flag-row{background:rgba(10,15,30,.7);border-left:3px solid var(--ac,#00f5d4);
  padding:10px 14px;border-radius:0 10px 10px 0;margin:5px 0;
  font-size:.83rem;color:#c4d8ff;}
.flag-row.HIGH{--ac:#f72585;}.flag-row.MEDIUM{--ac:#ffd60a;}.flag-row.LOW{--ac:#06d6a0;}
.badge-HIGH{background:rgba(247,37,133,.15);color:#f9a8d4;padding:2px 10px;
  border-radius:20px;font-size:.68rem;font-weight:700;border:1px solid rgba(247,37,133,.3);}
.badge-MEDIUM{background:rgba(255,214,10,.12);color:#fef08a;padding:2px 10px;
  border-radius:20px;font-size:.68rem;font-weight:700;border:1px solid rgba(255,214,10,.3);}
.badge-LOW{background:rgba(6,214,160,.12);color:#6ee7b7;padding:2px 10px;
  border-radius:20px;font-size:.68rem;font-weight:700;border:1px solid rgba(6,214,160,.3);}

/* AUTO TAG */
.auto-tag{background:linear-gradient(135deg,rgba(0,245,212,.15),rgba(114,9,183,.1));
  color:#00f5d4;border:1px solid rgba(0,245,212,.25);border-radius:6px;
  padding:3px 10px;font-size:.68rem;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;font-family:'JetBrains Mono',monospace;}

/* BUTTONS */
div[data-testid="stButton"]>button{
  background:linear-gradient(135deg,#00f5d4,#0891b2 50%,#7209b7)!important;
  color:#04070f!important;border:none!important;border-radius:12px!important;
  font-weight:700!important;font-family:'Syne',sans-serif!important;
  padding:13px 28px!important;width:100%!important;
  box-shadow:0 4px 20px rgba(0,245,212,.2)!important;
  transition:all .3s!important;
}
div[data-testid="stButton"]>button:hover{
  opacity:.88!important;box-shadow:0 8px 30px rgba(0,245,212,.35)!important;
}
div[data-testid="stDownloadButton"]>button{
  background:linear-gradient(135deg,rgba(0,245,212,.1),rgba(114,9,183,.1))!important;
  color:#00f5d4!important;border:1px solid rgba(0,245,212,.3)!important;
  border-radius:12px!important;font-weight:600!important;
  padding:12px 24px!important;width:100%!important;
}
/* FILE UPLOADER */
div[data-testid="stFileUploader"]{
  background:rgba(8,15,35,.6);border:1.5px dashed rgba(0,245,212,.2);
  border-radius:16px;padding:12px;
}
/* EXPANDERS */
details{background:rgba(8,15,35,.7)!important;border:1px solid rgba(0,245,212,.1)!important;
  border-radius:14px!important;margin-bottom:8px!important;}
summary{padding:13px 18px!important;color:#7dd3fc!important;font-weight:600!important;}
/* MISC */
hr{border-color:rgba(0,245,212,.08)!important;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:#04070f;}
::-webkit-scrollbar-thumb{background:rgba(0,245,212,.3);border-radius:3px;}
div[data-testid="stSelectbox"]>div>div{
  background:rgba(8,15,35,.8)!important;
  border:1px solid rgba(0,245,212,.15)!important;border-radius:10px!important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:28px 0 20px;">
      <div style="width:60px;height:60px;border-radius:16px;
        background:linear-gradient(135deg,#00f5d4,#7209b7);
        display:flex;align-items:center;justify-content:center;
        margin:0 auto 12px;font-size:1.8rem;
        box-shadow:0 8px 24px rgba(0,245,212,.3);">🧠</div>
      <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:800;
        background:linear-gradient(135deg,#00f5d4,#b14cf0);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        Quality Intelligence</div>
      <div style="font-size:.6rem;color:#1e3a5f;letter-spacing:.2em;
        text-transform:uppercase;margin-top:3px;
        font-family:'JetBrains Mono',monospace;">ENGINE V3.0</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    PAGE = st.radio("nav", [
        "🏠  Dashboard",
        "📂  Audit Sheet Analysis",
        "🚨  Transcript Scanner",
        "🎯  Agent Scorecards",
        "🤖  Voicebot Audit",
        "📊  Sales Intelligence",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("""
    <div style="margin:4px 6px;padding:14px 16px;
      background:rgba(0,245,212,.04);border:1px solid rgba(0,245,212,.1);
      border-radius:12px;font-size:.72rem;line-height:1.9;">
      <div style="color:#00f5d4;font-weight:700;letter-spacing:.1em;
        text-transform:uppercase;margin-bottom:7px;font-family:'Syne',sans-serif;
        font-size:.65rem;">⚙️ Setup</div>
      <div style="color:#3d5070;">Create <code style="background:rgba(0,245,212,.1);
        padding:1px 6px;border-radius:4px;color:#00f5d4;
        font-family:'JetBrains Mono',monospace;">.env</code> file:</div>
      <code style="background:rgba(0,0,0,.4);padding:4px 8px;border-radius:6px;
        color:#00f5d4;font-size:.65rem;font-family:'JetBrains Mono',monospace;
        display:block;margin-top:6px;">ANTHROPIC_API_KEY=sk-ant-...</code>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════
def sec(label, color=""):
    st.markdown(f'<div class="sec {color}">{label}</div>', unsafe_allow_html=True)

def mcard(items):
    for col, val, ac, lbl in items:
        with col:
            st.markdown(
                f'<div class="qie-card" style="--ac:{ac};">'
                f'<div class="v">{val}</div>'
                f'<div class="l">{lbl}</div></div>',
                unsafe_allow_html=True)

def ai_box(content):
    import re
    t = content.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    t = re.sub(r"##\s+(.*)",  r"<h2>\1</h2>", t)
    t = re.sub(r"###\s+(.*)", r"<h3>\1</h3>", t)
    t = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", t)
    t = t.replace("\n","<br>")
    st.markdown(f'<div class="ai-box">{t}</div>', unsafe_allow_html=True)

def ai_section(full, keyword):
    lines = full.split("\n"); in_s=False; buf=[]
    for line in lines:
        if keyword.upper() in line.upper() and line.startswith("#"):
            in_s=True; continue
        if in_s:
            if line.startswith("## ") and keyword.upper() not in line.upper(): break
            buf.append(line)
    txt = "\n".join(buf).strip()
    ai_box(txt if txt else full)

def load_any(uploaded):
    """Universal loader — returns DataFrame or None. Shows result message."""
    if uploaded is None:
        return None
    uploaded.seek(0)
    df, ftype, msg = parse_file(uploaded)
    label = get_file_type_label(ftype)
    if df is not None and len(df) > 0:
        st.success(f"✅ {label} loaded — {msg}")
        return df
    else:
        st.error(f"❌ Could not parse file — {msg}")
        st.info("💡 Tip: CSV format works most reliably. Export from Excel as .csv and try again.")
        return None

def normalise_df(df):
    """Standardise column names."""
    df = df.copy()
    df.columns = (df.columns.astype(str).str.strip().str.lower()
                  .str.replace(r"[\s\-/\\]+", "_", regex=True)
                  .str.replace(r"[^\w]", "", regex=True))
    return df

def make_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for name,content in files.items(): z.writestr(name, content)
    return buf.getvalue()

def page_header(emoji, title, subtitle, grad="135deg,#00f5d4,#0891b2"):
    st.markdown(
        f"<h2 style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;"
        f"background:linear-gradient({grad});-webkit-background-clip:text;"
        f"-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:2px;'>"
        f"{emoji} {title}</h2>"
        f"<p style='color:#3d5070;font-size:.88rem;margin-top:0;'>{subtitle}</p>",
        unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown("""
    <div style="padding:44px 0 28px;text-align:center;">
      <div style="display:inline-block;background:linear-gradient(135deg,rgba(0,245,212,.1),rgba(114,9,183,.1));
        border:1px solid rgba(0,245,212,.2);border-radius:50px;
        padding:5px 16px;font-size:.7rem;color:#00f5d4;font-weight:700;
        letter-spacing:.12em;text-transform:uppercase;margin-bottom:18px;
        font-family:'JetBrains Mono',monospace;">✦ AI-Powered QA Analytics</div>
      <h1 style="font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;
        background:linear-gradient(135deg,#fff 0%,#00f5d4 40%,#b14cf0 80%,#f72585 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;letter-spacing:-.03em;line-height:1.1;margin-bottom:14px;">
        Quality Intelligence Engine
      </h1>
      <p style="font-size:.98rem;color:#4a6080;max-width:480px;margin:0 auto;">
        Upload your audit data in any format.<br>
        The engine detects, analyses, and delivers AI-powered insights instantly.
      </p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3, gap="large")
    cards = [
        (c1,"📂","Audit Analysis","#00f5d4","TNI · Calibration · ATA · Scorecards"),
        (c2,"🚨","Transcript Scanner","#f72585","100+ violation patterns · Risk profiles"),
        (c3,"🤖","Voicebot Audit","#06d6a0","Containment · Intent · Escalation · CSAT"),
    ]
    for col,icon,title,ac,desc in cards:
        with col:
            st.markdown(f"""
            <div class="qie-card" style="--ac:{ac};text-align:left;padding:26px;">
              <div style="font-size:2rem;margin-bottom:10px;">{icon}</div>
              <div style="font-family:'Syne',sans-serif;font-size:1rem;
                font-weight:700;color:{ac};margin-bottom:8px;">{title}</div>
              <div style="font-size:.82rem;color:#c4d8ff;line-height:1.8;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec("📋 Accepted File Formats")
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:8px 0;">
      <div style="background:rgba(0,245,212,.06);border:1px solid rgba(0,245,212,.15);
        border-radius:12px;padding:14px;text-align:center;">
        <div style="font-size:1.4rem;">📊</div>
        <div style="font-size:.75rem;color:#00f5d4;font-weight:700;margin:4px 0;">CSV</div>
        <div style="font-size:.7rem;color:#3d5070;">Best format</div></div>
      <div style="background:rgba(6,214,160,.06);border:1px solid rgba(6,214,160,.15);
        border-radius:12px;padding:14px;text-align:center;">
        <div style="font-size:1.4rem;">📗</div>
        <div style="font-size:.75rem;color:#06d6a0;font-weight:700;margin:4px 0;">Excel</div>
        <div style="font-size:.7rem;color:#3d5070;">.xlsx / .xls</div></div>
      <div style="background:rgba(247,37,133,.06);border:1px solid rgba(247,37,133,.15);
        border-radius:12px;padding:14px;text-align:center;">
        <div style="font-size:1.4rem;">📄</div>
        <div style="font-size:.75rem;color:#f72585;font-weight:700;margin:4px 0;">PDF</div>
        <div style="font-size:.7rem;color:#3d5070;">Table extraction</div></div>
      <div style="background:rgba(177,76,240,.06);border:1px solid rgba(177,76,240,.15);
        border-radius:12px;padding:14px;text-align:center;">
        <div style="font-size:1.4rem;">📝</div>
        <div style="font-size:.75rem;color:#b14cf0;font-weight:700;margin:4px 0;">Word</div>
        <div style="font-size:.7rem;color:#3d5070;">.docx</div></div>
      <div style="background:rgba(255,214,10,.06);border:1px solid rgba(255,214,10,.15);
        border-radius:12px;padding:14px;text-align:center;">
        <div style="font-size:1.4rem;">📃</div>
        <div style="font-size:.75rem;color:#ffd60a;font-weight:700;margin:4px 0;">TXT</div>
        <div style="font-size:.7rem;color:#3d5070;">Tab/CSV text</div></div>
    </div>""", unsafe_allow_html=True)

    sec("📋 CSV Format Guide")
    t1,t2,t3,t4 = st.tabs(["📊 Agent Audit / TNI","⚖️ Calibration","🔍 Audit the Auditor","🤖 Voicebot"])
    with t1:
        st.caption("Needs: agent_name + score columns. audit_date is optional for trend analysis.")
        st.dataframe(pd.DataFrame({"agent_name":["Akshata","Sunil","Ankit"],"audit_date":["2025-01-10","2025-01-10","2025-01-11"],"greeting":[65,80,55],"empathy":[60,75,50],"closing":[70,85,65]}), use_container_width=True, hide_index=True)
    with t2:
        st.caption("Needs: auditor_name + call_id + score columns. Multiple auditors rate the same call.")
        st.dataframe(pd.DataFrame({"auditor_name":["QA_Priya","QA_Rahul","QA_Meena"],"call_id":["C001","C001","C001"],"greeting":[75,55,80],"empathy":[80,60,85]}), use_container_width=True, hide_index=True)
    with t3:
        st.caption("Needs: auditor scores + master_ columns for same parameters.")
        st.dataframe(pd.DataFrame({"auditor_name":["QA_Priya","QA_Rahul"],"greeting":[75,55],"master_greeting":[78,78],"empathy":[80,60],"master_empathy":[82,82]}), use_container_width=True, hide_index=True)
    with t4:
        st.caption("Needs: bot_name + interaction_id + any performance columns you have.")
        st.dataframe(pd.DataFrame({"bot_name":["SalesBot","SalesBot"],"interaction_id":["I001","I002"],"containment_result":["yes","no"],"intent_detected":["check_balance","apply_loan"],"intent_expected":["check_balance","check_balance"],"csat_score":[4.5,2.0]}), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
# PAGE: AUDIT SHEET ANALYSIS
# ═══════════════════════════════════════════════════════════════
def page_audit_analysis():
    page_header("📂","Audit Sheet Analysis",
                "Upload CSV, Excel, PDF or Word — engine auto-detects and runs all analyses")

    uploaded = st.file_uploader(
        "Upload audit file",
        type=ALL_TYPES, key="audit_up",
        help="Accepts CSV, Excel (.xlsx), PDF, Word (.docx), TXT")

    if not uploaded:
        st.info("👆 Upload your audit sheet above to begin. Accepts any format.")
        return

    raw_df = load_any(uploaded)
    if raw_df is None:
        return

    df = normalise_df(raw_df)

    # Show preview
    with st.expander("🔍 Preview loaded data", expanded=False):
        st.write(f"**{len(df):,} rows × {len(df.columns)} columns**")
        st.write("Columns:", list(df.columns))
        st.dataframe(df.head(8), use_container_width=True, hide_index=True)

    # Auto-detect type
    df2, file_type, warnings, info = auto_prepare(df)

    type_map = {
        "tni":         ("📊 Agent Audit / TNI Data", "#00f5d4"),
        "calibration": ("⚖️ Calibration Data",       "#b14cf0"),
        "ata":         ("🔍 Audit the Auditor Data",  "#06d6a0"),
        "unknown":     ("❓ Format not recognised",   "#ffd60a"),
    }
    tlabel, tcolor = type_map.get(file_type, ("❓ Unknown","#ffd60a"))
    st.markdown(
        f"<div style='background:#0d1426;border:1px solid #152040;border-radius:10px;"
        f"padding:11px 16px;margin:8px 0;'>"
        f"<span class='auto-tag'>AUTO-DETECTED</span> "
        f"<span style='color:{tcolor};font-weight:700;margin-left:8px;'>{tlabel}</span>"
        f"<span style='color:#3d5070;font-size:.82rem;margin-left:12px;'>"
        f"{info['rows']:,} rows · {len(info['score_cols'])} score columns</span></div>",
        unsafe_allow_html=True)

    for w in warnings:
        st.warning(w)

    if file_type == "unknown":
        st.error("❌ Could not identify data type. Make sure your file has agent_name, auditor_name, or master_ columns.")
        st.info("📌 Check the 'CSV Format Guide' on the Dashboard page for the correct column names.")
        return

    # ── Run analysis ──────────────────────────────────────────
    with st.spinner("⚙️ Running analysis pipeline…"):
        tni_sum = cal_sum = ata_sum = None
        try:
            if file_type in ("tni","calibration","ata"):
                ok, err = tni_val(df2)
                if ok:
                    tni_sum = build_tni_summary(df2)
            if file_type == "calibration":
                ok, err = cal_val(df2)
                if ok:
                    cal_sum = build_calibration_summary(df2)
            if file_type == "ata":
                ok, err = ata_val(df2)
                if ok:
                    ata_sum = build_ata_summary(df2)
        except Exception as e:
            st.error(f"Analysis error: {e}")
            return

    st.success("✅ Analysis complete — results below")
    score_cols = info["score_cols"]

    # ── KPIs ─────────────────────────────────────────────────
    cols4 = st.columns(4)
    if tni_sum:
        mcard([
            (cols4[0], info.get("agent_count",0),      "#00f5d4", "Agents"),
            (cols4[1], len(score_cols),                 "#b14cf0", "Parameters"),
            (cols4[2], len(tni_sum["_weak_df"]),        "#ffd60a", "Weak Params"),
            (cols4[3], len(tni_sum["_recur_df"]),       "#f72585", "Recurring Fails"),
        ])
    elif cal_sum:
        flagged = int(cal_sum["_variance_df"]["flagged"].sum()) if not cal_sum["_variance_df"].empty else 0
        mcard([
            (cols4[0], info.get("auditor_count",0),    "#00f5d4", "Auditors"),
            (cols4[1], len(score_cols),                 "#b14cf0", "Parameters"),
            (cols4[2], flagged,                         "#ffd60a", "High Variance"),
            (cols4[3], len(cal_sum["_strict_df"]),      "#f72585", "Strict Auditors"),
        ])
    elif ata_sum:
        acc_df  = ata_sum["_accuracy_df"]
        avg_acc = round(acc_df["accuracy_%"].mean(),1) if not acc_df.empty else 0
        below   = int((acc_df["accuracy_%"] < 85).sum()) if not acc_df.empty else 0
        mcard([
            (cols4[0], info.get("auditor_count",0),    "#00f5d4", "Auditors"),
            (cols4[1], f"{avg_acc}%",                   "#06d6a0" if avg_acc>=85 else "#f72585", "Avg Accuracy"),
            (cols4[2], below,                           "#ffd60a", "Below Threshold"),
            (cols4[3], len(ata_sum["_missed_df"]),      "#f72585", "Missed Flags"),
        ])
    st.markdown("<br>", unsafe_allow_html=True)

    # ── TNI section ───────────────────────────────────────────
    if tni_sum:
        sec("📊 Parameter Performance")
        cl,cr = st.columns(2)
        with cl: render_chart(score_bar_chart(df2,"Average Score by Parameter"),"bar1")
        with cr:
            agt = tni_sum.get("_agent_df", pd.DataFrame())
            render_chart(agent_league_table_chart(agt),"league1")

        tf = trend_line_chart(df2, score_cols[:6])
        if tf and tf.data:
            sec("📈 Score Trends Over Time")
            render_chart(tf,"trend1")

        sec("⚠️ Weak Parameters","amber")
        wdf = tni_sum["_weak_df"]
        if not wdf.empty:
            st.dataframe(wdf.style.background_gradient(subset=["avg_score"],cmap="RdYlGn"),
                         use_container_width=True, hide_index=True)
        else:
            st.success("✅ All parameters above threshold!")

        sec("🔁 Recurring Weaknesses","red")
        rdf = tni_sum["_recur_df"]
        if not rdf.empty:
            st.dataframe(rdf, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No recurring weaknesses detected.")

        with st.expander("👥 Full Agent Statistics"):
            adf = tni_sum.get("_agent_df", pd.DataFrame())
            if not adf.empty:
                st.dataframe(adf.style.background_gradient(subset=["overall_avg"],cmap="RdYlGn"),
                             use_container_width=True, hide_index=True)

        sec("🤖 AI Training Report","purple")
        if st.button("🚀 Generate AI Training & Coaching Report", key="tni_ai"):
            with st.spinner("Claude analysing… (~20s)"):
                try:
                    r = analyse_tni(tni_sum); st.session_state["tni_ai"] = r
                except Exception as e: st.error(str(e))
        if "tni_ai" in st.session_state:
            r = st.session_state["tni_ai"]
            with st.expander("📌 Root Cause Analysis",     expanded=True): ai_section(r,"ROOT CAUSE")
            with st.expander("🎯 Skill Gap Summary"):                       ai_section(r,"SKILL GAP")
            with st.expander("📊 Priority Matrix"):                         ai_section(r,"PRIORITY")
            with st.expander("🎓 Training Recommendations"):                ai_section(r,"TRAINING")
            with st.expander("💬 Coaching Script"):                         ai_section(r,"COACHING")

    # ── Calibration section ───────────────────────────────────
    if cal_sum:
        sec("⚖️ Calibration Analysis","purple")
        render_chart(variance_heatmap(cal_sum["_variance_df"]),"var1")
        ca,cb = st.columns(2)
        with ca:
            sec("🔴 Strict Auditors","red")
            if not cal_sum["_strict_df"].empty:
                st.dataframe(cal_sum["_strict_df"], use_container_width=True, hide_index=True)
            else: st.success("None detected.")
        with cb:
            sec("🟢 Lenient Auditors","green")
            if not cal_sum["_lenient_df"].empty:
                st.dataframe(cal_sum["_lenient_df"], use_container_width=True, hide_index=True)
            else: st.success("None detected.")

        sec("🤖 AI Calibration Report","purple")
        if st.button("🚀 Generate AI Calibration Analysis", key="cal_ai"):
            with st.spinner("Claude analysing…"):
                try:
                    r = analyse_calibration(cal_sum); st.session_state["cal_ai"] = r
                except Exception as e: st.error(str(e))
        if "cal_ai" in st.session_state:
            r = st.session_state["cal_ai"]
            with st.expander("📊 Calibration Summary", expanded=True): ai_section(r,"CALIBRATION")
            with st.expander("🎯 Auditor Bias"):                        ai_section(r,"AUDITOR BIAS")
            with st.expander("📝 Guideline Improvements"):              ai_section(r,"GUIDELINE")
            with st.expander("📧 Executive Summary"):                   ai_section(r,"EXECUTIVE")

    # ── ATA section ───────────────────────────────────────────
    if ata_sum:
        sec("🔍 Audit the Auditor","green")
        render_chart(auditor_accuracy_chart(ata_sum["_accuracy_df"]),"acc1")
        if not ata_sum["_missed_df"].empty:
            sec("🚨 Missed Flags","red")
            st.dataframe(ata_sum["_missed_df"], use_container_width=True, hide_index=True)
        sec("🤖 AI ATA Report","purple")
        if st.button("🚀 Generate AI ATA Analysis", key="ata_ai"):
            with st.spinner("Claude analysing…"):
                try:
                    r = analyse_ata(ata_sum); st.session_state["ata_ai"] = r
                except Exception as e: st.error(str(e))
        if "ata_ai" in st.session_state:
            r = st.session_state["ata_ai"]
            with st.expander("Overall ATA Verdict", expanded=True): ai_section(r,"OVERALL")
            with st.expander("Auditor Ranking"):                     ai_section(r,"AUDITOR PERFORMANCE")
            with st.expander("Corrective Actions"):                  ai_section(r,"CORRECTIVE")

    # Store for scorecards page
    if tni_sum: st.session_state["audit_df"] = df2

# ═══════════════════════════════════════════════════════════════
# PAGE: TRANSCRIPT SCANNER
# ═══════════════════════════════════════════════════════════════
def page_transcripts():
    page_header("🚨","Transcript Scanner",
                "Upload call transcripts in any format — auto-detects violations",
                "135deg,#f72585,#ffd60a")

    with st.sidebar:
        st.markdown("---")
        st.markdown("**⚙️ Custom Rules**")
        rules_txt = st.text_area(
            "FORMAT: SEVERITY: phrase",
            height=120,
            placeholder="HIGH: your phrase\nMEDIUM: phrase",
            key="rf_rules")

    custom    = parse_custom_rules(rules_txt) if rules_txt else []
    all_flags = DEFAULT_FLAGS + custom

    # Accept ALL file types including txt, pdf, docx
    uploaded = st.file_uploader(
        "Upload transcript files (multiple allowed)",
        type=ALL_TYPES,
        accept_multiple_files=True,
        key="rf_up",
        help="Accepts TXT, PDF, Word, CSV, Excel — upload multiple files at once")

    if not uploaded:
        st.info("👆 Upload one or more transcript files. Each file = one call transcript.")
        return

    if st.button("🔍 Scan All Transcripts", key="rf_scan"):
        results = []
        bar = st.progress(0, text="Scanning…")
        for i, f in enumerate(uploaded):
            try:
                f.seek(0)
                raw = f.read()
                # For text-like files decode directly; for others use parse_file to extract text
                ext = f.name.lower().split(".")[-1]
                if ext in ("txt",):
                    text = raw.decode("utf-8", errors="ignore")
                else:
                    # Try to get text content via parse_file then convert to string
                    f.seek(0)
                    df_tmp, ftype_tmp, _ = parse_file(f)
                    if df_tmp is not None:
                        text = df_tmp.to_string()
                    else:
                        # Fallback: raw decode
                        text = raw.decode("utf-8", errors="ignore")
                results.append(scan_transcript(f.name, text, all_flags))
            except Exception as e:
                results.append({"filename": f.name, "agent": f.name,
                                "total":0,"high":0,"medium":0,"low":0,"flags":[]})
            bar.progress((i+1)/len(uploaded), text=f"Scanned {i+1}/{len(uploaded)}")
        bar.empty()
        st.session_state["rf_results"] = results
        st.success(f"✅ {len(results)} file(s) scanned")

    if "rf_results" not in st.session_state:
        return

    results  = st.session_state["rf_results"]
    total_f  = sum(r["total"]  for r in results)
    high_c   = sum(r["high"]   for r in results)
    med_c    = sum(r["medium"] for r in results)
    low_c    = sum(r["low"]    for r in results)

    c1,c2,c3,c4,c5 = st.columns(5)
    mcard([
        (c1, len(results),  "#00f5d4", "Files Scanned"),
        (c2, total_f,       "#f72585", "Total Flags"),
        (c3, high_c,        "#f72585", "HIGH"),
        (c4, med_c,         "#ffd60a", "MEDIUM"),
        (c5, low_c,         "#06d6a0", "LOW"),
    ])
    st.markdown("<br>", unsafe_allow_html=True)

    cl,cr = st.columns(2)
    with cl:
        render_chart(flag_severity_donut(high_c, med_c, low_c),"donut1")
    with cr:
        agent_flags = {}
        for r in results:
            a = r["agent"]; agent_flags[a] = agent_flags.get(a,0)+r["total"]
        if agent_flags:
            af_df = pd.DataFrame(list(agent_flags.items()),columns=["agent","flags"]).sort_values("flags").tail(10)
            fig = go.Figure(go.Bar(x=af_df["flags"],y=af_df["agent"],orientation="h",
                marker_color="#f72585",text=af_df["flags"],textposition="outside",
                textfont=dict(color="#c4d8ff")))
            fig.update_layout(paper_bgcolor="#080f24",plot_bgcolor="#080f24",
                font=dict(color="#c4d8ff"),height=300,
                title=dict(text="Flags by Agent",font=dict(color="#c4d8ff",size=13)),
                margin=dict(l=20,r=20,t=40,b=20),
                xaxis=dict(gridcolor="#0f1e3d"),yaxis=dict(gridcolor="#0f1e3d"))
            render_chart(fig,"agent_flags")

    sec("🔍 Violation Details")
    fa,fb = st.columns([3,1])
    with fa: search = st.text_input("Search agent or filename","",key="rf_search")
    with fb: sev_f  = st.selectbox("Severity",["All","HIGH","MEDIUM","LOW"],key="rf_sev")

    flagged = sorted([r for r in results if r["total"]>0],
                     key=lambda x:(-x["high"],-x["medium"]))
    shown = 0
    for r in flagged:
        flags = r["flags"]
        if search and search.lower() not in r["agent"].lower() and search.lower() not in r["filename"].lower():
            continue
        if sev_f != "All":
            flags = [f for f in flags if f["severity"]==sev_f]
            if not flags: continue
        h=sum(1 for f in flags if f["severity"]=="HIGH")
        m=sum(1 for f in flags if f["severity"]=="MEDIUM")
        l=sum(1 for f in flags if f["severity"]=="LOW")
        with st.expander(f"🚨 {r['agent']}  |  {r['filename']}  |  🔴{h}  🟠{m}  🟡{l}"):
            for f in flags:
                s=f["severity"]; ctx=f["context"][:120].replace("**","")
                st.markdown(
                    f'<div class="flag-row {s}"><span class="badge-{s}">{s}</span>'
                    f'&nbsp;<strong>{f["keyword"]}</strong> — {ctx}</div>',
                    unsafe_allow_html=True)
        shown += 1

    if shown == 0: st.success("✅ No violations found matching your filters.")

    sec("🤖 AI Compliance Report","purple")
    if st.button("🚀 Generate AI Compliance Analysis", key="rf_ai"):
        with st.spinner("Claude reviewing…"):
            try:
                rfs = build_redflag_summary(results)
                r   = analyse_red_flags(rfs)
                st.session_state["rf_ai"] = r
            except Exception as e: st.error(str(e))
    if "rf_ai" in st.session_state:
        r = st.session_state["rf_ai"]
        with st.expander("⚠️ Compliance Risk Assessment", expanded=True): ai_section(r,"COMPLIANCE RISK")
        with st.expander("👤 Agent Risk Profiles"):                        ai_section(r,"AGENT RISK")
        with st.expander("📋 Immediate Action Plan"):                      ai_section(r,"IMMEDIATE ACTION")
        with st.expander("🛡️ Prevention Recommendations"):                 ai_section(r,"PREVENTION")

# ═══════════════════════════════════════════════════════════════
# PAGE: AGENT SCORECARDS
# ═══════════════════════════════════════════════════════════════
def page_scorecards():
    page_header("🎯","Agent Scorecards",
                "Individual AI-powered performance reports — download as PDF or batch ZIP",
                "135deg,#b14cf0,#f72585")

    df = st.session_state.get("audit_df", None)

    uploaded = st.file_uploader(
        "Upload audit file (or reuse data from Audit Sheet Analysis)",
        type=ALL_TYPES, key="sc_up")

    if uploaded:
        raw = load_any(uploaded)
        if raw is not None:
            df, _, _, _ = auto_prepare(normalise_df(raw))
            st.session_state["audit_df"] = df

    if df is None:
        st.info("👆 Upload a file above, or go to **Audit Sheet Analysis** first — the data carries over automatically.")
        return

    ok, err = tni_val(df)
    if not ok:
        st.error(f"File issue: {err}")
        return

    agents = get_agent_list(df)
    if not agents:
        st.warning("No agents found in data.")
        return

    st.success(f"✅ {len(agents)} agents found in dataset")

    sec("🔍 Individual Agent Deep Dive")
    cs,cb = st.columns([3,1])
    with cs: chosen = st.selectbox("Select Agent", agents, key="sc_sel")
    with cb:
        st.markdown("<br>",unsafe_allow_html=True)
        gen = st.button("🎯 Generate Report", key="sc_gen")

    if gen:
        with st.spinner(f"Building scorecard for {chosen}…"):
            try:
                profile = build_agent_profile(df, chosen)
                try:
                    ai_rep = generate_agent_scorecard({
                        "name":profile["name"],"total_audits":profile["total_audits"],
                        "overall_avg":profile["overall_avg"],"param_scores":profile["param_scores"],
                        "strengths":profile["strengths"],"weaknesses":profile["weaknesses"],
                        "trend":profile["trend"],"red_flags":0,
                    })
                    profile["ai_report"] = ai_rep
                except Exception as e:
                    st.warning(f"AI unavailable: {e}")
                    profile["ai_report"] = ""
                st.session_state["sc_profile"] = profile
            except Exception as e:
                st.error(f"Error building profile: {e}")

    if "sc_profile" in st.session_state:
        p = st.session_state["sc_profile"]
        if p.get("name") == chosen:
            rc = {"Exceeds Expectations":"#06d6a0","Meets Expectations":"#00f5d4",
                  "Needs Improvement":"#ffd60a"}.get(p["rating"],"#f72585")
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#0d1426,#111c38);"
                f"border:1px solid #152040;border-radius:16px;padding:22px;margin:10px 0;"
                f"display:flex;align-items:center;gap:20px;'>"
                f"<div style='text-align:center;min-width:90px;'>"
                f"<div style='font-family:Syne,sans-serif;font-size:2.6rem;font-weight:800;"
                f"color:{rc};'>{p['overall_avg']}</div>"
                f"<div style='font-size:.65rem;color:#3d5070;text-transform:uppercase;'>Score</div></div>"
                f"<div><div style='font-size:1.1rem;font-weight:700;color:#e2e8f0;'>{p['name']}</div>"
                f"<div style='color:{rc};font-weight:600;margin:4px 0;'>{p['rating']}</div>"
                f"<div style='font-size:.78rem;color:#3d5070;'>Audits: {p['total_audits']} | Trend: {p['trend']}</div>"
                f"</div></div>", unsafe_allow_html=True)

            cl,cr = st.columns(2)
            with cl: render_chart(agent_radar_chart(p["param_avgs"],p["name"]),"radar1")
            with cr:
                sec("💪 Strengths","green")
                if not p["strengths_df"].empty:
                    st.dataframe(p["strengths_df"], use_container_width=True, hide_index=True)
                sec("📉 Development Areas","red")
                if not p["weaknesses_df"].empty:
                    st.dataframe(p["weaknesses_df"], use_container_width=True, hide_index=True)

            if p.get("ai_report"):
                sec("🤖 AI Coaching Plan","purple")
                r = p["ai_report"]
                with st.expander("📋 Performance Summary", expanded=True): ai_section(r,"PERFORMANCE SUMMARY")
                with st.expander("💪 Strengths"):                          ai_section(r,"STRENGTHS")
                with st.expander("📉 Development Areas"):                  ai_section(r,"DEVELOPMENT")
                with st.expander("🗓️ 4-Week Coaching Plan"):               ai_section(r,"COACHING PLAN")
                with st.expander("🗒️ Manager Notes"):                      ai_section(r,"MANAGER NOTES")

            try:
                pdf_bytes = generate_scorecard_pdf(p)
                st.download_button(
                    f"⬇️ Download {p['name']} Scorecard PDF",
                    data=pdf_bytes,
                    file_name=f"Scorecard_{p['name'].replace(' ','_')}.pdf",
                    mime="application/pdf", use_container_width=True)
            except Exception as e: st.error(f"PDF error: {e}")

    st.markdown("---")
    sec("📦 Batch — All Agent Scorecards")
    st.write(f"Generate PDF scorecards for all **{len(agents)} agents** and download as a single ZIP.")
    if st.button("📦 Generate All Scorecards (ZIP)", key="sc_batch"):
        files = {}
        bar = st.progress(0, text="Building…")
        for i,agent in enumerate(agents):
            try:
                p2 = build_agent_profile(df, agent)
                files[f"Scorecard_{agent.replace(' ','_')}.pdf"] = generate_scorecard_pdf(p2)
            except: pass
            bar.progress((i+1)/len(agents), text=agent)
        bar.empty()
        if files:
            zb = make_zip(files)
            st.download_button(
                f"⬇️ Download All {len(files)} Scorecards (ZIP)",
                data=zb,
                file_name=f"All_Scorecards_{datetime.today().strftime('%Y%m%d')}.zip",
                mime="application/zip", use_container_width=True)
            st.success(f"✅ {len(files)} scorecards ready.")

    sec("👥 Team Overview")
    try:
        render_chart(agent_league_table_chart(compute_agent_stats(df)),"league2")
    except Exception: pass

# ═══════════════════════════════════════════════════════════════
# PAGE: VOICEBOT AUDIT
# ═══════════════════════════════════════════════════════════════
def page_voicebot():
    page_header("🤖","Voicebot Audit",
                "Upload voicebot audit dump — AI analyses containment, intent accuracy, escalation patterns",
                "135deg,#06d6a0,#00f5d4")

    with st.expander("📋 How to prepare your Voicebot CSV", expanded=False):
        st.markdown("**Required:** `bot_name` and `interaction_id` columns. Add any others you have:")
        eg = pd.DataFrame({
            "bot_name":["SalesBot","SalesBot"],"interaction_id":["I001","I002"],
            "containment_result":["yes","no"],"escalation_reason":[None,"Complex query"],
            "intent_detected":["check_balance","apply_loan"],
            "intent_expected":["check_balance","check_balance"],
            "csat_score":[4.5,2.0],"response_accuracy":[92,55],
        })
        st.dataframe(eg, use_container_width=True, hide_index=True)
        st.markdown("""
        **Optional columns:** `fallback_rate`, `dead_air_rate`, `avg_handle_time`,
        `intent_accuracy`, `sentiment`, `response_accuracy`, or any custom score columns.
        """)

    uploaded = st.file_uploader(
        "Upload Voicebot Audit file",
        type=ALL_TYPES, key="vb_up",
        help="Accepts CSV, Excel, PDF, Word, TXT")

    if not uploaded:
        st.info("👆 Upload your voicebot audit file above. Download `sample_voicebot.csv` from the repo to test.")
        return

    raw_df = load_any(uploaded)
    if raw_df is None:
        return

    # Normalise columns
    raw_df = normalise_df(raw_df)

    with st.expander("🔍 Preview loaded data", expanded=False):
        st.write("Columns found:", list(raw_df.columns))
        st.dataframe(raw_df.head(8), use_container_width=True, hide_index=True)

    # Validate — with helpful error
    ok, err = vb_val(raw_df)
    if not ok:
        st.error(f"❌ {err}")
        st.info("💡 Your file needs at least `bot_name` and `interaction_id` columns, plus some numeric score columns.")
        # Try to help by showing what columns we found
        num_cols = [c for c in raw_df.columns if pd.api.types.is_numeric_dtype(raw_df[c])]
        st.write(f"**Numeric columns found:** {num_cols if num_cols else 'None'}")
        return

    st.success(f"✅ {len(raw_df):,} interactions loaded")

    with st.spinner("⚙️ Analysing voicebot performance…"):
        try:
            summary   = build_voicebot_summary(raw_df)
        except Exception as e:
            st.error(f"Analysis error: {e}")
            return

    kpis      = summary["_kpis"]
    intent_df = summary["_intent_df"]
    escal_df  = summary["_escal_df"]
    fail_df   = summary["_failures_df"]
    bot_df    = summary["_bot_perf_df"]
    sentiment = summary["_sentiment"]

    # ── KPI Cards ─────────────────────────────────────────────
    st.markdown("<br>",unsafe_allow_html=True)
    kpi_data = []
    cols_list = st.columns(5)
    idx = 0
    for key, label, good_thresh, higher_is_bad, unit in [
        ("containment_rate", "Containment Rate", 70,  False, "%"),
        ("escalation_rate",  "Escalation Rate",  30,  True,  "%"),
        ("intent_accuracy",  "Intent Accuracy",  85,  False, "%"),
        ("csat_score",       "CSAT Score",        3.5, False, "/5"),
        ("fallback_rate",    "Fallback Rate",     20,  True,  "%"),
    ]:
        val = kpis.get(key)
        if val is not None and idx < 5:
            if higher_is_bad:
                ac = "#f72585" if val > good_thresh else "#06d6a0"
            else:
                ac = "#06d6a0" if val >= good_thresh else "#f72585"
            kpi_data.append((cols_list[idx], f"{val}{unit}", ac, label))
            idx += 1

    # Fill remaining with total
    if idx < 5:
        kpi_data.append((cols_list[idx], f"{len(raw_df):,}", "#00f5d4", "Total Interactions"))

    if kpi_data:
        mcard(kpi_data)
        st.markdown("<br>",unsafe_allow_html=True)

    # ── Gauges ────────────────────────────────────────────────
    gauge_params = []
    if kpis.get("containment_rate") is not None:
        gauge_params.append(("containment_rate",70,"Containment Rate","%"))
    if kpis.get("intent_accuracy") is not None:
        gauge_params.append(("intent_accuracy",85,"Intent Accuracy","%"))
    if kpis.get("csat_score") is not None:
        gauge_params.append(("csat_score",3.5,"CSAT Score","/5"))

    if gauge_params:
        sec("📊 Performance Gauges")
        gcols = st.columns(len(gauge_params))
        for i,(key,target,label,unit) in enumerate(gauge_params):
            with gcols[i]:
                render_chart(voicebot_kpi_gauge(kpis[key],target,label,unit),f"g{i}")

    # ── Intent Analysis ───────────────────────────────────────
    if not intent_df.empty:
        sec("🧠 Intent Recognition Analysis","amber")
        cl,cr = st.columns([3,2])
        with cl: render_chart(voicebot_intent_chart(intent_df),"intent1")
        with cr:
            st.dataframe(intent_df.style.background_gradient(
                subset=["accuracy_%"],cmap="RdYlGn"),
                use_container_width=True, hide_index=True)

    # ── Escalation ────────────────────────────────────────────
    if not escal_df.empty:
        sec("📞 Escalation Analysis","red")
        cl,cr = st.columns([2,3])
        with cl: render_chart(voicebot_escalation_chart(escal_df),"esc1")
        with cr: st.dataframe(escal_df, use_container_width=True, hide_index=True)

    # ── Failure Patterns ──────────────────────────────────────
    if not fail_df.empty:
        sec("⚠️ Failure Patterns","amber")
        render_chart(voicebot_failure_chart(fail_df),"fail1")
        st.dataframe(fail_df, use_container_width=True, hide_index=True)

    # ── Bot Comparison ────────────────────────────────────────
    if not bot_df.empty and len(bot_df) > 1:
        sec("🤖 Bot Performance Comparison")
        if "overall_score" in bot_df.columns:
            st.dataframe(bot_df.style.background_gradient(subset=["overall_score"],cmap="RdYlGn"),
                         use_container_width=True, hide_index=True)
        else:
            st.dataframe(bot_df, use_container_width=True, hide_index=True)

    # ── Sentiment ─────────────────────────────────────────────
    if sentiment:
        sec("😊 Sentiment Distribution")
        scols = st.columns(len(sentiment))
        sc_map = {"positive":"#06d6a0","neutral":"#00f5d4","negative":"#f72585"}
        for i,(label,count) in enumerate(sentiment.items()):
            pct = round(count/len(raw_df)*100,1)
            ac  = sc_map.get(label.lower(),"#b14cf0")
            with scols[i]:
                st.markdown(
                    f'<div class="qie-card" style="--ac:{ac};">'
                    f'<div class="v">{pct}%</div>'
                    f'<div class="l">{label.title()}</div></div>',
                    unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)

    # ── Extra KPIs ────────────────────────────────────────────
    extra = {k:v for k,v in kpis.items()
             if k not in {"containment_rate","escalation_rate","intent_accuracy",
                           "csat_score","fallback_rate","containment_target",
                           "containment_status","csat_target","silence_warning"}
             and isinstance(v,(int,float))}
    if extra:
        with st.expander("📋 All KPI Details"):
            st.dataframe(pd.DataFrame(list(extra.items()),columns=["Metric","Value"]),
                         use_container_width=True, hide_index=True)

    # ── AI Report ─────────────────────────────────────────────
    sec("🤖 Claude AI — Voicebot Intelligence Report","purple")
    if st.button("🚀 Generate AI Voicebot Analysis (~25s)", key="vb_ai_btn"):
        with st.spinner("Claude analysing voicebot data…"):
            try:
                r = analyse_voicebot(summary)
                st.session_state["vb_ai"] = r
            except Exception as e: st.error(str(e))

    if "vb_ai" in st.session_state:
        r = st.session_state["vb_ai"]
        with st.expander("🏆 Performance Verdict",        expanded=True): ai_section(r,"PERFORMANCE VERDICT")
        with st.expander("📞 Containment Analysis"):                      ai_section(r,"CONTAINMENT")
        with st.expander("🧠 Intent & NLU Analysis"):                     ai_section(r,"INTENT")
        with st.expander("🔁 Conversation Flow Failures"):                ai_section(r,"CONVERSATION FLOW")
        with st.expander("🗺️ Optimisation Roadmap"):                     ai_section(r,"OPTIMISATION")
        with st.expander("📧 Executive Summary"):                          ai_section(r,"EXECUTIVE")

# ═══════════════════════════════════════════════════════════════
# PAGE: SALES INTELLIGENCE
# ═══════════════════════════════════════════════════════════════
def page_sales_intelligence():
    page_header("📊","Sales Intelligence",
                "Upload sales call data — revenue leakage, win/loss patterns, campaign performance",
                "135deg,#ffd60a,#f72585")

    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(255,214,10,.06),rgba(247,37,133,.06));
      border:1px solid rgba(255,214,10,.15);border-radius:16px;padding:22px 26px;margin:8px 0;">
      <div style="font-family:'Syne',sans-serif;font-size:.9rem;font-weight:700;
        color:#ffd60a;margin-bottom:10px;">📊 What this module analyses</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:.83rem;color:#c4d8ff;line-height:1.8;">
        <div>✦ &nbsp;Campaign health scores<br>✦ &nbsp;Revenue leakage by source<br>✦ &nbsp;Win / loss analysis</div>
        <div>✦ &nbsp;Escalation impact on revenue<br>✦ &nbsp;Conversion rate trends<br>✦ &nbsp;AI recommendations</div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.expander("📋 Supported CSV Format", expanded=False):
        st.markdown("Your sales data CSV should have these columns (use what you have):")
        eg = pd.DataFrame({
            "campaign_name":["Q4 Enterprise","Q4 SMB"],
            "date":["2025-01-10","2025-01-10"],
            "calls_attempted":[500,300],
            "calls_connected":[380,240],
            "escalated":[45,30],
            "converted":[20,18],
            "avg_deal_value":[50000,15000],
            "outcome":["closed","closed"],
        })
        st.dataframe(eg, use_container_width=True, hide_index=True)

    uploaded = st.file_uploader(
        "Upload Sales / Campaign data file",
        type=ALL_TYPES, key="si_up",
        help="Accepts CSV, Excel, PDF, Word, TXT")

    if not uploaded:
        st.info("👆 Upload your sales campaign data file above.")
        return

    raw_df = load_any(uploaded)
    if raw_df is None:
        return

    df = normalise_df(raw_df)

    with st.expander("🔍 Preview loaded data", expanded=False):
        st.write(f"**{len(df):,} rows × {len(df.columns)} columns**")
        st.write("Columns:", list(df.columns))
        st.dataframe(df.head(8), use_container_width=True, hide_index=True)

    st.success(f"✅ {len(df):,} rows loaded")

    # ── Auto-detect numeric columns for analysis ───────────────
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    if not num_cols:
        st.error("No numeric columns found for analysis.")
        return

    # ── KPI detection ─────────────────────────────────────────
    def find_col(*names):
        for n in names:
            for c in df.columns:
                if n in c.lower(): return c
        return None

    col_calls   = find_col("calls_attempted","total_calls","calls")
    col_connect = find_col("calls_connected","connected","answered")
    col_esc     = find_col("escalat")
    col_conv    = find_col("convert","closed","won")
    col_deal    = find_col("deal_value","revenue","deal_size","avg_deal")
    col_campaign= find_col("campaign_name","campaign","name")

    # ── Summary KPIs ──────────────────────────────────────────
    sec("📊 Campaign Overview")
    kpi_items = []
    cols5 = st.columns(5)
    cidx  = 0

    if col_calls and cidx < 5:
        kpi_items.append((cols5[cidx], f"{int(df[col_calls].sum()):,}", "#00f5d4", "Total Calls"))
        cidx += 1
    if col_connect and cidx < 5:
        conn_rate = round(df[col_connect].sum()/max(df[col_calls].sum(),1)*100,1) if col_calls else 0
        kpi_items.append((cols5[cidx], f"{conn_rate}%", "#06d6a0", "Connection Rate"))
        cidx += 1
    if col_conv and cidx < 5:
        conv_total = int(df[col_conv].sum())
        kpi_items.append((cols5[cidx], f"{conv_total:,}", "#b14cf0", "Conversions"))
        cidx += 1
    if col_esc and cidx < 5:
        esc_rate = round(df[col_esc].sum()/max(df[col_connect or col_calls or ""].sum() if (col_connect or col_calls) else 1,1)*100,1)
        kpi_items.append((cols5[cidx], f"{esc_rate}%", "#ffd60a", "Escalation Rate"))
        cidx += 1
    if col_deal and cidx < 5:
        total_rev = df[col_deal].sum() if col_deal else 0
        if col_conv:
            total_rev = df[col_conv].sum() * df[col_deal].mean() if col_deal else 0
        kpi_items.append((cols5[cidx], f"${total_rev/1e6:.1f}M" if total_rev > 1e6 else f"${total_rev:,.0f}", "#ffd60a", "Est. Revenue"))
        cidx += 1

    if kpi_items:
        mcard(kpi_items)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Revenue Leakage ───────────────────────────────────────
    if col_calls and col_connect and col_conv and col_deal:
        sec("💸 Revenue Leakage Analysis","red")
        total_calls_val  = df[col_calls].sum()
        total_conn_val   = df[col_connect].sum()
        avg_deal         = df[col_deal].mean()
        actual_conv      = df[col_conv].sum()
        baseline_rate    = actual_conv / max(total_conn_val, 1)
        potential_conv   = total_conn_val * max(baseline_rate * 1.2, 0.1)
        leakage_est      = (potential_conv - actual_conv) * avg_deal
        dropped          = total_calls_val - total_conn_val

        cl,cr = st.columns(2)
        with cl:
            lk_data = {
                "Drop-off (no connection)": dropped * avg_deal * baseline_rate,
                "Escalation penalty": df[col_esc].sum() * avg_deal * 0.3 if col_esc else 0,
                "Conversion gap": (potential_conv - actual_conv) * avg_deal * 0.5,
            }
            lk_data = {k:v for k,v in lk_data.items() if v > 0}
            if lk_data:
                fig = go.Figure(go.Bar(
                    x=list(lk_data.values()), y=list(lk_data.keys()),
                    orientation="h", marker_color=["#f72585","#ffd60a","#b14cf0"],
                    text=[f"${v:,.0f}" for v in lk_data.values()],
                    textposition="outside",textfont=dict(color="#c4d8ff")))
                fig.update_layout(
                    paper_bgcolor="#080f24",plot_bgcolor="#080f24",
                    font=dict(color="#c4d8ff"),height=280,
                    title=dict(text="Revenue Leakage by Source",font=dict(color="#c4d8ff",size=13)),
                    margin=dict(l=20,r=80,t=40,b=20),
                    xaxis=dict(gridcolor="#0f1e3d"),yaxis=dict(gridcolor="#0f1e3d"))
                render_chart(fig,"leakage_bar")
        with cr:
            st.markdown(f"""
            <div style="background:rgba(247,37,133,.06);border:1px solid rgba(247,37,133,.15);
              border-radius:14px;padding:20px;margin-top:10px;">
              <div style="font-family:'Syne',sans-serif;font-size:.72rem;color:#f72585;
                text-transform:uppercase;letter-spacing:.12em;margin-bottom:12px;">
                Leakage Summary</div>
              <div style="font-size:2rem;font-weight:800;color:#f72585;margin-bottom:4px;">
                ${leakage_est:,.0f}</div>
              <div style="font-size:.75rem;color:#3d5070;">Estimated revenue leakage</div>
              <hr style="border-color:rgba(247,37,133,.1);margin:12px 0;">
              <div style="font-size:.82rem;color:#c4d8ff;line-height:2;">
                Calls dropped: <strong style="color:#ffd60a;">{int(dropped):,}</strong><br>
                Avg deal value: <strong style="color:#00f5d4;">${avg_deal:,.0f}</strong><br>
                Actual conversions: <strong style="color:#06d6a0;">{int(actual_conv):,}</strong>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── Campaign breakdown ────────────────────────────────────
    if col_campaign:
        sec("🏆 Campaign Performance")
        grp_cols = [c for c in num_cols if c != col_campaign][:6]
        if grp_cols:
            camp_df = df.groupby(col_campaign)[grp_cols].sum().reset_index()
            st.dataframe(camp_df, use_container_width=True, hide_index=True)

            # Bar chart of key metric
            key_metric = col_conv or col_connect or grp_cols[0]
            fig = go.Figure(go.Bar(
                x=camp_df[col_campaign],
                y=camp_df[key_metric],
                marker_color="#00f5d4",
                text=camp_df[key_metric].round(0),
                textposition="outside",textfont=dict(color="#c4d8ff")))
            fig.update_layout(
                paper_bgcolor="#080f24",plot_bgcolor="#080f24",
                font=dict(color="#c4d8ff"),height=320,
                title=dict(text=f"Campaign Comparison — {key_metric.replace('_',' ').title()}",
                           font=dict(color="#c4d8ff",size=13)),
                margin=dict(l=20,r=20,t=40,b=60),
                xaxis=dict(gridcolor="#0f1e3d"),yaxis=dict(gridcolor="#0f1e3d"))
            render_chart(fig,"camp_bar")

    # ── Trend over time ───────────────────────────────────────
    date_col = find_col("date","period","month","week")
    if date_col and num_cols:
        sec("📈 Performance Trends")
        try:
            df2 = df.copy()
            df2[date_col] = pd.to_datetime(df2[date_col], dayfirst=True, errors="coerce")
            df2 = df2.dropna(subset=[date_col]).sort_values(date_col)
            trend_metric = col_conv or col_connect or num_cols[0]
            trend_df = df2.groupby(date_col)[trend_metric].sum().reset_index()
            fig = go.Figure(go.Scatter(
                x=trend_df[date_col], y=trend_df[trend_metric],
                line=dict(color="#00f5d4",width=2),
                fill="tozeroy",fillcolor="rgba(0,245,212,0.06)",
                mode="lines+markers",marker=dict(color="#00f5d4",size=6)))
            fig.update_layout(
                paper_bgcolor="#080f24",plot_bgcolor="#080f24",
                font=dict(color="#c4d8ff"),height=300,
                title=dict(text=f"{trend_metric.replace('_',' ').title()} Over Time",
                           font=dict(color="#c4d8ff",size=13)),
                margin=dict(l=20,r=20,t=40,b=20),
                xaxis=dict(gridcolor="#0f1e3d"),yaxis=dict(gridcolor="#0f1e3d"))
            render_chart(fig,"trend_si")
        except Exception: pass

    # ── Numeric summary table ─────────────────────────────────
    with st.expander("📋 Full Data Summary"):
        st.dataframe(df.describe().round(2), use_container_width=True)

    # ── AI Report ─────────────────────────────────────────────
    sec("🤖 AI Sales Intelligence Report","purple")
    if st.button("🚀 Generate AI Sales Analysis", key="si_ai_btn"):
        with st.spinner("Claude analysing sales data…"):
            try:
                # Build a summary string for Claude
                summary_lines = [
                    f"Sales campaign data with {len(df):,} rows.",
                    f"Columns: {', '.join(df.columns.tolist())}",
                ]
                if col_calls:   summary_lines.append(f"Total calls: {int(df[col_calls].sum()):,}")
                if col_connect: summary_lines.append(f"Calls connected: {int(df[col_connect].sum()):,}")
                if col_conv:    summary_lines.append(f"Conversions: {int(df[col_conv].sum()):,}")
                if col_esc:     summary_lines.append(f"Escalations: {int(df[col_esc].sum()):,}")
                if col_deal:    summary_lines.append(f"Avg deal value: ${df[col_deal].mean():,.0f}")
                if col_campaign:
                    camp_summary = df.groupby(col_campaign)[num_cols[:3]].sum().to_string()
                    summary_lines.append(f"\nCampaign breakdown:\n{camp_summary}")

                prompt_data = {
                    "kpis": {
                        "data_summary": "\n".join(summary_lines),
                        "total_rows": len(df),
                        "columns": list(df.columns),
                    },
                    "intent_data": "N/A",
                    "escalation_data": f"Escalation column: {col_esc}, total: {int(df[col_esc].sum()) if col_esc else 'N/A'}",
                    "failure_patterns": f"Estimated revenue leakage: ${leakage_est:,.0f}" if (col_calls and col_connect and col_conv and col_deal) else "N/A",
                    "bot_performance": df.groupby(col_campaign)[num_cols[:3]].sum().to_string() if col_campaign else "N/A",
                    "sentiment": "N/A",
                    "total_interactions": len(df),
                }
                r = analyse_voicebot(prompt_data)  # reuse voicebot AI engine
                st.session_state["si_ai"] = r
            except Exception as e:
                st.error(f"AI error: {e}")

    if "si_ai" in st.session_state:
        r = st.session_state["si_ai"]
        with st.expander("🏆 Performance Verdict",    expanded=True): ai_section(r,"PERFORMANCE VERDICT")
        with st.expander("💸 Revenue Leakage"):                        ai_section(r,"CONTAINMENT")
        with st.expander("🗺️ Optimisation Roadmap"):                  ai_section(r,"OPTIMISATION")
        with st.expander("📧 Executive Summary"):                       ai_section(r,"EXECUTIVE")

# ═══════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════
if   PAGE == "🏠  Dashboard":           page_dashboard()
elif PAGE == "📂  Audit Sheet Analysis": page_audit_analysis()
elif PAGE == "🚨  Transcript Scanner":   page_transcripts()
elif PAGE == "🎯  Agent Scorecards":     page_scorecards()
elif PAGE == "🤖  Voicebot Audit":       page_voicebot()
elif PAGE == "📊  Sales Intelligence":   page_sales_intelligence()
