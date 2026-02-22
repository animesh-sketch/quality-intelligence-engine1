# ============================================================
# ai_engine.py  —  Quality Intelligence Engine v2
# Central AI hub. All Claude API calls live here.
# ============================================================

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()


def _get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not found.\n"
            "Create a .env file and add: ANTHROPIC_API_KEY=sk-ant-..."
        )
    return anthropic.Anthropic(api_key=api_key)


def _call_claude(prompt: str, max_tokens: int = 2000) -> str:
    client = _get_client()
    try:
        msg = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except anthropic.AuthenticationError:
        raise ValueError("Invalid API key. Check ANTHROPIC_API_KEY in your .env file.")
    except anthropic.RateLimitError:
        raise ValueError("Rate limit reached. Wait a moment and try again.")
    except anthropic.APIError as e:
        raise ValueError(f"Claude API error: {e}")


# ── 1. TNI Prompt ─────────────────────────────────────────────────────────────
def analyse_tni(summary: dict) -> str:
    prompt = f"""
You are a senior Learning & Development analyst for a call centre operation.

TNI DATA:
Weak Parameters (avg score < 70):
{summary.get('weak_params', 'None')}

Recurring Weaknesses (3+ failures per agent):
{summary.get('recurring', 'None')}

Score Trend:
{summary.get('trend_data', 'Not available')}

Agent Statistics:
{summary.get('agent_stats', 'Not available')}

Parameter Averages:
{summary.get('param_averages', 'Not available')}

Produce a structured report with these EXACT sections:

## 1. ROOT CAUSE ANALYSIS
For each weak parameter, identify if the cause is: knowledge gap, process gap, attitude/motivation, or tool/system issue. Be specific.

## 2. SKILL GAP SUMMARY
List missing skills grouped by category: Communication, Product Knowledge, Compliance, Soft Skills.

## 3. PRIORITY MATRIX
| Priority Level | Parameter | Business Impact | Urgency |
Top 5 priorities ranked CRITICAL to LOW.

## 4. TRAINING RECOMMENDATIONS
For each priority: format (roleplay/e-learning/classroom/coaching), duration, who attends, expected outcome.

## 5. COACHING SCRIPT
A ready-to-use script a Team Leader can use RIGHT NOW with an underperforming agent:
- Empathetic opening
- Observation statement (what was seen)
- Impact statement (why it matters)
- Reflective question for the agent
- One improvement technique
- Commitment close

Be specific, actionable, and data-driven.
"""
    return _call_claude(prompt, 2200)


# ── 2. Calibration Prompt ─────────────────────────────────────────────────────
def analyse_calibration(summary: dict) -> str:
    prompt = f"""
You are a senior QA Calibration specialist for a call centre.

CALIBRATION DATA:
Parameters with Variance > 15%:
{summary.get('variance_data', 'None')}

Strict Auditors (scoring below team average):
{summary.get('strict_auditors', 'None')}

Lenient Auditors (scoring above team average):
{summary.get('lenient_auditors', 'None')}

Most Disputed Parameters:
{summary.get('disputed_params', 'None')}

Auditor Statistics:
{summary.get('auditor_stats', 'Not available')}

Overall Calibration Health:
{summary.get('overall_score', 'Not available')}

Produce a structured calibration report with these EXACT sections:

## 1. CALIBRATION SUMMARY
Is the team calibrated? Overall variance level? Which parameters are most at risk?

## 2. AUDITOR BIAS ANALYSIS
For each biased auditor: name, direction (strict/lenient), deviation amount, impact on data integrity.

## 3. PARAMETER DISAGREEMENT ANALYSIS
For each disputed parameter: why auditors likely disagree, what a low vs high score looks like.

## 4. GUIDELINE IMPROVEMENT SUGGESTIONS
For the top 3 disputed parameters, write improved scoring guidelines with:
- Behavioural anchors for score 1, 3, and 5
- One positive example and one negative example
- Common auditor mistakes for this parameter

## 5. EXECUTIVE SUMMARY
5 sentences for a VP/Head of Quality:
- Current calibration status
- Biggest risk right now
- Recommended immediate action
- Business impact if not fixed
- Suggested resolution timeline
"""
    return _call_claude(prompt, 2200)


