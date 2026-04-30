"""Shared JSONL helpers for the intention-generation pipeline."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SCORE_PATTERN = re.compile(r"overall\s*score\s*[:：]\s*([0-3](?:\.\d+)?)", re.I)


def read_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no} of {path}") from exc
    return records


def append_jsonl(path: str | Path, record: Dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_jsonl(path: str | Path, records: Iterable[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_record_id(record: Dict[str, Any]) -> str:
    value = record.get("key", record.get("id"))
    if value is None:
        raise ValueError(f"Record is missing a 'key' or 'id' field: {record}")
    return str(value)


def get_record_text(record: Dict[str, Any]) -> str:
    for field in ("result", "information", "text"):
        value = record.get(field)
        if value is not None:
            return str(value)
    return json.dumps(record, ensure_ascii=False)


def records_to_dict(path: str | Path) -> Tuple[Dict[str, str], List[str]]:
    data: Dict[str, str] = {}
    order: List[str] = []
    for record in read_jsonl(path):
        record_id = get_record_id(record)
        data[record_id] = get_record_text(record)
        order.append(record_id)
    return data, order


def parse_overall_score(text: str) -> Optional[float]:
    match = SCORE_PATTERN.search(text)
    if not match:
        return None
    return float(match.group(1))
