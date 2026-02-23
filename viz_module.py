# ============================================================
# viz_module.py  —  Quality Intelligence Engine v3
# All charts and visualisations using Plotly + Streamlit.
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ── Theme colours — Neon Noir Premium ─────────────────────────────────────────
BG       = "#04070f"
BG_CARD  = "#080f24"
BLUE     = "#00f5d4"
GREEN    = "#06d6a0"
AMBER    = "#ffd60a"
RED      = "#f72585"
PURPLE   = "#b14cf0"
TEXT     = "#c4d8ff"
GRID     = "#0f1e3d"

LAYOUT_BASE = dict(
    paper_bgcolor=BG_CARD,
    plot_bgcolor=BG_CARD,
    font=dict(family="DM Sans, sans-serif", color=TEXT, size=12),
    margin=dict(l=20, r=20, t=44, b=20),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
)


def score_bar_chart(df: pd.DataFrame, title: str = "Parameter Scores") -> go.Figure:
    """
    Horizontal bar chart of parameter average scores.
    Coloured by performance: red < 60, amber 60-70, green > 70.
    """
    cols = [c for c in df.columns
            if pd.api.types.is_numeric_dtype(df[c])
            and c not in {"agent_name","auditor_name","audit_date","call_id"}
            and not c.startswith("master_")]
    if not cols:
        return go.Figure()

    means = df[cols].mean().sort_values()
    colors = [RED if v < 60 else AMBER if v < 70 else GREEN for v in means.values]

    fig = go.Figure(go.Bar(
        x=means.values,
        y=[c.replace("_", " ").title() for c in means.index],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}" for v in means.values],
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
    ))
    fig.add_vline(x=70, line_dash="dot", line_color=AMBER,
                  annotation_text="Target 70", annotation_font_color=AMBER)
    fig.update_layout(**LAYOUT_BASE, title=dict(text=title, font=dict(color=TEXT, size=14)),
                      height=max(300, len(cols) * 40))
    return fig


def agent_radar_chart(param_avgs: pd.Series, agent_name: str) -> go.Figure:
    """Radar / spider chart for one agent's parameter scores."""
    if param_avgs.empty:
        return go.Figure()

    categories = [c.replace("_", " ").title() for c in param_avgs.index]
    values     = param_avgs.values.tolist()
    values    += [values[0]]  # close the loop
    categories += [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories,
        fill="toself",
        fillcolor=f"rgba(59,130,246,0.2)",
        line=dict(color=BLUE, width=2),
        name=agent_name,
    ))
    fig.add_trace(go.Scatterpolar(
        r=[70] * len(categories), theta=categories,
        line=dict(color=AMBER, width=1, dash="dot"),
        name="Target (70)",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=BG_CARD,
            radialaxis=dict(visible=True, range=[0, 100], color=TEXT,
                            gridcolor=GRID, tickfont=dict(color=TEXT, size=9)),
            angularaxis=dict(color=TEXT, gridcolor=GRID),
        ),
        paper_bgcolor=BG_CARD,
        font=dict(color=TEXT),
        legend=dict(font=dict(color=TEXT)),
        title=dict(text=f"{agent_name} — Performance Radar",
                   font=dict(color=TEXT, size=13)),
        height=380,
        margin=dict(l=40, r=40, t=50, b=20),
    )
    return fig


