# ============================================================
# tni_module.py  —  Training Needs Identification logic
# ============================================================

import pandas as pd
import numpy as np
from typing import Tuple

SCORE_THRESHOLD = 70
RECURRENCE_MIN  = 3

EXCLUDE_COLS = {"agent_name", "auditor_name", "audit_date", "call_id",
                "month", "week", "team", "supervisor", "date"}


def _score_cols(df: pd.DataFrame) -> list:
    return [c for c in df.columns
            if c.lower() not in EXCLUDE_COLS
            and pd.api.types.is_numeric_dtype(df[c])]


def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    if "agent_name" not in df.columns:
        return False, "Missing 'agent_name' column."
    if len(_score_cols(df)) == 0:
        return False, "No numeric score columns found."
    return True, ""


def compute_weak_parameters(df: pd.DataFrame) -> pd.DataFrame:
    cols  = _score_cols(df)
    means = df[cols].mean().reset_index()
    means.columns = ["parameter", "avg_score"]
    weak  = means[means["avg_score"] < SCORE_THRESHOLD].sort_values("avg_score")
    weak["avg_score"] = weak["avg_score"].round(2)
    return weak


def compute_recurring_weaknesses(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in _score_cols(df):
        tmp = df[["agent_name", col]].copy()
        tmp["weak"] = tmp[col] < SCORE_THRESHOLD
        cnt = tmp.groupby("agent_name")["weak"].sum().reset_index()
        cnt.columns = ["agent_name", "weak_count"]
        cnt["parameter"] = col
        rows.append(cnt[cnt["weak_count"] >= RECURRENCE_MIN])
    if not rows:
        return pd.DataFrame(columns=["agent_name", "parameter", "weak_count"])
    return pd.concat(rows).sort_values("weak_count", ascending=False).reset_index(drop=True)


def compute_trend(df: pd.DataFrame) -> pd.DataFrame:
    cols = _score_cols(df)
    try:
        df = df.copy()
        df["audit_date"] = pd.to_datetime(df["audit_date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["audit_date"]).sort_values("audit_date")
    except Exception:
        return pd.DataFrame()
    if len(df) < 2:
        return pd.DataFrame()
    mid  = len(df) // 2
    f    = df.iloc[:mid][cols].mean()
    l    = df.iloc[mid:][cols].mean()
    rows = []
    for c in cols:
        d = l[c] - f[c]
        rows.append({
            "parameter": c,
            "trend":     "Improving" if d > 2 else ("Declining" if d < -2 else "Stable"),
            "first_avg": round(f[c], 2),
            "last_avg":  round(l[c], 2),
            "change":    round(d, 2),
        })
    return pd.DataFrame(rows).sort_values("change")


def compute_agent_stats(df: pd.DataFrame) -> pd.DataFrame:
    cols  = _score_cols(df)
    stats = df.groupby("agent_name")[cols].mean()
    stats["overall_avg"] = stats.mean(axis=1).round(2)
    return stats.reset_index().sort_values("overall_avg")


def build_tni_summary(df: pd.DataFrame) -> dict:
    weak  = compute_weak_parameters(df)
    recur = compute_recurring_weaknesses(df)
    trend = compute_trend(df)
    agent = compute_agent_stats(df)
    cols  = _score_cols(df)
    return {
        "weak_params":    weak.to_string(index=False)  if not weak.empty  else "None",
        "recurring":      recur.to_string(index=False) if not recur.empty else "None",
        "trend_data":     trend.to_string(index=False) if not trend.empty else "Not available",
        "agent_stats":    agent.to_string(index=False),
        "param_averages": df[cols].mean().round(2).to_string() if cols else "N/A",
        "_weak_df":  weak,
        "_recur_df": recur,
        "_trend_df": trend,
        "_agent_df": agent,
    }
