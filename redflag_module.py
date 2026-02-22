# ============================================================
# redflag_module.py  —  Transcript Red Flag Detection
# Pre-loaded with rules from real Unext/Manipal QA data.
# ============================================================

import re
import pandas as pd

SCORE_THRESHOLD = 70

# ── Pre-loaded flag rules ─────────────────────────────────────────────────────
DEFAULT_FLAGS = [
    # HIGH — Zero tolerance
    ("HIGH", "chutiya"), ("HIGH", "f**ker"), ("HIGH", "bhnc"), ("HIGH", "tharki"),
    ("HIGH", "intercourse"), ("HIGH", "h***mi"), ("HIGH", "obscene"),
    ("HIGH", "sexual joke"), ("HIGH", "will take exam on your behalf"),
    ("HIGH", "complete assignment on your behalf"), ("HIGH", "take exam for you"),
    ("HIGH", "do assignment for you"), ("HIGH", "selling leads"), ("HIGH", "referral fee"),
    ("HIGH", "join as freelancer"), ("HIGH", "calling from government university"),
    ("HIGH", "from my personal number"), ("HIGH", "say things worse"),
    ("HIGH", "escalates then it will be a problem"), ("HIGH", "you are uneducated"),
    ("HIGH", "mentally unstable"), ("HIGH", "gunga"), ("HIGH", "kahan se aate hai"),
    ("HIGH", "bade aadmi nahi ban paye"), ("HIGH", "ravaan"),
    ("HIGH", "500 will be deducted every day"), ("HIGH", "500 deducted daily"),
    ("HIGH", "file a police case"), ("HIGH", "please go ahead all the best"),
    ("HIGH", "keep answering the phone"), ("HIGH", "we would not want student like you"),
    ("HIGH", "thik hai karwa dijie"), ("HIGH", "exited from the system"),
    ("HIGH", "separated from the organization"), ("HIGH", "final warning letter"),
    ("HIGH", "discussing internal strategy on recorded line"),
    ("HIGH", "lead exhaustion"), ("HIGH", "calling from personal number"),
    ("HIGH", "circus in parliament"), ("HIGH", "comedy in news channels"),

    # MEDIUM — Unprofessional
    ("MEDIUM", "at least it will look like i am working"),
    ("MEDIUM", "you are lying"), ("MEDIUM", "you are not telling the lie correctly"),
    ("MEDIUM", "who is more civilized"), ("MEDIUM", "lena hai admission"),
    ("MEDIUM", "ho gaya to banate ho"), ("MEDIUM", "ok do it"), ("MEDIUM", "okay do it"),
    ("MEDIUM", "don't act like an uneducated"),
    ("MEDIUM", "why are you wasting your time and my time"),
    ("MEDIUM", "don't do this drama"),
    ("MEDIUM", "screenshot bhej denge to kya de denge"),
    ("MEDIUM", "university pata hai kitni badi hai"),
    ("MEDIUM", "you are not my lead"), ("MEDIUM", "wasting time of the counselor"),
    ("MEDIUM", "why are you guys wasting"), ("MEDIUM", "disconnected call without closure"),
    ("MEDIUM", "call disconnected abruptly"), ("MEDIUM", "overlapped during conversation"),
    ("MEDIUM", "repeated calling after opt out"), ("MEDIUM", "did not acknowledge complaint"),
    ("MEDIUM", "no apology offered"), ("MEDIUM", "incorrect referral amount"),
    ("MEDIUM", "wrong policy information"), ("MEDIUM", "byjus"),
    ("MEDIUM", "natak mat karo"), ("MEDIUM", "main pagal ho jata hun"),
    ("MEDIUM", "tamij nahin hai"), ("MEDIUM", "we would not want"),
    ("MEDIUM", "amazon voucher incorrectly stated"), ("MEDIUM", "sarcastic"),

    # LOW — Communication gaps
    ("LOW", "beta"), ("LOW", "bachha"), ("LOW", "bachche"),
    ("LOW", "aunty"), ("LOW", "uncle"), ("LOW", "bhai"), ("LOW", "yaar"),
    ("LOW", "great yar"), ("LOW", "talking to colleague on recorded line"),
    ("LOW", "personal conversation on recorded line"),
    ("LOW", "voicemail not disconnected"), ("LOW", "failed to disconnect voicemail"),
    ("LOW", "background conversation recorded"),
    ("LOW", "offline conversation while call connected"),
    ("LOW", "left call unattended"), ("LOW", "call transferred without consent"),
    ("LOW", "transferred without permission"), ("LOW", "discussing on whatsapp"),
    ("LOW", "recorded line so we cannot"), ("LOW", "failed to probe effectively"),
    ("LOW", "did not update notes"), ("LOW", "status not updated"),
    ("LOW", "fir kya kroge beta"), ("LOW", "sadda kutta"),
    ("LOW", "okay go to goa"), ("LOW", "are suniye to sahi"),
    ("LOW", "giggled during conversation"), ("LOW", "laughed during conversation"),
]


