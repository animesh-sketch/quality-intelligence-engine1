# ============================================================
# smart_detector.py  —  Quality Intelligence Engine v3
# Auto-detects uploaded file type and maps columns intelligently.
# The user just uploads — this figures out what to do with it.
# ============================================================

import pandas as pd
import numpy as np
from difflib import get_close_matches

# Known column name variations (fuzzy matching)
AGENT_NAME_ALIASES    = ["agent_name", "agent", "name", "counsellor", "counselor",
                          "representative", "rep_name", "employee", "emp_name"]
AUDITOR_NAME_ALIASES  = ["auditor_name", "auditor", "qa_name", "reviewer", "qa"]
CALL_ID_ALIASES       = ["call_id", "call", "callid", "ticket_id", "reference",
                          "call_reference", "interaction_id"]
DATE_ALIASES          = ["audit_date", "date", "audit_dt", "call_date", "month",
                          "week", "period"]

# Common score parameter names
SCORE_KEYWORDS = ["greeting", "empathy", "closing", "compliance", "communication",
                  "product", "knowledge", "objection", "handling", "soft", "skill",
                  "accuracy", "opening", "probing", "resolution", "hold", "transfer",
                  "tone", "clarity", "patience", "rapport", "needs", "assessment",
                  "quality", "score", "rating", "marks", "points"]


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, strip, replace spaces with underscore."""
    df = df.copy()
    df.columns = (df.columns.str.strip()
                             .str.lower()
                             .str.replace(r"[\s\-/\\]+", "_", regex=True)
                             .str.replace(r"[^\w]", "", regex=True))
    return df


def fuzzy_rename(df: pd.DataFrame, aliases: list, target: str) -> pd.DataFrame:
    """If target column missing, find best alias match and rename it."""
    if target in df.columns:
        return df
    for alias in aliases:
        if alias in df.columns:
            df = df.rename(columns={alias: target})
            return df
    # Try fuzzy match
    cols = df.columns.tolist()
    matches = get_close_matches(target, cols, n=1, cutoff=0.7)
    if matches:
        df = df.rename(columns={matches[0]: target})
    return df


def detect_and_normalise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auto-map common column name variations to standard names.
    """
    df = normalise_columns(df)
    df = fuzzy_rename(df, AGENT_NAME_ALIASES,   "agent_name")
    df = fuzzy_rename(df, AUDITOR_NAME_ALIASES,  "auditor_name")
    df = fuzzy_rename(df, CALL_ID_ALIASES,       "call_id")
    df = fuzzy_rename(df, DATE_ALIASES,          "audit_date")
    return df


def get_score_columns(df: pd.DataFrame) -> list:
    """
    Return numeric columns that look like quality parameters.
    Excludes ID, name, date columns.
    """
    exclude = {"agent_name", "auditor_name", "audit_date", "call_id",
               "month", "week", "team", "supervisor", "date", "id",
               "master_auditor", "overall_score"}
    master_exclude = {c for c in df.columns if c.startswith("master_")}
    exclude = exclude | master_exclude

    candidates = [
        c for c in df.columns
        if c not in exclude
        and pd.api.types.is_numeric_dtype(df[c])
        and not c.startswith("master_")
    ]
    return candidates


def classify_file(df: pd.DataFrame) -> str:
    """
    Determine what kind of file this is:
    - 'tni'          — agent scores by auditor/date, no master cols
    - 'calibration'  — multiple auditors scoring same calls
    - 'ata'          — has master_ columns
    - 'unknown'      — can't determine
    """
    cols = df.columns.tolist()
    score_cols = get_score_columns(df)

    has_master  = any(c.startswith("master_") for c in cols)
    has_auditor = "auditor_name" in cols
    has_agent   = "agent_name" in cols
    has_call    = "call_id" in cols

    if has_master:
        return "ata"

    if has_auditor and has_call:
        # Check if multiple auditors scored same call
        if has_call and df.groupby("call_id")["auditor_name"].nunique().max() > 1:
            return "calibration"
        return "calibration"  # has auditor + call_id = calibration data

    if has_agent and not has_auditor and score_cols:
        return "tni"

    if has_agent and has_auditor and score_cols:
        return "tni"  # Both agent and auditor — treat as TNI

    return "unknown"


def validate_scores(df: pd.DataFrame) -> list:
    """
    Check score columns are in expected range (0-100).
    Return list of warnings.
    """
    warnings = []
    score_cols = get_score_columns(df)
    for col in score_cols:
        mn = df[col].min()
        mx = df[col].max()
        if mx > 100:
            warnings.append(f"Column '{col}' has values above 100 (max={mx:.0f}). Scores should be 0-100.")
        if mn < 0:
            warnings.append(f"Column '{col}' has negative values (min={mn:.0f}).")
        null_count = df[col].isnull().sum()
        if null_count > 0:
            warnings.append(f"Column '{col}' has {null_count} missing values — these rows will be skipped.")
    return warnings


def auto_prepare(raw_df: pd.DataFrame) -> tuple:
    """
    Main entry point. Takes raw uploaded DataFrame.
    Returns (prepared_df, file_type, warnings, detected_cols_info)
    """
    df        = detect_and_normalise(raw_df)
    file_type = classify_file(df)
    warnings  = validate_scores(df)
    score_cols = get_score_columns(df)

    info = {
        "file_type":     file_type,
        "rows":          len(df),
        "score_cols":    score_cols,
        "has_agent":     "agent_name" in df.columns,
        "has_auditor":   "auditor_name" in df.columns,
        "has_call_id":   "call_id" in df.columns,
        "has_date":      "audit_date" in df.columns,
        "agent_count":   df["agent_name"].nunique() if "agent_name" in df.columns else 0,
        "auditor_count": df["auditor_name"].nunique() if "auditor_name" in df.columns else 0,
    }
    return df, file_type, warnings, info
