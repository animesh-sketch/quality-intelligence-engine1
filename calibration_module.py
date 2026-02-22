# ============================================================
# calibration_module.py  —  Quality Intelligence Engine
# Inter-rater reliability and auditor calibration logic.
# Detects variance, strict/lenient bias, and disputed params.
# ============================================================

import pandas as pd
import numpy as np
from typing import Tuple

REQUIRED_COLUMNS  = ["auditor_name"]
VARIANCE_THRESHOLD = 15    # % variance above this = calibration issue
BIAS_THRESHOLD     = 5     # points above/below mean = strict or lenient


def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validate that the uploaded calibration CSV has usable columns."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"

    score_cols = _get_score_columns(df)
    if len(score_cols) == 0:
        return False, (
            "No numeric score columns found. "
            "Add parameter columns like 'greeting', 'empathy', 'closing' with scores."
        )
    return True, ""


def _get_score_columns(df: pd.DataFrame) -> list:
    """Return numeric columns that are scoring parameters."""
    exclude = {"auditor_name", "agent_name", "audit_date", "call_id",
               "month", "week", "team", "supervisor"}
    return [
        c for c in df.columns
        if c.lower() not in exclude and pd.api.types.is_numeric_dtype(df[c])
    ]


def compute_variance(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each parameter, compute the coefficient of variation (CV = std/mean * 100).
    Flag parameters where CV > VARIANCE_THRESHOLD.
    """
    score_cols = _get_score_columns(df)
    rows = []
    for col in score_cols:
        col_mean = df[col].mean()
        col_std  = df[col].std()
        cv = (col_std / col_mean * 100) if col_mean != 0 else 0
        rows.append({
            "parameter":  col,
            "mean_score": round(col_mean, 2),
            "std_dev":    round(col_std, 2),
            "variance_%": round(cv, 2),
            "flagged":    cv > VARIANCE_THRESHOLD,
        })

    result = pd.DataFrame(rows).sort_values("variance_%", ascending=False)
    return result


def detect_auditor_bias(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compare each auditor's mean scores to the overall team mean per parameter.
    Return (strict_df, lenient_df).
    """
    score_cols = _get_score_columns(df)
    overall_means = df[score_cols].mean()

    auditor_means = df.groupby("auditor_name")[score_cols].mean()
    deviations    = auditor_means - overall_means

    strict  = []
    lenient = []

    for auditor in deviations.index:
        row  = deviations.loc[auditor]
        avg_dev = row.mean()

        if avg_dev <= -BIAS_THRESHOLD:
            # Consistently scores BELOW team average = STRICT
            worst_param = row.idxmin()
            strict.append({
                "auditor_name":    auditor,
                "avg_deviation":   round(avg_dev, 2),
                "most_strict_on":  worst_param,
                "deviation_there": round(row[worst_param], 2),
            })
        elif avg_dev >= BIAS_THRESHOLD:
            # Consistently scores ABOVE team average = LENIENT
            most_param = row.idxmax()
            lenient.append({
                "auditor_name":     auditor,
                "avg_deviation":    round(avg_dev, 2),
                "most_lenient_on":  most_param,
                "deviation_there":  round(row[most_param], 2),
            })

    strict_df  = pd.DataFrame(strict)  if strict  else pd.DataFrame(columns=["auditor_name","avg_deviation","most_strict_on","deviation_there"])
    lenient_df = pd.DataFrame(lenient) if lenient else pd.DataFrame(columns=["auditor_name","avg_deviation","most_lenient_on","deviation_there"])
    return strict_df, lenient_df


def compute_disputed_parameters(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each parameter, compute std deviation PER CALL (same call, different auditors).
    If call_id exists, use it. Otherwise fall back to global std dev ranking.
    """
    score_cols = _get_score_columns(df)

    if "call_id" in df.columns:
        # Ideal: multiple auditors scored the same call
        rows = []
        for col in score_cols:
            per_call = df.groupby("call_id")[col].std().dropna()
            rows.append({
                "parameter":       col,
                "avg_disagreement": round(per_call.mean(), 2) if not per_call.empty else 0,
            })
        result = pd.DataFrame(rows).sort_values("avg_disagreement", ascending=False)
    else:
        # Fallback: rank by overall standard deviation
        rows = []
        for col in score_cols:
            rows.append({
                "parameter":       col,
                "avg_disagreement": round(df[col].std(), 2),
            })
        result = pd.DataFrame(rows).sort_values("avg_disagreement", ascending=False)

    return result


def compute_auditor_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-auditor overall average score and audit count."""
    score_cols = _get_score_columns(df)
    stats = df.groupby("auditor_name")[score_cols].agg(["mean", "count"]).reset_index()

    # Flatten multi-level columns
    stats.columns = ["auditor_name"] + [
        f"{col[0]}_{col[1]}" for col in stats.columns[1:]
    ]

    mean_cols = [c for c in stats.columns if c.endswith("_mean")]
    stats["overall_avg"] = stats[mean_cols].mean(axis=1).round(2)
    stats["audit_count"] = df.groupby("auditor_name").size().values
    return stats[["auditor_name", "overall_avg", "audit_count"]].sort_values("overall_avg")


def compute_overall_calibration_score(variance_df: pd.DataFrame) -> str:
    """Return a simple health rating based on how many params are flagged."""
    total   = len(variance_df)
    flagged = variance_df["flagged"].sum()
    if total == 0:
        return "Unknown"
    pct = flagged / total * 100
    if pct == 0:
        return "Excellent — All parameters within calibration tolerance"
    elif pct <= 25:
        return f"Good — {int(pct)}% of parameters need attention"
    elif pct <= 60:
        return f"At Risk — {int(pct)}% of parameters show high variance"
    else:
        return f"CRITICAL — {int(pct)}% of parameters are out of calibration"


def build_calibration_summary(df: pd.DataFrame) -> dict:
    """
    Orchestrate all calibration computations and package for AI engine.
    """
    variance_df           = compute_variance(df)
    strict_df, lenient_df = detect_auditor_bias(df)
    disputed_df           = compute_disputed_parameters(df)
    auditor_stats         = compute_auditor_stats(df)
    overall_score         = compute_overall_calibration_score(variance_df)

    flagged_variance = variance_df[variance_df["flagged"]]

    return {
        "variance_data":   flagged_variance.to_string(index=False) if not flagged_variance.empty else "None",
        "strict_auditors": strict_df.to_string(index=False)        if not strict_df.empty        else "None",
        "lenient_auditors":lenient_df.to_string(index=False)       if not lenient_df.empty       else "None",
        "disputed_params": disputed_df.head(5).to_string(index=False),
        "auditor_stats":   auditor_stats.to_string(index=False),
        "overall_score":   overall_score,
        # Raw dataframes for UI charts
        "_variance_df":    variance_df,
        "_strict_df":      strict_df,
        "_lenient_df":     lenient_df,
        "_disputed_df":    disputed_df,
        "_auditor_df":     auditor_stats,
    }
