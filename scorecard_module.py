# ============================================================
# scorecard_module.py  --  Individual Agent Scorecard Engine
# Builds per-agent profiles from TNI CSV data.
# ============================================================

import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
import io

EXCLUDE_COLS = {"agent_name", "auditor_name", "audit_date", "call_id",
                "month", "week", "team", "supervisor", "date"}


def _score_cols(df: pd.DataFrame) -> list:
    return [c for c in df.columns
            if c.lower() not in EXCLUDE_COLS
            and pd.api.types.is_numeric_dtype(df[c])]


def get_agent_list(df: pd.DataFrame) -> list:
    return sorted(df["agent_name"].dropna().unique().tolist())


def build_agent_profile(df: pd.DataFrame, agent_name: str, ai_report: str = "") -> dict:
    """
    Build a full profile dict for one agent.
    """
    agent_df = df[df["agent_name"] == agent_name].copy()
    cols     = _score_cols(df)

    if agent_df.empty:
        return {}

    param_avgs    = agent_df[cols].mean().round(2)
    overall_avg   = round(param_avgs.mean(), 2)
    strengths     = param_avgs.nlargest(3).reset_index()
    strengths.columns = ["parameter", "score"]
    weaknesses    = param_avgs.nsmallest(3).reset_index()
    weaknesses.columns = ["parameter", "score"]

    # Trend
    trend_str = "Not available"
    if "audit_date" in agent_df.columns and len(agent_df) >= 2:
        try:
            agent_df["audit_date"] = pd.to_datetime(
                agent_df["audit_date"], dayfirst=True, errors="coerce"
            )
            agent_df = agent_df.dropna(subset=["audit_date"]).sort_values("audit_date")
            mid = len(agent_df) // 2
            f   = agent_df.iloc[:mid][cols].mean().mean()
            l   = agent_df.iloc[mid:][cols].mean().mean()
            diff = l - f
            trend_str = (
                f"Improving (+{diff:.1f} pts)" if diff > 2
                else f"Declining ({diff:.1f} pts)" if diff < -2
                else "Stable"
            )
        except Exception:
            pass

    # Rating
    if overall_avg >= 85:
        rating = "Exceeds Expectations"
        rating_color = (16, 185, 129)
    elif overall_avg >= 70:
        rating = "Meets Expectations"
        rating_color = (59, 130, 246)
    elif overall_avg >= 55:
        rating = "Needs Improvement"
        rating_color = (245, 158, 11)
    else:
        rating = "Critical -- Immediate Action Required"
        rating_color = (239, 68, 68)

    return {
        "name":          agent_name,
        "total_audits":  len(agent_df),
        "overall_avg":   overall_avg,
        "param_scores":  param_avgs.to_string(),
        "strengths":     strengths.to_string(index=False),
        "weaknesses":    weaknesses.to_string(index=False),
        "trend":         trend_str,
        "rating":        rating,
        "rating_color":  rating_color,
        "param_avgs":    param_avgs,
        "strengths_df":  strengths,
        "weaknesses_df": weaknesses,
        "red_flags":     0,  # can be set externally
        "ai_report":     ai_report,
    }


