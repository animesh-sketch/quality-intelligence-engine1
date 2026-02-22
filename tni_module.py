# ============================================================
# tni_module.py  —  Quality Intelligence Engine
# Training Needs Identification logic.
# Detects weak parameters, recurring failures, and trends.
# ============================================================

import pandas as pd
import numpy as np
from typing import Tuple

# Parameters that must be present in the CSV (minimum required)
REQUIRED_COLUMNS = ["agent_name", "audit_date"]
SCORE_THRESHOLD = 70        # below this = weak
RECURRENCE_MIN  = 3         # 3+ occurrences = recurring weakness
VARIANCE_WARN   = 10        # flag parameters with high score variance too


def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Check the uploaded CSV has the minimum required columns.
    Returns (is_valid, error_message).
    """
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"

    # Need at least one numeric score column beyond identifiers
    score_cols = _get_score_columns(df)
    if len(score_cols) == 0:
        return False, (
            "No numeric score columns found. "
            "Add columns like 'greeting', 'empathy', 'closing' with numeric scores."
        )
    return True, ""


def _get_score_columns(df: pd.DataFrame) -> list:
    """Return all numeric columns that are NOT identifier/date columns."""
    exclude = {"agent_name", "auditor_name", "audit_date", "call_id",
               "month", "week", "team", "supervisor"}
    return [
        c for c in df.columns
        if c.lower() not in exclude and pd.api.types.is_numeric_dtype(df[c])
    ]


def compute_weak_parameters(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each score parameter, compute the mean score across all agents.
    Return parameters where mean < SCORE_THRESHOLD, sorted worst-first.
    """
    score_cols = _get_score_columns(df)
    means = df[score_cols].mean().reset_index()
    means.columns = ["parameter", "avg_score"]
    weak = means[means["avg_score"] < SCORE_THRESHOLD].sort_values("avg_score")
    weak["avg_score"] = weak["avg_score"].round(2)
    return weak


def compute_recurring_weaknesses(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each agent × parameter, count how many times the score was < threshold.
    Return cases where that count >= RECURRENCE_MIN.
    """
    score_cols = _get_score_columns(df)
    rows = []
    for col in score_cols:
        if col not in df.columns:
            continue
        col_data = df[["agent_name", col]].copy()
        col_data["is_weak"] = col_data[col] < SCORE_THRESHOLD
        counts = (
            col_data.groupby("agent_name")["is_weak"]
            .sum()
            .reset_index()
            .rename(columns={"is_weak": "weak_count"})
        )
        counts["parameter"] = col
        counts = counts[counts["weak_count"] >= RECURRENCE_MIN]
        rows.append(counts)

    if not rows:
        return pd.DataFrame(columns=["agent_name", "parameter", "weak_count"])

    result = pd.concat(rows, ignore_index=True)
    return result.sort_values(["weak_count", "agent_name"], ascending=[False, True])


def compute_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort by audit_date and compute rolling mean of all score columns.
    Returns a summary of direction (improving / declining / stable).
    """
    score_cols = _get_score_columns(df)

    try:
        df = df.copy()
        df["audit_date"] = pd.to_datetime(df["audit_date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["audit_date"]).sort_values("audit_date")
    except Exception:
        return pd.DataFrame(columns=["parameter", "trend", "first_avg", "last_avg", "change"])

    if len(df) < 2:
        return pd.DataFrame(columns=["parameter", "trend", "first_avg", "last_avg", "change"])

    midpoint = len(df) // 2
    first_half = df.iloc[:midpoint][score_cols].mean()
    last_half  = df.iloc[midpoint:][score_cols].mean()

    trend_rows = []
    for col in score_cols:
        diff = last_half[col] - first_half[col]
        if diff > 2:
            direction = "📈 Improving"
        elif diff < -2:
            direction = "📉 Declining"
        else:
            direction = "➡️ Stable"
        trend_rows.append({
            "parameter":  col,
            "trend":      direction,
            "first_avg":  round(first_half[col], 2),
            "last_avg":   round(last_half[col], 2),
            "change":     round(diff, 2),
        })

    return pd.DataFrame(trend_rows).sort_values("change")


def compute_agent_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-agent average score across all parameters."""
    score_cols = _get_score_columns(df)
    stats = df.groupby("agent_name")[score_cols].mean()
    stats["overall_avg"] = stats.mean(axis=1).round(2)
    stats = stats.reset_index().sort_values("overall_avg")
    return stats


def build_tni_summary(df: pd.DataFrame) -> dict:
    """
    Orchestrate all TNI computations and package them into a dict
    ready to be sent to the AI engine.
    """
    weak     = compute_weak_parameters(df)
    recur    = compute_recurring_weaknesses(df)
    trend    = compute_trend(df)
    agent_st = compute_agent_stats(df)
    score_cols = _get_score_columns(df)

    param_averages = (
        df[score_cols].mean().round(2).to_string()
        if score_cols else "No score columns"
    )

    return {
        "weak_params":    weak.to_string(index=False)   if not weak.empty    else "None",
        "recurring":      recur.to_string(index=False)  if not recur.empty   else "None",
        "trend_data":     trend.to_string(index=False)  if not trend.empty   else "Not available",
        "agent_stats":    agent_st.to_string(index=False),
        "param_averages": param_averages,
        # Also return raw dataframes for UI charts
        "_weak_df":       weak,
        "_recur_df":      recur,
        "_trend_df":      trend,
        "_agent_df":      agent_st,
    }
