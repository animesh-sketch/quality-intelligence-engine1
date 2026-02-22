# ============================================================
# ata_module.py  —  Audit the Auditor
# Master auditor re-scores same calls and compares to QA scores.
# Detects accuracy gaps, missed flags, and scoring drift.
# ============================================================

import pandas as pd
import numpy as np
from typing import Tuple

EXCLUDE_COLS = {"auditor_name", "master_auditor", "agent_name", "call_id",
                "audit_date", "month", "week", "team", "supervisor"}

ACCURACY_THRESHOLD = 85   # auditor must be >= 85% accurate vs master
DRIFT_THRESHOLD    = 10   # 10+ point gap = scoring drift
MISS_THRESHOLD     = 15   # missed by 15+ points = missed flag


def _score_cols(df: pd.DataFrame) -> list:
    return [c for c in df.columns
            if c.lower() not in EXCLUDE_COLS
            and pd.api.types.is_numeric_dtype(df[c])]


def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    ATA CSV needs: auditor_name, master_score (or master_ prefixed cols),
    and matching parameter columns.
    Minimum: auditor_name + at least one score column pair.
    """
    if "auditor_name" not in df.columns:
        return False, "Missing 'auditor_name' column."
    
    # Check for master score columns
    master_cols = [c for c in df.columns if c.startswith("master_") 
                   and pd.api.types.is_numeric_dtype(df[c])]
    auditor_cols = _score_cols(df)
    
    if len(auditor_cols) == 0:
        return False, "No auditor score columns found."
    
    if len(master_cols) == 0:
        # Try alternate format: overall_score + master_overall_score
        if "master_overall" not in df.columns and "master_score" not in df.columns:
            return False, (
                "No master score columns found. "
                "Add columns prefixed with 'master_' (e.g. master_greeting, master_empathy) "
                "or a 'master_score' column."
            )
    return True, ""


def get_master_pairs(df: pd.DataFrame) -> list:
    """
    Return list of (auditor_col, master_col) pairs where both exist.
    """
    pairs = []
    score_cols = _score_cols(df)
    
    # Look for master_X columns matching auditor X columns
    for col in score_cols:
        master_col = f"master_{col}"
        if master_col in df.columns and pd.api.types.is_numeric_dtype(df[master_col]):
            pairs.append((col, master_col))
    
    # Fallback: if single master_score vs overall
    if not pairs:
        if "master_score" in df.columns and "overall_score" in df.columns:
            pairs.append(("overall_score", "master_score"))
        elif "master_score" in df.columns and score_cols:
            # Compare master_score against mean of all auditor cols
            pairs.append(("__mean__", "master_score"))
    
    return pairs


def compute_auditor_accuracy(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each auditor, compute accuracy % vs master across all paired parameters.
    Accuracy = 100 - avg(abs(auditor_score - master_score))
    """
    pairs = get_master_pairs(df)
    if not pairs:
        return pd.DataFrame()

    rows = []
    for auditor in df["auditor_name"].unique():
        adf = df[df["auditor_name"] == auditor]
        diffs = []
        for a_col, m_col in pairs:
            if a_col == "__mean__":
                score_cols = _score_cols(df)
                a_scores = adf[score_cols].mean(axis=1)
            else:
                a_scores = adf[a_col]
            m_scores = adf[m_col]
            diff = (a_scores - m_scores).abs().mean()
            diffs.append(diff)
        
        avg_diff   = np.mean(diffs)
        accuracy   = max(0, round(100 - avg_diff, 2))
        audit_count = len(adf)
        
        rows.append({
            "auditor_name":   auditor,
            "accuracy_%":     accuracy,
            "avg_gap_pts":    round(avg_diff, 2),
            "audits_reviewed": audit_count,
            "status":         "✅ Accurate" if accuracy >= ACCURACY_THRESHOLD else "⚠️ Needs Calibration",
        })
    
    return pd.DataFrame(rows).sort_values("accuracy_%", ascending=False)