# ── 3. Red Flag Prompt ────────────────────────────────────────────────────────
def analyse_red_flags(summary: dict) -> str:
    prompt = f"""
You are a senior Quality Compliance Analyst reviewing call centre red flag violations.

RED FLAG DATA:
Total Transcripts Scanned: {summary.get('total_transcripts', 0)}
Total Flags Detected: {summary.get('total_flags', 0)}
HIGH Severity Flags: {summary.get('high_count', 0)}
MEDIUM Severity Flags: {summary.get('medium_count', 0)}
LOW Severity Flags: {summary.get('low_count', 0)}

Top Flagged Agents:
{summary.get('top_agents', 'None')}

Most Common Flag Types:
{summary.get('top_flags', 'None')}

Detailed Flag List:
{summary.get('flag_details', 'None')}

Produce a structured compliance report with these EXACT sections:

## 1. COMPLIANCE RISK ASSESSMENT
Overall risk level (Critical/High/Medium/Low). Which violations pose the biggest brand and legal risk?

## 2. AGENT RISK PROFILES
For each flagged agent: risk level, pattern of behaviour, recommended action (verbal warning / written warning / PIP / termination).

## 3. VIOLATION PATTERN ANALYSIS
What patterns emerge? Are violations isolated incidents or systemic? Are certain shifts/teams more affected?

## 4. IMMEDIATE ACTION PLAN
Specific actions to take in the next 24 hours, next 7 days, and next 30 days.

## 5. PREVENTION RECOMMENDATIONS
Process changes, script updates, or monitoring improvements to prevent recurrence.
"""
    return _call_claude(prompt, 2000)


# ── 4. ATA Prompt ────────────────────────────────────────────────────────────
def analyse_ata(summary: dict) -> str:
    prompt = f"""
You are a Master Quality Auditor reviewing how accurately your QA auditors are scoring agents.

ATA DATA:
Overall ATA Health: {summary.get('overall_score', 'N/A')}
Total Auditors Reviewed: {summary.get('auditor_count', 0)}

Auditor Accuracy vs Master Scores:
{summary.get('accuracy_data', 'None')}

Parameter-Level Gaps (where auditors drift from master):
{summary.get('param_gaps', 'None')}

Missed Flags (auditor scored higher than master by 15+ points):
{summary.get('missed_flags', 'None')}

Produce a structured ATA report with these EXACT sections:

## 1. OVERALL ATA VERDICT
Is your QA team accurately auditing? What is the trust level in current audit data?

## 2. AUDITOR PERFORMANCE RANKING
Rank each auditor from most to least accurate. For each:
- Accuracy score
- Their biggest blind spot (parameter they consistently get wrong)
- Recommended action (no action / coaching / re-certification / reassignment)

## 3. MISSED FLAGS ANALYSIS
For every missed flag: what did the auditor miss, what's the risk, and what should have been scored?

## 4. PARAMETER BLIND SPOTS
Which parameters do auditors collectively misunderstand? Why? What does the correct scoring look like?

## 5. CORRECTIVE ACTION PLAN
- Immediate actions (this week)
- Short term (this month): re-calibration sessions, parameter guideline updates
- Long term: process changes to prevent recurrence
- Which auditors need re-certification before being allowed to audit again?
"""
    return _call_claude(prompt, 2000)


