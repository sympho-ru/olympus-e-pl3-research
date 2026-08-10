from __future__ import annotations

import json
from pathlib import Path

import pytest

from epl3_research.evidence import EvidenceCounts, EvidenceError, load_evidence


def compact(value: dict[str, object]) -> str:
    return json.dumps(value, separators=(",", ":"))


def range_row(digest: str = "0" * 64, offset: int = 8, length: int = 16):
    return {"block": 0, "offset": offset, "length": length, "sha256": digest}


def instruction_row(digest: str = "0" * 64):
    return {
        "address": 4096,
        "instruction": "nop",
        "block": 0,
        "offset": 0,
        "length": 1,
        "sha256": digest,
    }


def write_evidence(
    root: Path,
    range_value: dict[str, object] | None = None,
    instruction_value: dict[str, object] | None = None,
) -> None:
    directory = root / "evidence"
    directory.mkdir(exist_ok=True)
    (directory / "ranges.jsonl").write_text(
        compact(range_value or range_row()) + "\n", encoding="utf-8"
    )
    (directory / "instructions.jsonl").write_text(
        compact(instruction_value or instruction_row()) + "\n", encoding="utf-8"
    )


def test_flat_evidence_schema_has_only_two_canonical_files(
    tmp_path: Path, synthetic_source
) -> None:
    write_evidence(tmp_path)
    assert load_evidence(tmp_path, synthetic_source.registry) == EvidenceCounts(1, 1)

    (tmp_path / "evidence" / "topic.json").write_text('{"facts":[]}\n')
    with pytest.raises(EvidenceError, match="unexpected topic.json"):
        load_evidence(tmp_path, synthetic_source.registry)


def test_range_and_instruction_rows_fail_closed(tmp_path: Path, synthetic_source) -> None:
    write_evidence(tmp_path, range_row(offset=9999, length=1))
    with pytest.raises(EvidenceError, match="outside block"):
        load_evidence(tmp_path, synthetic_source.registry)

    write_evidence(tmp_path)
    (tmp_path / "evidence" / "ranges.jsonl").write_text(
        compact(range_row(offset=9, length=1))
        + "\n"
        + compact(range_row(offset=8, length=1))
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(EvidenceError, match="must be sorted"):
        load_evidence(tmp_path, synthetic_source.registry)


def test_source_bound_validation_recomputes_all_slice_hashes(
    tmp_path: Path, synthetic_source
) -> None:
    valid_range = range_row(synthetic_source.slice_sha256(0, 8, 16))
    valid_instruction = instruction_row(synthetic_source.slice_sha256(0, 0, 1))
    write_evidence(tmp_path, valid_range, valid_instruction)
    assert load_evidence(tmp_path, source=synthetic_source) == EvidenceCounts(1, 1)

    for field, changed_value in (
        ("offset", 9),
        ("length", 15),
        ("sha256", "f" * 64),
    ):
        changed = dict(valid_range)
        changed[field] = changed_value
        write_evidence(tmp_path, changed, valid_instruction)
        with pytest.raises(EvidenceError, match="sha256 mismatch"):
            load_evidence(tmp_path, source=synthetic_source)

    changed_instruction = dict(valid_instruction)
    changed_instruction["sha256"] = "f" * 64
    write_evidence(tmp_path, valid_range, changed_instruction)
    with pytest.raises(EvidenceError, match="sha256 mismatch"):
        load_evidence(tmp_path, source=synthetic_source)
