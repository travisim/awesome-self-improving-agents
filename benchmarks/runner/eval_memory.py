#!/usr/bin/env python3
"""Dataset validator and adapter inspector for the self-improvement benchmarks.

This runner deliberately does **not** fabricate scores. It validates dataset
schemas, reports corpus statistics, and lists registered memory adapters.
Actual measurements require a concrete `MemoryAdapter` implementation plus an
agent harness; until one exists, this tool refuses to print benchmark results.

Usage:
    python3 benchmarks/runner/eval_memory.py --validate
    python3 benchmarks/runner/eval_memory.py --list
    python3 benchmarks/runner/eval_memory.py --stats
    python3 benchmarks/runner/eval_memory.py --list-adapters

Exit codes:
    0  all requested checks passed
    1  schema violation or I/O error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset"
RUNNER_DIR = Path(__file__).resolve().parent


class FieldSpec:
    """A required field with an expected Python type and a human description."""

    def __init__(self, name: str, kind: type, description: str, non_empty: bool = True):
        self.name = name
        self.kind = kind
        self.description = description
        self.non_empty = non_empty


SCHEMAS: Dict[str, Dict[str, Any]] = {
    "contradiction_overwrite.json": {
        "metric": "COF",
        "prefix": "cof-",
        "fields": [
            FieldSpec("id", str, "unique case id"),
            FieldSpec("topic", str, "subject domain of the fact"),
            FieldSpec("turn_initial", str, "the fact stated early (later stale)"),
            FieldSpec("turn_update", str, "the contradicting fact stated later"),
            FieldSpec("query", str, "question asked after both turns"),
            FieldSpec("expected_answer", str, "post-update truth"),
            FieldSpec("stale_trap", str, "answer indicating the stale fact was used"),
        ],
    },
    "needle_in_multiturn.json": {
        "metric": "NIMS",
        "prefix": "nims-",
        "fields": [
            FieldSpec("id", str, "unique case id"),
            FieldSpec("needle", str, "the embedded constraint text"),
            FieldSpec("injected_turn", int, "turn where the needle appears", non_empty=False),
            FieldSpec("total_turns", int, "session length", non_empty=False),
            FieldSpec("query", str, "later question depending on the needle"),
            FieldSpec("expected_value", str, "literal value that must be recovered"),
        ],
    },
    "cross_session_transfer.json": {
        "metric": "CSST",
        "prefix": "csst-",
        "fields": [
            FieldSpec("id", str, "unique case id"),
            FieldSpec("skill_name", str, "identifier of the taught procedure"),
            FieldSpec("session_1_teaching", str, "instruction taught in session 1"),
            FieldSpec("session_2_task", str, "independent request in session 2"),
            FieldSpec("expected_command", str, "artifact proving the skill was applied"),
        ],
    },
}


def _fail(errors: List[str], message: str) -> None:
    errors.append(message)


def validate_file(filename: str, spec: Dict[str, Any], seen_ids: Dict[str, str]) -> Tuple[bool, int, List[str]]:
    path = DATASET_DIR / filename
    errors: List[str] = []

    if not path.exists():
        return False, 0, [f"missing file: {path}"]

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        return False, 0, [f"invalid JSON: {exc}"]

    if not isinstance(data, list):
        return False, 0, ["root must be a JSON array"]
    if not data:
        return False, 0, ["dataset is empty"]

    prefix = spec["prefix"]
    field_names = [field.name for field in spec["fields"]]

    for index, record in enumerate(data):
        location = f"[{index}]"
        if not isinstance(record, dict):
            _fail(errors, f"{location} must be an object")
            continue

        for field in spec["fields"]:  # type: ignore[union-attr]
            location = f"[{index}].{field.name}"
            if field.name not in record:
                _fail(errors, f"{location} missing (expected {field.description})")
                continue
            value = record[field.name]
            if not isinstance(value, field.kind):
                _fail(errors, f"{location} must be {field.kind.__name__}, got {type(value).__name__}")
                continue
            if field.non_empty and isinstance(value, str) and not value.strip():
                _fail(errors, f"{location} must not be empty")

        case_id = record.get("id")
        if isinstance(case_id, str) and case_id:
            location = f"[{index}].id"
            if not case_id.startswith(prefix):
                _fail(errors, f"{location} should start with '{prefix}' (got '{case_id}')")
            if case_id in seen_ids:
                _fail(errors, f"{location} duplicate of {seen_ids[case_id]}")
            else:
                seen_ids[case_id] = filename

        extra = sorted(set(record) - set(field_names))
        if extra:
            print(f"    note: {filename}[{index}] extra keys {extra} (allowed, not validated)")

        # Metric-specific invariants.
        if filename == "contradiction_overwrite.json":
            expected = record.get("expected_answer")
            stale = record.get("stale_trap")
            if isinstance(expected, str) and isinstance(stale, str) and expected.strip() == stale.strip():
                _fail(errors, f"[{index}] expected_answer equals stale_trap — case cannot distinguish update from failure")
        if filename == "needle_in_multiturn.json":
            injected = record.get("injected_turn")
            total = record.get("total_turns")
            if isinstance(injected, int) and isinstance(total, int):
                if injected < 0 or total <= 0:
                    _fail(errors, f"[{index}] turn counts must be positive")
                elif injected > total:
                    _fail(errors, f"[{index}] injected_turn ({injected}) exceeds total_turns ({total})")

    return (len(errors) == 0), len(data), errors


def cmd_validate() -> int:
    print("Validating benchmark datasets\n")
    all_ok = True
    total_cases = 0
    seen_ids: Dict[str, str] = {}

    for filename, spec in SCHEMAS.items():
        ok, count, errors = validate_file(filename, spec, seen_ids)
        metric = spec["metric"]
        if ok:
            print(f"  PASS  {filename:34s} {metric:5s} {count:3d} cases")
            total_cases += count
        else:
            all_ok = False
            print(f"  FAIL  {filename:34s} {metric:5s} {count:3d} cases")
            for error in errors:
                print(f"          - {error}")

    print()
    if all_ok:
        print(f"All datasets valid. Total scenarios: {total_cases}")
        return 0
    print("Validation failed. Fix the errors above.")
    return 1


def load_dataset(filename: str) -> List[Dict[str, Any]]:
    with (DATASET_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def cmd_list() -> int:
    for filename, spec in SCHEMAS.items():
        print(f"\n{spec['metric']} — {filename}")
        try:
            records = load_dataset(filename)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  (cannot read: {exc})")
            continue
        for record in records:
            case_id = record.get("id", "<no id>")
            label = (
                record.get("topic")
                or record.get("skill_name")
                or f"turns={record.get('total_turns', '?')} injected={record.get('injected_turn', '?')}"
            )
            print(f"  {case_id:14s} {label}")
    return 0


def cmd_stats() -> int:
    print("Corpus statistics\n")
    total = 0
    for filename, spec in SCHEMAS.items():
        try:
            records = load_dataset(filename)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  {filename:34s} unreadable: {exc}")
            continue
        total += len(records)
        print(f"  {filename:34s} {len(records):3d} records")
        if filename == "needle_in_multiturn.json":
            buckets: Dict[int, int] = {}
            for record in records:
                turns = record.get("total_turns")
                if isinstance(turns, int):
                    buckets[turns] = buckets.get(turns, 0) + 1
            for turns in sorted(buckets):
                print(f"      {turns:>4d} turns: {buckets[turns]} case(s)")
    print(f"\n  total records: {total}")
    print("\n  VSCE: not implemented (planned, see issue tracker)")
    return 0


def cmd_list_adapters() -> int:
    sys.path.insert(0, str(RUNNER_DIR))
    try:
        from adapters import available_adapters  # type: ignore[import-not-found]
    except ImportError as exc:
        print(f"Could not import adapter registry: {exc}")
        return 1

    adapters = available_adapters()
    if not adapters:
        print("No adapters registered.")
        print("Implement one in benchmarks/runner/adapters/ and decorate it with")
        print("@register_adapter. See benchmarks/README.md for the contract.")
        return 0

    print(f"{len(adapters)} adapter(s) registered:\n")
    for name, cls in sorted(adapters.items()):
        caps = cls.capabilities
        flags = [
            label
            for label, enabled in (
                ("vector", caps.vector_search),
                ("graph", caps.graph_traversal),
                ("temporal", caps.temporal_validity),
                ("persistent", caps.persistence),
            )
            if enabled
        ]
        print(f"  {name:24s} {cls.__module__}.{cls.__name__}  [{', '.join(flags) or 'no declared capabilities'}]")
        if caps.notes:
            print(f"      {caps.notes}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate benchmark datasets and inspect memory adapters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="This runner never prints benchmark scores it did not compute.",
    )
    parser.add_argument("--validate", action="store_true", help="check every dataset against its schema")
    parser.add_argument("--list", action="store_true", help="list cases in each dataset")
    parser.add_argument("--stats", action="store_true", help="print corpus statistics")
    parser.add_argument("--list-adapters", action="store_true", help="show registered memory adapters")
    args = parser.parse_args()

    if not any((args.validate, args.list, args.stats, args.list_adapters)):
        parser.print_help()
        print("\nTip: --validate is what CI runs.")
        return 0

    status = 0
    if args.validate:
        status |= cmd_validate()
    if args.list:
        status |= cmd_list()
    if args.stats:
        status |= cmd_stats()
    if args.list_adapters:
        status |= cmd_list_adapters()
    return status


if __name__ == "__main__":
    sys.exit(main())
