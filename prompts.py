"""Prompt builders used by strategy, score, and intention generation."""

from __future__ import annotations


INTENTION_ASPECTS = """Intention1: After posting this Tweet, the user wants to ...
Intention2: After viewing this Tweet, others will ...
Intention3: The user posts this Tweet because the user is ...
Intention4: The user posts this Tweet because the user intended to ...
Intention5: After posting this Tweet, the user feels ...
Intention6: After viewing this Tweet, others feel ...
Intention7: After viewing this Tweet, others want to ...
Intention8: After posting this Tweet, the user will ...
Intention9: Before posting this Tweet, the user needs to ...
Intention10: The user posts this Tweet because ..."""


def build_strategy_prompt(information: str) -> str:
    return f"""Based on the following information, design analysis strategies to explore the user's intention in posting it.

The information may include text, concepts, actions, objects, emotions, keywords, image descriptions, audio emotions, and video behavior.

Develop 10 distinct strategies. Each strategy must correspond to one of the 10 intention aspects below:

{INTENTION_ASPECTS}

Output format:
<strategy1>/<After posting this Tweet, the user wants to ...>
<strategy2>/<After viewing this Tweet, others will ...>
...

Requirements:
- Focus on how to analyze the information, not on producing the final intention.
- Make the 10 strategies meaningfully different from one another.
- Keep each strategy clear, concise, and actionable.

Information:
{information}"""


def build_score_prompt(strategy: str, information: str) -> str:
    return f"""Evaluate the provided 10 strategies, each corresponding to Intention1 to Intention10.

Per-strategy criteria, each scored 0 or 1:
1. Relevance: the strategy is directly relevant to its assigned intention aspect.
2. Analytical: the strategy describes a method for analyzing the provided information without generating a specific result.
3. Clarity: the strategy is clearly stated and easy to understand.

Overall criterion:
Distinctness: all 10 strategies must be distinct. If any two strategies are essentially the same, distinctness fails.

Scoring:
- For each strategy, compute an individual score from 0 to 3 by summing the three criteria.
- If distinctness fails, the overall score is 0.
- If distinctness passes, the overall score is the average of the 10 individual scores, rounded to two decimals.

Output format:
- Overall Score: [score]
- Breakdown: [number] strategies scored 3, [number] scored 2, [number] scored 1, [number] scored 0.
- Distinctness: [Pass/Fail]

Strategies:
{strategy}

Information:
{information}"""


def build_intention_prompt(strategy: str, information: str) -> str:
    return f"""Based on the information and strategy below, infer the user's posting intentions.

Information:
{information}

Strategy:
{strategy}

Use the strategy as guidance. Make the intentions human-centric and generate exactly 10 intentions in this format:

{INTENTION_ASPECTS}"""
