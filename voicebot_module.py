# ============================================================
# voicebot_module.py  —  Quality Intelligence Engine v3
# Voicebot / IVR audit analysis.
# Analyses bot performance from audit dump CSV.
# ============================================================

import pandas as pd
import numpy as np
from typing import Tuple

# ── Column aliases — auto-mapped by smart_detector ────────────────────────────
REQUIRED_COLS = ["bot_name", "interaction_id"]   # minimum needed

EXCLUDE_COLS = {"bot_name", "interaction_id", "session_id", "call_date",
                "customer_id", "audit_date", "date", "auditor_name",
                "containment_result", "escalation_reason", "sentiment",
                "resolution_status", "intent_detected", "intent_expected",
                "language", "channel", "team", "month", "week"}

# Thresholds
CONTAINMENT_TARGET      = 70    # % of calls bot should resolve without human
INTENT_ACCURACY_TARGET  = 85    # % intent correctly identified
FALLBACK_WARNING        = 20    # % fallback rate above this = problem
SILENCE_WARNING         = 10    # % calls with dead air above this = problem
CSAT_TARGET             = 3.5   # out of 5
RESPONSE_ACCURACY_TARGET = 80   # % correct responses


def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}. Need at least: bot_name, interaction_id"
    score_cols = _score_cols(df)
    metric_cols = _metric_cols(df)
    if len(score_cols) == 0 and len(metric_cols) == 0:
        return False, "No score or metric columns found."
    return True, ""


def _score_cols(df: pd.DataFrame) -> list:
    """Numeric columns that are quality parameter scores."""
    return [c for c in df.columns
            if c.lower() not in EXCLUDE_COLS
            and pd.api.types.is_numeric_dtype(df[c])
            and not c.endswith("_rate")
            and not c.endswith("_count")
            and not c.endswith("_pct")]


def _metric_cols(df: pd.DataFrame) -> list:
    """Columns that represent performance metrics (rates, %)."""
    return [c for c in df.columns
            if (c.endswith("_rate") or c.endswith("_pct") or c.endswith("_count")
                or c in {"containment_rate","fallback_rate","escalation_rate",
                         "intent_accuracy","response_accuracy","csat_score",
                         "dead_air_rate","avg_handle_time","self_service_rate"})
            and pd.api.types.is_numeric_dtype(df[c])]


def compute_kpi_summary(df: pd.DataFrame) -> dict:
    """
    Compute top-level KPIs from the voicebot audit dump.
    Returns a flat dict of key metrics.
    """
    kpis = {}
    total = len(df)
    kpis["total_interactions"] = total

    # Containment
    if "containment_result" in df.columns:
        contained = df["containment_result"].astype(str).str.lower().isin(
            ["yes","contained","resolved","true","1","success"]
        ).sum()
        kpis["containment_rate"]   = round(contained / total * 100, 2)
        kpis["containment_target"] = CONTAINMENT_TARGET
        kpis["containment_status"] = "✅ On Target" if kpis["containment_rate"] >= CONTAINMENT_TARGET else "⚠️ Below Target"
    elif "containment_rate" in df.columns:
        kpis["containment_rate"]   = round(df["containment_rate"].mean(), 2)
        kpis["containment_status"] = "✅ On Target" if kpis["containment_rate"] >= CONTAINMENT_TARGET else "⚠️ Below Target"

    # Escalation / Fallback
    if "escalation_rate" in df.columns:
        kpis["escalation_rate"] = round(df["escalation_rate"].mean(), 2)
    elif "escalation_reason" in df.columns:
        escalated = df["escalation_reason"].notna().sum()
        kpis["escalation_rate"] = round(escalated / total * 100, 2)

    if "fallback_rate" in df.columns:
        kpis["fallback_rate"] = round(df["fallback_rate"].mean(), 2)

    # Intent accuracy
    if "intent_accuracy" in df.columns:
        kpis["intent_accuracy"] = round(df["intent_accuracy"].mean(), 2)
    elif "intent_detected" in df.columns and "intent_expected" in df.columns:
        correct = (df["intent_detected"].astype(str).str.lower() ==
                   df["intent_expected"].astype(str).str.lower()).sum()
        kpis["intent_accuracy"] = round(correct / total * 100, 2)

    # Response accuracy
    if "response_accuracy" in df.columns:
        kpis["response_accuracy"] = round(df["response_accuracy"].mean(), 2)

    # CSAT
    if "csat_score" in df.columns:
        kpis["csat_score"]  = round(df["csat_score"].mean(), 2)
        kpis["csat_target"] = CSAT_TARGET

    # Dead air / silence
    if "dead_air_rate" in df.columns:
        kpis["dead_air_rate"]   = round(df["dead_air_rate"].mean(), 2)
        kpis["silence_warning"] = kpis["dead_air_rate"] > SILENCE_WARNING

    # Handle time
    if "avg_handle_time" in df.columns:
        kpis["avg_handle_time"] = round(df["avg_handle_time"].mean(), 2)

    return kpis


