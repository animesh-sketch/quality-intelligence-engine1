# ============================================================
# ai_engine.py  —  Quality Intelligence Engine
# Handles all Claude API communication.
# All prompts are structured and templated here.
# ============================================================

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()  # reads ANTHROPIC_API_KEY from .env file


def _get_client() -> anthropic.Anthropic:
    """Initialise and return Anthropic client. Raises clear error if key missing."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not found. "
            "Create a .env file in the project folder and add:\n"
            "ANTHROPIC_API_KEY=sk-ant-..."
        )
    return anthropic.Anthropic(api_key=api_key)


def _call_claude(prompt: str, max_tokens: int = 1800) -> str:
    """
    Send a prompt to Claude and return the text response.
    Wraps API errors with user-friendly messages.
    """
    client = _get_client()
    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except anthropic.AuthenticationError:
        raise ValueError("Invalid API key. Please check your ANTHROPIC_API_KEY in .env")
    except anthropic.RateLimitError:
        raise ValueError("Rate limit hit. Please wait a moment and try again.")
    except anthropic.APIError as e:
        raise ValueError(f"Claude API error: {str(e)}")


# ── TNI Prompt ──────────────────────────────────────────────────────────────

TNI_PROMPT_TEMPLATE = """
You are a senior Learning & Development analyst specialising in call centre quality.

You have received the following Training Needs Identification (TNI) data from a QA audit system:

--- TNI DATA ---
{tni_data}
---

Based on this data, produce a structured analysis with EXACTLY these sections:

## 1. ROOT CAUSE ANALYSIS
Identify the likely root causes behind each weak parameter. Be specific — mention whether the cause is likely knowledge gap, process gap, motivation/attitude issue, or system/tool issue.

## 2. SKILL GAP SUMMARY
List the specific skills agents are missing. Group them by category (Communication, Product Knowledge, Compliance, Soft Skills, etc.).

## 3. PRIORITY MATRIX
Rank the top 5 training priorities from CRITICAL to LOW. Format as:
| Priority | Parameter | Impact | Urgency |

## 4. TRAINING RECOMMENDATIONS
For each priority area, recommend:
- Training format (role-play / e-learning / classroom / coaching)
- Duration
- Who should attend (all agents / specific cohort)
- Expected outcome

## 5. COACHING SCRIPT
Write a ready-to-use coaching conversation script a Team Leader can use with an underperforming agent. Include:
- Opening (empathetic, non-threatening)
- Observation statement (what was noticed)
- Impact statement (why it matters)
- Question to draw out agent's self-reflection
- Suggested improvement technique
- Commitment close

Keep the tone professional, actionable, and data-driven. Do not add disclaimers or generic advice.
"""


def analyse_tni(tni_summary: dict) -> str:
    """
    Send TNI summary data to Claude and return structured analysis.

    Parameters
    ----------
    tni_summary : dict  —  keys: weak_params, recurring, trend_data, agent_stats
    """
    data_block = f"""
Weak Parameters (score < 70):
{tni_summary.get('weak_params', 'None identified')}

Recurring Weaknesses (3+ occurrences across agents):
{tni_summary.get('recurring', 'None identified')}

Score Trend (recent direction):
{tni_summary.get('trend_data', 'Not available')}

Agent-Level Statistics:
{tni_summary.get('agent_stats', 'Not available')}

Team Average Scores by Parameter:
{tni_summary.get('param_averages', 'Not available')}
"""
    prompt = TNI_PROMPT_TEMPLATE.format(tni_data=data_block)
    return _call_claude(prompt, max_tokens=2000)


# ── Calibration Prompt ───────────────────────────────────────────────────────

CALIBRATION_PROMPT_TEMPLATE = """
You are a senior Quality Assurance Calibration expert for a call centre operation.

You have received the following calibration analysis data:

--- CALIBRATION DATA ---
{calibration_data}
---

Produce a structured calibration review with EXACTLY these sections:

## 1. CALIBRATION SUMMARY
Summarise the overall calibration health. State clearly: Is the team calibrated? What is the overall variance level? Which parameters are most at risk?

## 2. AUDITOR BIAS ANALYSIS
For each auditor flagged as strict or lenient:
- Name the auditor
- State their bias direction (strict / lenient)
- Quantify the deviation (e.g., "scores 12% below team average on Greeting")
- Explain the likely impact on agent morale and data integrity

## 3. PARAMETER DISAGREEMENT ANALYSIS
For each parameter with high variance:
- Explain WHY auditors likely disagree (ambiguous definition, subjectivity, missing examples)
- Give a concrete example of what a "3" vs "5" looks like for that parameter

## 4. GUIDELINE IMPROVEMENT SUGGESTIONS
For the top 3 most disputed parameters, write improved scoring guidelines:
- Clear behavioural anchors for each score level (1, 3, 5)
- Mandatory examples (positive and negative)
- Common mistakes auditors make when scoring this parameter

## 5. EXECUTIVE SUMMARY
Write a 5-sentence executive summary suitable for a VP / Head of Quality. Include:
- Current calibration status
- Biggest risk
- Recommended immediate action
- Expected business impact if not fixed
- Timeline for resolution

Use precise, data-driven language. No generic advice.
"""


def analyse_calibration(calibration_summary: dict) -> str:
    """
    Send calibration data to Claude and return structured analysis.

    Parameters
    ----------
    calibration_summary : dict  —  keys: variance_data, strict_auditors,
                                    lenient_auditors, disputed_params, auditor_stats
    """
    data_block = f"""
Parameters with Variance > 15%:
{calibration_summary.get('variance_data', 'None detected')}

Strict Auditors (consistently below team average):
{calibration_summary.get('strict_auditors', 'None detected')}

Lenient Auditors (consistently above team average):
{calibration_summary.get('lenient_auditors', 'None detected')}

Most Disputed Parameters (highest inter-rater disagreement):
{calibration_summary.get('disputed_params', 'None detected')}

Auditor-Level Statistics:
{calibration_summary.get('auditor_stats', 'Not available')}

Overall Team Calibration Score:
{calibration_summary.get('overall_score', 'Not available')}
"""
    prompt = CALIBRATION_PROMPT_TEMPLATE.format(calibration_data=data_block)
    return _call_claude(prompt, max_tokens=2000)