def trend_line_chart(df: pd.DataFrame, score_cols: list) -> go.Figure:
    """Line chart showing score trend over time."""
    if "audit_date" not in df.columns or not score_cols:
        return go.Figure()
    try:
        df = df.copy()
        df["audit_date"] = pd.to_datetime(df["audit_date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["audit_date"]).sort_values("audit_date")
        grouped = df.groupby("audit_date")[score_cols].mean().reset_index()
    except Exception:
        return go.Figure()

    fig = go.Figure()
    palette = [BLUE, GREEN, AMBER, RED, PURPLE, "#06b6d4", "#f43f5e", "#84cc16"]
    for i, col in enumerate(score_cols[:8]):
        fig.add_trace(go.Scatter(
            x=grouped["audit_date"], y=grouped[col],
            name=col.replace("_", " ").title(),
            line=dict(color=palette[i % len(palette)], width=2),
            mode="lines+markers",
        ))
    fig.add_hline(y=70, line_dash="dot", line_color=AMBER)
    fig.update_layout(**LAYOUT_BASE,
                      title=dict(text="Score Trends Over Time", font=dict(color=TEXT, size=14)),
                      height=350,
                      legend=dict(font=dict(color=TEXT), bgcolor=BG_CARD))
    return fig


def agent_league_table_chart(agent_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart ranking all agents by overall score."""
    if agent_df.empty or "overall_avg" not in agent_df.columns:
        return go.Figure()

    df = agent_df.sort_values("overall_avg")
    colors = [RED if v < 55 else AMBER if v < 70 else GREEN for v in df["overall_avg"]]

    fig = go.Figure(go.Bar(
        x=df["overall_avg"],
        y=df["agent_name"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}" for v in df["overall_avg"]],
        textposition="outside",
        textfont=dict(color=TEXT),
    ))
    fig.add_vline(x=70, line_dash="dot", line_color=AMBER)
    layout3 = dict(**LAYOUT_BASE)
    layout3["xaxis"] = dict(range=[0, 105], gridcolor=GRID)
    fig.update_layout(**layout3,
                      title=dict(text="Agent League Table", font=dict(color=TEXT, size=14)),
                      height=max(300, len(df) * 38))
    return fig


def variance_heatmap(variance_df: pd.DataFrame) -> go.Figure:
    """Bar chart of parameter variance levels."""
    if variance_df.empty:
        return go.Figure()

    df = variance_df.sort_values("variance_%", ascending=False)
    colors = [RED if v > 20 else AMBER if v > 15 else GREEN for v in df["variance_%"]]

    fig = go.Figure(go.Bar(
        x=[c.replace("_"," ").title() for c in df["parameter"]],
        y=df["variance_%"],
        marker_color=colors,
        text=[f"{v:.1f}%" for v in df["variance_%"]],
        textposition="outside",
        textfont=dict(color=TEXT),
    ))
    fig.add_hline(y=15, line_dash="dot", line_color=AMBER,
                  annotation_text="Threshold 15%", annotation_font_color=AMBER)
    fig.update_layout(**LAYOUT_BASE,
                      title=dict(text="Parameter Variance by Auditor", font=dict(color=TEXT, size=14)),
                      height=340)
    return fig


def auditor_accuracy_chart(accuracy_df: pd.DataFrame) -> go.Figure:
    """Bar chart of auditor accuracy scores."""
    if accuracy_df.empty:
        return go.Figure()

    df = accuracy_df.sort_values("accuracy_%")
    colors = [RED if v < 75 else AMBER if v < 85 else GREEN for v in df["accuracy_%"]]

    fig = go.Figure(go.Bar(
        x=df["accuracy_%"],
        y=df["auditor_name"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in df["accuracy_%"]],
        textposition="outside",
        textfont=dict(color=TEXT),
    ))
    fig.add_vline(x=85, line_dash="dot", line_color=AMBER,
                  annotation_text="Target 85%", annotation_font_color=AMBER)
    layout2 = dict(**LAYOUT_BASE)
    layout2["xaxis"] = dict(range=[0, 110], gridcolor=GRID)
    fig.update_layout(**layout2,
                      title=dict(text="Auditor Accuracy vs Master", font=dict(color=TEXT, size=14)),
                      height=max(280, len(df) * 45))
    return fig


def flag_severity_donut(high: int, medium: int, low: int) -> go.Figure:
    """Donut chart showing flag severity distribution."""
    if high + medium + low == 0:
        return go.Figure()

    fig = go.Figure(go.Pie(
        labels=["HIGH", "MEDIUM", "LOW"],
        values=[high, medium, low],
        hole=0.6,
        marker_colors=[RED, AMBER, GREEN],
        textfont=dict(color="white", size=12),
        hovertemplate="%{label}: %{value} flags<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=BG_CARD,
        font=dict(color=TEXT),
        legend=dict(font=dict(color=TEXT), bgcolor=BG_CARD),
        title=dict(text="Violation Severity", font=dict(color=TEXT, size=14)),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        annotations=[dict(text=f"{high+medium+low}<br>flags",
                          x=0.5, y=0.5, font_size=16,
                          font_color=TEXT, showarrow=False)]
    )
    return fig


def render_chart(fig: go.Figure, key: str = None):
    """Render a plotly chart in Streamlit with dark styling."""
    if fig and fig.data:
        st.plotly_chart(fig, use_container_width=True, key=key,
                        config={"displayModeBar": False})


# ── Voicebot Charts ───────────────────────────────────────────────────────────

def voicebot_kpi_gauge(value: float, target: float, title: str, unit: str = "%") -> go.Figure:
    """Gauge chart for a single KPI vs target."""
    color = GREEN if value >= target else (AMBER if value >= target * 0.8 else RED)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={"reference": target, "valueformat": ".1f",
               "increasing": {"color": GREEN}, "decreasing": {"color": RED}},
        number={"suffix": unit, "font": {"color": TEXT, "size": 28}},
        gauge={
            "axis": {"range": [0, 100 if unit == "%" else target * 1.5],
                     "tickcolor": TEXT, "tickfont": {"color": TEXT}},
            "bar":  {"color": color},
            "bgcolor": BG_CARD,
            "bordercolor": GRID,
            "steps": [
                {"range": [0, target * 0.8],        "color": "#1a0a0a"},
                {"range": [target * 0.8, target],    "color": "#1a1500"},
                {"range": [target, 100 if unit == "%" else target * 1.5], "color": "#0a1a0a"},
            ],
            "threshold": {"line": {"color": AMBER, "width": 2}, "value": target},
        },
        title={"text": title, "font": {"color": TEXT, "size": 13}},
    ))
    fig.update_layout(paper_bgcolor=BG_CARD, font=dict(color=TEXT),
                      height=220, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def voicebot_intent_chart(intent_df) -> go.Figure:
    """Bar chart of intent accuracy by intent type."""
    if intent_df.empty:
        return go.Figure()
    df = intent_df.sort_values("accuracy_%")
    colors = [RED if v < 70 else AMBER if v < 85 else GREEN for v in df["accuracy_%"]]
    fig = go.Figure(go.Bar(
        x=df["accuracy_%"], y=df["intent"],
        orientation="h", marker_color=colors,
        text=[f"{v:.1f}%" for v in df["accuracy_%"]],
        textposition="outside", textfont=dict(color=TEXT),
    ))
    fig.add_vline(x=85, line_dash="dot", line_color=AMBER,
                  annotation_text="Target 85%", annotation_font_color=AMBER)
    layout = dict(**LAYOUT_BASE)
    layout["xaxis"] = dict(range=[0, 115], gridcolor=GRID)
    fig.update_layout(**layout,
                      title=dict(text="Intent Recognition Accuracy", font=dict(color=TEXT, size=14)),
                      height=max(280, len(df) * 38))
    return fig


def voicebot_escalation_chart(escal_df) -> go.Figure:
    """Pie chart of escalation reasons."""
    if escal_df.empty:
        return go.Figure()
    palette = [RED, AMBER, PURPLE, BLUE, GREEN, "#06b6d4", "#f43f5e"]
    fig = go.Figure(go.Pie(
        labels=escal_df["escalation_reason"],
        values=escal_df["count"],
        hole=0.5,
        marker_colors=palette[:len(escal_df)],
        textfont=dict(color="white", size=11),
    ))
    fig.update_layout(
        paper_bgcolor=BG_CARD, font=dict(color=TEXT),
        title=dict(text="Escalation Reasons", font=dict(color=TEXT, size=14)),
        legend=dict(font=dict(color=TEXT), bgcolor=BG_CARD),
        height=320, margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def voicebot_failure_chart(failures_df) -> go.Figure:
    """Bar chart of failure rates by parameter."""
    if failures_df.empty:
        return go.Figure()
    df = failures_df.sort_values("fail_rate_%", ascending=False).head(10)
    colors = [RED if s == "HIGH" else AMBER if s == "MEDIUM" else GREEN
              for s in df["severity"]]
    fig = go.Figure(go.Bar(
        x=df["parameter"], y=df["fail_rate_%"],
        marker_color=colors,
        text=[f"{v:.1f}%" for v in df["fail_rate_%"]],
        textposition="outside", textfont=dict(color=TEXT),
    ))
    fig.add_hline(y=25, line_dash="dot", line_color=AMBER)
    fig.update_layout(**LAYOUT_BASE,
                      title=dict(text="Failure Rate by Parameter", font=dict(color=TEXT, size=14)),
                      height=340)
    return fig

