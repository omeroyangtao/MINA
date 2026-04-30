"""Run the full strategy-score-intention pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, Optional

from intention import generate_intention
from io_utils import append_jsonl, get_record_id, get_record_text, read_jsonl
from llm_client import DEFAULT_MODEL_ID, LocalLLMClient
from round_score import score_strategy
from round_strategy import generate_strategy


def run_pipeline(
    input_path: str,
    output_dir: str = "outputs",
    threshold: float = 2.8,
    max_attempts: int = 3,
    model_id: str = DEFAULT_MODEL_ID,
    overwrite: bool = False,
) -> Dict[str, int]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if overwrite:
        _clear_outputs(
            output,
            (
                "strategy_attempts.jsonl",
                "score_attempts.jsonl",
                "strategy_final.jsonl",
                "intention.jsonl",
                "discarded.jsonl",
            ),
        )
    client = LocalLLMClient(model_id=model_id)

    summary = {"accepted": 0, "discarded": 0, "total": 0}
    for record in read_jsonl(input_path):
        summary["total"] += 1
        record_id = get_record_id(record)
        information = get_record_text(record)
        accepted_strategy: Optional[str] = None
        accepted_score: Optional[float] = None

        for attempt in range(1, max_attempts + 1):
            strategy = generate_strategy(information, client)
            append_jsonl(
                output / "strategy_attempts.jsonl",
                {"key": record_id, "attempt": attempt, "result": strategy},
            )

            score_text = score_strategy(strategy, information, client)
            score = _extract_score(score_text)
            append_jsonl(
                output / "score_attempts.jsonl",
                {
                    "key": record_id,
                    "attempt": attempt,
                    "score": score,
                    "result": score_text,
                },
            )

            print(f"{record_id}: attempt {attempt}/{max_attempts}, score={score}")
            if score is not None and score >= threshold:
                accepted_strategy = strategy
                accepted_score = score
                break

        if accepted_strategy is None:
            summary["discarded"] += 1
            append_jsonl(
                output / "discarded.jsonl",
                {"key": record_id, "reason": "score_below_threshold", "threshold": threshold},
            )
            continue

        append_jsonl(
            output / "strategy_final.jsonl",
            {"key": record_id, "score": accepted_score, "result": accepted_strategy},
        )
        intention = generate_intention(accepted_strategy, information, client)
        append_jsonl(output / "intention.jsonl", {"key": record_id, "result": intention})
        summary["accepted"] += 1
        print(f"{record_id}: accepted and generated intention")

    return summary


def _extract_score(score_text: str) -> Optional[float]:
    from io_utils import parse_overall_score

    return parse_overall_score(score_text)


def _clear_outputs(output_dir: Path, filenames: Iterable[str]) -> None:
    for filename in filenames:
        path = output_dir / filename
        if path.exists():
            path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="all_information.jsonl", help="Input JSONL file.")
    parser.add_argument("--output-dir", default="outputs", help="Directory for all pipeline outputs.")
    parser.add_argument("--threshold", type=float, default=2.8, help="Minimum accepted overall score.")
    parser.add_argument("--max-attempts", type=int, default=3, help="Maximum strategy generations per record.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Local Hugging Face model path/name.")
    parser.add_argument("--overwrite", action="store_true", help="Clear existing output files before running.")
    args = parser.parse_args()

    summary = run_pipeline(
        input_path=args.input,
        output_dir=args.output_dir,
        threshold=args.threshold,
        max_attempts=args.max_attempts,
        model_id=args.model_id,
        overwrite=args.overwrite,
    )
    print(
        "Done: "
        f"{summary['accepted']} accepted, "
        f"{summary['discarded']} discarded, "
        f"{summary['total']} total."
    )


if __name__ == "__main__":
    main()
