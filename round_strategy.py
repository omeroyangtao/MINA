"""Generate analysis strategies for tweet-intention inference."""

from __future__ import annotations

import argparse
from typing import Dict, Optional

from io_utils import append_jsonl, get_record_id, get_record_text, read_jsonl
from llm_client import DEFAULT_MODEL_ID, LocalLLMClient
from prompts import build_strategy_prompt


def generate_strategy(
    information: str,
    client: Optional[LocalLLMClient] = None,
) -> str:
    client = client or LocalLLMClient()
    return client.generate(build_strategy_prompt(information))


def generate_strategy_record(
    record: Dict[str, object],
    client: Optional[LocalLLMClient] = None,
) -> Dict[str, str]:
    record_id = get_record_id(record)
    information = get_record_text(record)
    return {"key": record_id, "result": generate_strategy(information, client)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="all_information.jsonl", help="Input JSONL file.")
    parser.add_argument("--output", default="strategy_round-1.jsonl", help="Output JSONL file.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Local Hugging Face model path/name.")
    args = parser.parse_args()

    client = LocalLLMClient(model_id=args.model_id)
    for record in read_jsonl(args.input):
        result = generate_strategy_record(record, client)
        append_jsonl(args.output, result)
        print(f"Generated strategy for {result['key']}")


if __name__ == "__main__":
    main()
