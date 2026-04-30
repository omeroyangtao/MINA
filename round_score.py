"""Score generated strategies and extract their overall score."""

from __future__ import annotations

import argparse
from typing import Dict, Optional

from io_utils import append_jsonl, parse_overall_score, records_to_dict
from llm_client import DEFAULT_MODEL_ID, LocalLLMClient
from prompts import build_score_prompt


def score_strategy(
    strategy: str,
    information: str,
    client: Optional[LocalLLMClient] = None,
) -> str:
    client = client or LocalLLMClient()
    return client.generate(build_score_prompt(strategy, information))


def score_strategy_record(
    record_id: str,
    strategy: str,
    information: str,
    client: Optional[LocalLLMClient] = None,
) -> Dict[str, object]:
    score_text = score_strategy(strategy, information, client)
    return {
        "key": record_id,
        "score": parse_overall_score(score_text),
        "result": score_text,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--information", default="all_information.jsonl", help="Information JSONL file.")
    parser.add_argument("--strategies", default="strategy_round-1.jsonl", help="Strategy JSONL file.")
    parser.add_argument("--output", default="score_round-1.jsonl", help="Output JSONL file.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Local Hugging Face model path/name.")
    args = parser.parse_args()

    information_by_id, _ = records_to_dict(args.information)
    strategies_by_id, strategy_ids = records_to_dict(args.strategies)
    client = LocalLLMClient(model_id=args.model_id)

    for record_id in strategy_ids:
        if record_id not in information_by_id:
            print(f"Skipping {record_id}: no matching information record.")
            continue
        result = score_strategy_record(
            record_id,
            strategies_by_id[record_id],
            information_by_id[record_id],
            client,
        )
        append_jsonl(args.output, result)
        print(f"Scored {record_id}: {result['score']}")


if __name__ == "__main__":
    main()