def compute_intent_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse intent recognition performance.
    If intent_detected + intent_expected columns exist, compute per-intent accuracy.
    Otherwise fall back to intent_accuracy column.
    """
    if "intent_detected" in df.columns and "intent_expected" in df.columns:
        df2 = df.copy()
        df2["correct"] = (df2["intent_detected"].astype(str).str.lower() ==
                          df2["intent_expected"].astype(str).str.lower()).astype(int)
        result = df2.groupby("intent_expected").agg(
            total=("correct","count"),
            correct=("correct","sum"),
        ).reset_index()
        result["accuracy_%"] = (result["correct"] / result["total"] * 100).round(2)
        result["gap"]        = (100 - result["accuracy_%"]).round(2)
        return result.rename(columns={"intent_expected":"intent"}).sort_values("accuracy_%")

    return pd.DataFrame(columns=["intent","total","correct","accuracy_%","gap"])


def compute_escalation_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse escalation reasons — what is causing users to escalate to human?
    """
    if "escalation_reason" not in df.columns:
        return pd.DataFrame(columns=["escalation_reason","count","pct"])

    reasons = df["escalation_reason"].dropna()
    counts  = reasons.value_counts().reset_index()
    counts.columns = ["escalation_reason","count"]
    counts["pct"] = (counts["count"] / len(df) * 100).round(2)
    return counts


def compute_bot_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    If multiple bots exist, compare performance across them.
    Otherwise show performance by date/period.
    """
    if "bot_name" not in df.columns:
        return pd.DataFrame()

    score_cols   = _score_cols(df)
    metric_cols  = _metric_cols(df)
    all_cols     = list(set(score_cols + metric_cols))

    if not all_cols:
        return pd.DataFrame()

    agg    = df.groupby("bot_name")[all_cols].mean().round(2)
    counts = df.groupby("bot_name").size().reset_index(name="interactions")
    result = agg.reset_index().merge(counts, on="bot_name")
    result["overall_score"] = result[score_cols].mean(axis=1).round(2) if score_cols else 0
    return result.sort_values("overall_score", ascending=False)


def compute_failure_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify the most common failure patterns across all interactions.
    """
    score_cols = _score_cols(df)
    if not score_cols:
        return pd.DataFrame()

    # Find parameters where score < 70 (failing)
    rows = []
    for col in score_cols:
        fail_rate = (df[col] < 70).mean() * 100
        avg       = df[col].mean()
        rows.append({
            "parameter":  col.replace("_"," ").title(),
            "avg_score":  round(avg, 2),
            "fail_rate_%": round(fail_rate, 2),
            "severity":   "HIGH" if fail_rate > 50 else ("MEDIUM" if fail_rate > 25 else "LOW"),
        })

    result = pd.DataFrame(rows).sort_values("fail_rate_%", ascending=False)
    return result


def compute_sentiment_distribution(df: pd.DataFrame) -> dict:
    """If sentiment column exists, return distribution."""
    if "sentiment" not in df.columns:
        return {}
    counts = df["sentiment"].value_counts()
    return counts.to_dict()


def build_voicebot_summary(df: pd.DataFrame) -> dict:
    """Orchestrate all voicebot computations for AI engine."""
    kpis        = compute_kpi_summary(df)
    intent_df   = compute_intent_analysis(df)
    escal_df    = compute_escalation_analysis(df)
    bot_perf    = compute_bot_performance(df)
    failures    = compute_failure_patterns(df)
    sentiment   = compute_sentiment_distribution(df)

    return {
        "kpis":             kpis,
        "intent_data":      intent_df.to_string(index=False) if not intent_df.empty else "Not available",
        "escalation_data":  escal_df.to_string(index=False)  if not escal_df.empty  else "Not available",
        "bot_performance":  bot_perf.to_string(index=False)  if not bot_perf.empty  else "Not available",
        "failure_patterns": failures.to_string(index=False)  if not failures.empty  else "Not available",
        "sentiment":        str(sentiment) if sentiment else "Not available",
        "total_interactions": len(df),
        # Raw DFs for UI
        "_kpis":          kpis,
        "_intent_df":     intent_df,
        "_escal_df":      escal_df,
        "_bot_perf_df":   bot_perf,
        "_failures_df":   failures,
        "_sentiment":     sentiment,
    }