# ── 5. Agent Scorecard Prompt ─────────────────────────────────────────────────
def generate_agent_scorecard(agent_data: dict) -> str:
    prompt = f"""
You are a call centre performance coach generating a personalised agent report.

AGENT PROFILE:
Name: {agent_data.get('name', 'Unknown')}
Total Audits: {agent_data.get('total_audits', 0)}
Overall Average Score: {agent_data.get('overall_avg', 'N/A')}

Parameter Scores:
{agent_data.get('param_scores', 'Not available')}

Strongest Parameters:
{agent_data.get('strengths', 'None identified')}

Weakest Parameters:
{agent_data.get('weaknesses', 'None identified')}

Score Trend: {agent_data.get('trend', 'Not available')}

Red Flags Detected: {agent_data.get('red_flags', 0)}

Generate a personalised agent scorecard report with these EXACT sections:

## 1. PERFORMANCE SUMMARY
Overall rating (Exceeds/Meets/Needs Improvement/Critical). 2-3 sentence narrative about this agent's performance.

## 2. STRENGTHS
Top 3 things this agent does well. Be specific and encouraging.

## 3. DEVELOPMENT AREAS
Top 3 areas needing improvement. Be specific, non-judgmental, and actionable.

## 4. PERSONALISED COACHING PLAN
A 4-week coaching plan:
- Week 1: Focus area + specific activity
- Week 2: Focus area + specific activity
- Week 3: Focus area + specific activity
- Week 4: Assessment + next steps

## 5. MANAGER NOTES
3 bullet points a manager should know about this agent when planning team activities, call assignments, or escalation handling.
"""
    return _call_claude(prompt, 1800)

# ── 6. Voicebot Audit Prompt ──────────────────────────────────────────────────
def analyse_voicebot(summary: dict) -> str:
    kpis = summary.get("kpis", {})
    prompt = f"""
You are a senior Conversational AI Quality Analyst reviewing voicebot performance data.

VOICEBOT KPIs:
Total Interactions: {summary.get("total_interactions", 0)}
Containment Rate: {kpis.get("containment_rate", "N/A")}% (Target: {kpis.get("containment_target", 70)}%)
Escalation Rate: {kpis.get("escalation_rate", "N/A")}%
Fallback Rate: {kpis.get("fallback_rate", "N/A")}%
Intent Accuracy: {kpis.get("intent_accuracy", "N/A")}%
Response Accuracy: {kpis.get("response_accuracy", "N/A")}%
CSAT Score: {kpis.get("csat_score", "N/A")} / 5
Dead Air Rate: {kpis.get("dead_air_rate", "N/A")}%
Avg Handle Time: {kpis.get("avg_handle_time", "N/A")}s

Intent Performance by Intent Type:
{summary.get("intent_data", "Not available")}

Escalation Reasons (why users drop out to human):
{summary.get("escalation_data", "Not available")}

Failure Patterns (parameters scoring below 70):
{summary.get("failure_patterns", "Not available")}

Bot Performance Comparison:
{summary.get("bot_performance", "Not available")}

Sentiment Distribution:
{summary.get("sentiment", "Not available")}

Produce a structured voicebot analysis report with these EXACT sections:

## 1. PERFORMANCE VERDICT
Is this voicebot performing well? What is the overall health score? What are the 3 biggest wins and 3 biggest risks?

## 2. CONTAINMENT ANALYSIS
Why are users escalating to human agents? What intents/flows are failing containment? What is the business cost of current escalation rate?

## 3. INTENT & NLU ANALYSIS
Which intents are being misunderstood? What are the likely causes (training data gaps, similar intent confusion, out-of-scope queries)? Which intents need urgent retraining?

## 4. CONVERSATION FLOW FAILURES
Where in the conversation are users dropping off or getting stuck? What design improvements would reduce fallback rates?

## 5. OPTIMISATION ROADMAP
Priority-ranked list of improvements:
- Quick wins (fix in 1 week, high impact)
- Short term (1 month, NLU retraining, flow redesign)
- Long term (2-3 months, architectural changes)
For each: expected improvement in containment rate, CSAT, or intent accuracy.

## 6. EXECUTIVE SUMMARY
5 sentences for a VP / Head of CX:
- Current bot performance vs industry benchmark
- Biggest risk to customer experience
- ROI opportunity if top issues are fixed
- Recommended immediate action
- Timeline to meaningful improvement
"""
    return _call_claude(prompt, 2500)

