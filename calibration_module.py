# ============================================================
# calibration_module.py  —  Inter-rater reliability logic
# ============================================================

import pandas as pd
import numpy as np
from typing import Tuple

VARIANCE_THRESHOLD = 15
BIAS_THRESHOLD     = 5

EXCLUDE_COLS = {"auditor_name", "agent_name", "audit_date", "call_id",
                "month", "week", "team", "supervisor", "date"}


def _score_cols(df: pd.DataFrame) -> list:
    return [c for c in df.columns
            if c.lower() not in EXCLUDE_COLS
            and pd.api.types.is_numeric_dtype(df[c])]


def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    if "auditor_name" not in df.columns:
        return False, "Missing 'auditor_name' column."
    if len(_score_cols(df)) == 0:
        return False, "No numeric score columns found."
    return True, ""


def compute_variance(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in _score_cols(df):
        m  = df[col].mean()
        s  = df[col].std()
        cv = (s / m * 100) if m else 0
        rows.append({
            "parameter":  col,
            "mean_score": round(m, 2),
            "std_dev":    round(s, 2),
            "variance_%": round(cv, 2),
            "flagged":    cv > VARIANCE_THRESHOLD,
        })
    return pd.DataFrame(rows).sort_values("variance_%", ascending=False)


def detect_auditor_bias(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    cols          = _score_cols(df)
    overall_means = df[cols].mean()
    auditor_means = df.groupby("auditor_name")[cols].mean()
    deviations    = auditor_means - overall_means
    strict, lenient = [], []
    for auditor in deviations.index:
        row     = deviations.loc[auditor]
        avg_dev = row.mean()
        if avg_dev <= -BIAS_THRESHOLD:
            strict.append({
                "auditor_name":    auditor,
                "avg_deviation":   round(avg_dev, 2),
                "most_strict_on":  row.idxmin(),
                "deviation_there": round(row.min(), 2),
            })
        elif avg_dev >= BIAS_THRESHOLD:
            lenient.append({
                "auditor_name":     auditor,
                "avg_deviation":    round(avg_dev, 2),
                "most_lenient_on":  row.idxmax(),
                "deviation_there":  round(row.max(), 2),
            })
    empty_s = pd.DataFrame(columns=["auditor_name","avg_deviation","most_strict_on","deviation_there"])
    empty_l = pd.DataFrame(columns=["auditor_name","avg_deviation","most_lenient_on","deviation_there"])
    return (pd.DataFrame(strict)  if strict  else empty_s,
            pd.DataFrame(lenient) if lenient else empty_l)


def compute_disputed_parameters(df: pd.DataFrame) -> pd.DataFrame:
    cols = _score_cols(df)
    rows = []
    if "call_id" in df.columns:
        for col in cols:
            std = df.groupby("call_id")[col].std().dropna()
            rows.append({"parameter": col, "avg_disagreement": round(std.mean(), 2) if not std.empty else 0})
    else:
        for col in cols:
            rows.append({"parameter": col, "avg_disagreement": round(df[col].std(), 2)})
    return pd.DataFrame(rows).sort_values("avg_disagreement", ascending=False)


def compute_auditor_stats(df: pd.DataFrame) -> pd.DataFrame:
    cols  = _score_cols(df)
    stats = df.groupby("auditor_name")[cols].mean()
    stats["overall_avg"]  = stats.mean(axis=1).round(2)
    stats["audit_count"]  = df.groupby("auditor_name").size()
    return stats.reset_index()[["auditor_name", "overall_avg", "audit_count"]].sort_values("overall_avg")


def overall_health(variance_df: pd.DataFrame) -> str:
    total   = len(variance_df)
    flagged = variance_df["flagged"].sum()
    if total == 0:
        return "Unknown"
    pct = flagged / total * 100
    if pct == 0:   return "Excellent — all parameters within tolerance"
    if pct <= 25:  return f"Good — {int(pct)}% of parameters need attention"
    if pct <= 60:  return f"At Risk — {int(pct)}% of parameters show high variance"
    return f"CRITICAL — {int(pct)}% of parameters out of calibration"


def build_calibration_summary(df: pd.DataFrame) -> dict:
    var        = compute_variance(df)
    strict, le = detect_auditor_bias(df)
    disputed   = compute_disputed_parameters(df)
    aud_stats  = compute_auditor_stats(df)
    flagged    = var[var["flagged"]]
    return {
        "variance_data":    flagged.to_string(index=False)  if not flagged.empty  else "None",
        "strict_auditors":  strict.to_string(index=False)   if not strict.empty   else "None",
        "lenient_auditors": le.to_string(index=False)       if not le.empty       else "None",
        "disputed_params":  disputed.head(5).to_string(index=False),
        "auditor_stats":    aud_stats.to_string(index=False),
        "overall_score":    overall_health(var),
        "_variance_df":  var,
        "_strict_df":    strict,
        "_lenient_df":   le,
        "_disputed_df":  disputed,
        "_auditor_df":   aud_stats,
    }