def extract_agent_name(text: str) -> str:
    for pat in [
        r"Agent(?:\s+Name)?\s*[:\-]\s*(.+)",
        r"Counsello?r(?:\s+Name)?\s*[:\-]\s*(.+)",
        r"Representative\s*[:\-]\s*(.+)",
    ]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().split("\n")[0].strip()
    return "Unknown Agent"


def get_context(text: str, keyword: str, window: int = 110) -> str:
    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return ""
    start   = max(0, idx - window // 2)
    end     = min(len(text), idx + window // 2)
    snippet = text[start:end].replace("\n", " ").strip()
    return f"...{snippet}..."


def scan_transcript(filename: str, text: str, flags: list) -> dict:
    agent = extract_agent_name(text)
    hits  = []
    seen  = set()
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

    for severity, keyword in flags:
        if keyword in seen:
            continue
        if keyword.lower() in text.lower():
            hits.append({
                "severity": severity,
                "keyword":  keyword,
                "context":  get_context(text, keyword) or "(found in transcript)",
            })
            seen.add(keyword)

    hits.sort(key=lambda x: order.get(x["severity"], 3))
    return {
        "filename": filename,
        "agent":    agent,
        "flags":    hits,
        "total":    len(hits),
        "high":     sum(1 for h in hits if h["severity"] == "HIGH"),
        "medium":   sum(1 for h in hits if h["severity"] == "MEDIUM"),
        "low":      sum(1 for h in hits if h["severity"] == "LOW"),
    }


def parse_custom_rules(rules_text: str) -> list:
    """Parse user-pasted rules in format 'HIGH: phrase' """
    rules = []
    for line in rules_text.strip().split("\n"):
        line = line.strip()
        if ":" not in line:
            continue
        sev, kw = line.split(":", 1)
        sev = sev.strip().upper()
        kw  = kw.strip().lower()
        if sev in ("HIGH", "MEDIUM", "LOW") and kw:
            rules.append((sev, kw))
    return rules


def build_redflag_summary(results: list) -> dict:
    """Package scan results for AI engine."""
    total_flags  = sum(r["total"]  for r in results)
    high_count   = sum(r["high"]   for r in results)
    med_count    = sum(r["medium"] for r in results)
    low_count    = sum(r["low"]    for r in results)

    # Top flagged agents
    agent_counts = {}
    for r in results:
        a = r["agent"]
        if a not in agent_counts:
            agent_counts[a] = {"high": 0, "medium": 0, "low": 0, "total": 0}
        agent_counts[a]["high"]   += r["high"]
        agent_counts[a]["medium"] += r["medium"]
        agent_counts[a]["low"]    += r["low"]
        agent_counts[a]["total"]  += r["total"]

    top_agents_rows = sorted(agent_counts.items(),
                             key=lambda x: (-x[1]["high"], -x[1]["total"]))[:10]
    top_agents_str  = "\n".join(
        f"{a}: HIGH={v['high']} MEDIUM={v['medium']} LOW={v['low']}"
        for a, v in top_agents_rows
    )

    # Top flag keywords
    kw_counts = {}
    for r in results:
        for f in r["flags"]:
            k = f["keyword"]
            kw_counts[k] = kw_counts.get(k, 0) + 1
    top_kw = sorted(kw_counts.items(), key=lambda x: -x[1])[:10]
    top_flags_str = "\n".join(f'"{k}": {v} occurrences' for k, v in top_kw)

    # Detail sample
    details = []
    for r in results:
        for f in r["flags"][:2]:
            details.append(f"[{f['severity']}] {r['agent']} | {f['keyword']}")
    flag_details_str = "\n".join(details[:30])

    return {
        "total_transcripts": len(results),
        "total_flags":       total_flags,
        "high_count":        high_count,
        "medium_count":      med_count,
        "low_count":         low_count,
        "top_agents":        top_agents_str,
        "top_flags":         top_flags_str,
        "flag_details":      flag_details_str,
    }