def generate_scorecard_pdf(profile: dict) -> bytes:
    """
    Generate a professional A4 PDF scorecard for one agent.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    name         = profile.get("name", "Unknown")
    overall_avg  = profile.get("overall_avg", 0)
    rating       = profile.get("rating", "N/A")
    rating_color = profile.get("rating_color", (100, 100, 100))
    total_audits = profile.get("total_audits", 0)
    trend        = profile.get("trend", "N/A")
    strengths_df = profile.get("strengths_df", pd.DataFrame())
    weaknesses_df= profile.get("weaknesses_df", pd.DataFrame())
    ai_report    = profile.get("ai_report", "")
    param_avgs   = profile.get("param_avgs", pd.Series(dtype=float))

    # ── Header band ───────────────────────────────────────────────────────────
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, 210, 38, "F")
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(8)
    pdf.cell(0, 8, "AGENT PERFORMANCE SCORECARD", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 6, f"Quality Intelligence Engine   |   Generated {datetime.today().strftime('%d %B %Y')}", align="C", ln=True)
    pdf.cell(0, 6, f"Agent: {name}   |   Total Audits: {total_audits}   |   Trend: {trend}", align="C", ln=True)
    pdf.ln(16)

    # ── Overall score box ─────────────────────────────────────────────────────
    pdf.set_fill_color(*rating_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(60, 20, str(overall_avg), border=0, align="C", fill=True)
    pdf.set_font("Helvetica", "B", 11)
    x_after = pdf.get_x()
    y_after = pdf.get_y()
    pdf.set_fill_color(30, 41, 59)
    pdf.cell(130, 20, f"  {rating}", border=0, align="L", fill=True)
    pdf.ln(24)
    pdf.set_text_color(0, 0, 0)

    # ── Parameter scores table ────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(30, 64, 175)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(95, 8, "  PARAMETER", border=1, fill=True)
    pdf.cell(50, 8, "SCORE", border=1, align="C", fill=True)
    pdf.cell(45, 8, "STATUS", border=1, align="C", fill=True)
    pdf.ln()

    alt = False
    for param, score in param_avgs.items():
        pdf.set_fill_color(245, 247, 255) if alt else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(95, 7, f"  {str(param).title().replace('_', ' ')}", border=1, fill=True)

        if score >= 85:
            score_color = (16, 185, 129)
            status = "Excellent"
        elif score >= 70:
            score_color = (59, 130, 246)
            status = "Satisfactory"
        elif score >= 55:
            score_color = (245, 158, 11)
            status = "Below Target"
        else:
            score_color = (239, 68, 68)
            status = "Critical"

        pdf.set_fill_color(*score_color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(50, 7, str(round(score, 1)), border=1, align="C", fill=True)
        pdf.set_fill_color(245, 247, 255) if alt else pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(45, 7, status, border=1, align="C", fill=True)
        pdf.ln()
        alt = not alt

    pdf.ln(6)

    # ── Strengths ─────────────────────────────────────────────────────────────
    pdf.set_fill_color(5, 46, 22)
    pdf.set_text_color(74, 222, 128)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(93, 8, "  TOP STRENGTHS", border=1, fill=True)
    pdf.set_fill_color(74, 4, 78)
    pdf.set_text_color(216, 180, 254)
    pdf.cell(97, 8, "  DEVELOPMENT AREAS", border=1, fill=True)
    pdf.ln()

    max_rows = max(len(strengths_df), len(weaknesses_df))
    for i in range(max_rows):
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 9)

        # Strength cell
        if i < len(strengths_df):
            row = strengths_df.iloc[i]
            pdf.set_fill_color(240, 253, 244)
            pdf.cell(93, 7, f"  {str(row['parameter']).title().replace('_',' ')} -- {row['score']}", border=1, fill=True)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(93, 7, "", border=1, fill=True)

        # Weakness cell
        if i < len(weaknesses_df):
            row = weaknesses_df.iloc[i]
            pdf.set_fill_color(253, 244, 255)
            pdf.cell(97, 7, f"  {str(row['parameter']).title().replace('_',' ')} -- {row['score']}", border=1, fill=True)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(97, 7, "", border=1, fill=True)
        pdf.ln()

    pdf.ln(6)

    # ── AI Coaching Plan ──────────────────────────────────────────────────────
    if ai_report:
        pdf.set_fill_color(15, 23, 42)
        pdf.set_text_color(147, 197, 253)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, "  AI-GENERATED COACHING PLAN & RECOMMENDATIONS", border=1, fill=True, ln=True)

        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(30, 30, 30)
        # Strip markdown and sanitize for PDF
        import re
        clean = re.sub(r"#+\s*", "", ai_report)
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", clean)
        clean = re.sub(r"\*(.*?)\*",     r"\1", clean)
        # Remove non-latin chars
        clean = clean.encode("latin-1", errors="replace").decode("latin-1")
        pdf.set_fill_color(248, 250, 252)
        pdf.multi_cell(0, 5.5, clean[:3000], border=1, fill=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.set_y(-14)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6,
             "Confidential -- Quality Intelligence Engine | For internal use only",
             align="C")

    return pdf.output()