def compute_parameter_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each parameter, show average gap between auditor and master scores.
    Highlights which parameters auditors consistently get wrong.
    """
    pairs = get_master_pairs(df)
    if not pairs:
        return pd.DataFrame()

    rows = []
    for a_col, m_col in pairs:
        if a_col == "__mean__":
            continue
        diff        = (df[a_col] - df[m_col])
        avg_gap     = round(diff.mean(), 2)
        abs_gap     = round(diff.abs().mean(), 2)
        direction   = "Over-scoring" if avg_gap > 0 else ("Under-scoring" if avg_gap < 0 else "Aligned")
        
        rows.append({
            "parameter":    a_col,
            "avg_gap":      avg_gap,
            "abs_avg_gap":  abs_gap,
            "direction":    direction,
            "flagged":      abs_gap > DRIFT_THRESHOLD,
        })
    
    return pd.DataFrame(rows).sort_values("abs_avg_gap", ascending=False)


def detect_missed_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Find calls where auditor score was significantly higher than master
    (auditor missed a serious issue the master caught).
    Gap > MISS_THRESHOLD = missed flag.
    """
    pairs = get_master_pairs(df)
    if not pairs:
        return pd.DataFrame()

    missed = []
    for a_col, m_col in pairs:
        if a_col == "__mean__":
            continue
        col_df = df.copy()
        col_df["gap"] = col_df[a_col] - col_df[m_col]
        serious = col_df[col_df["gap"] > MISS_THRESHOLD]
        for _, row in serious.iterrows():
            missed.append({
                "auditor_name":  row.get("auditor_name", "Unknown"),
                "call_id":       row.get("call_id", "N/A"),
                "agent_name":    row.get("agent_name", "N/A"),
                "parameter":     a_col,
                "auditor_score": row[a_col],
                "master_score":  row[m_col],
                "gap":           round(row["gap"], 1),
            })
    
    if not missed:
        return pd.DataFrame(columns=["auditor_name","call_id","parameter","auditor_score","master_score","gap"])
    
    return pd.DataFrame(missed).sort_values("gap", ascending=False)


def compute_overall_ata_score(accuracy_df: pd.DataFrame) -> str:
    """Return overall ATA health summary."""
    if accuracy_df.empty:
        return "Not available"
    avg = accuracy_df["accuracy_%"].mean()
    below = (accuracy_df["accuracy_%"] < ACCURACY_THRESHOLD).sum()
    total = len(accuracy_df)
    if avg >= 95:
        return f"Excellent — avg accuracy {avg:.1f}% across all auditors"
    elif avg >= 85:
        return f"Good — avg accuracy {avg:.1f}%, {below}/{total} auditors below threshold"
    elif avg >= 70:
        return f"At Risk — avg accuracy {avg:.1f}%, {below}/{total} auditors need recalibration"
    else:
        return f"CRITICAL — avg accuracy {avg:.1f}%, majority of auditors are miscalibrated"


def build_ata_summary(df: pd.DataFrame) -> dict:
    """Orchestrate all ATA computations."""
    accuracy_df  = compute_auditor_accuracy(df)
    param_gaps   = compute_parameter_gaps(df)
    missed_flags = detect_missed_flags(df)
    overall      = compute_overall_ata_score(accuracy_df)

    return {
        "accuracy_data":  accuracy_df.to_string(index=False) if not accuracy_df.empty else "None",
        "param_gaps":     param_gaps.to_string(index=False)  if not param_gaps.empty  else "None",
        "missed_flags":   missed_flags.to_string(index=False) if not missed_flags.empty else "None",
        "overall_score":  overall,
        "auditor_count":  df["auditor_name"].nunique(),
        "_accuracy_df":   accuracy_df,
        "_param_gaps_df": param_gaps,
        "_missed_df":     missed_flags,
    }
