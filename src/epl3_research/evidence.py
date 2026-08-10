from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .source import SourceRegistry, VerifiedSource, load_registry


RANGE_FIELDS = frozenset({"block", "offset", "length", "sha256"})
INSTRUCTION_FIELDS = frozenset(
    {"address", "instruction", "block", "offset", "length", "sha256"}
)
EVIDENCE_FILES = frozenset({"ranges.jsonl", "instructions.jsonl"})
SHA256_RE = re.compile(r"[0-9a-f]{64}")
RangeRow = tuple[int, int, int, str]
InstructionRow = tuple[int, str, int, int, int, str]


class EvidenceError(ValueError):
    """The public firmware evidence is malformed or inconsistent."""


@dataclass(frozen=True)
class EvidenceCounts:
    ranges: int
    instructions: int


def _fields(value: dict[str, Any], expected: frozenset[str], context: str) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing or unknown:
        parts = []
        if missing:
            parts.append(f"missing {', '.join(missing)}")
        if unknown:
            parts.append(f"unknown {', '.join(unknown)}")
        raise EvidenceError(f"{context}: {'; '.join(parts)}")


def _text(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{context} must be a nonempty string")
    return value


def _range(
    value: object,
    context: str,
    registry: SourceRegistry,
    source: VerifiedSource | None,
) -> RangeRow:
    if not isinstance(value, dict):
        raise EvidenceError(f"{context} must contain an object")
    _fields(value, RANGE_FIELDS, context)
    coordinates = []
    for field in ("block", "offset", "length"):
        item = value[field]
        if isinstance(item, bool) or not isinstance(item, int):
            raise EvidenceError(f"{context}.{field} must be an integer")
        coordinates.append(item)
    block, offset, length = coordinates
    if block < 0 or block >= len(registry.blocks):
        raise EvidenceError(f"{context}.block is outside the source registry")
    size = registry.blocks[block].size
    if offset < 0 or length < 1 or offset + length > size:
        raise EvidenceError(
            f"{context} is outside block {block}: offset={offset}, length={length}, size={size}"
        )
    digest = value["sha256"]
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        raise EvidenceError(f"{context}.sha256 must be a lowercase SHA-256")
    if source is not None:
        actual = source.slice_sha256(block, offset, length)
        if digest != actual:
            raise EvidenceError(
                f"{context}.sha256 mismatch: expected {digest}, actual {actual}"
            )
    return block, offset, length, digest


def _rows(path: Path):
    if not path.is_file():
        raise EvidenceError(f"missing evidence file: {path}")
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        context = f"{path.name}:{line_number}"
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise EvidenceError(f"invalid JSON in {context}: {error}") from error
        yield context, value


def load_range_rows(
    path: Path,
    registry: SourceRegistry,
    source: VerifiedSource | None = None,
) -> tuple[RangeRow, ...]:
    previous: tuple[int, int, int] | None = None
    result: list[RangeRow] = []
    for context, value in _rows(path):
        row = _range(value, context, registry, source)
        block, offset, length, _digest = row
        coordinate = (block, offset, length)
        if previous is not None and coordinate <= previous:
            raise EvidenceError(f"{path.name} must be sorted and contain no duplicates")
        previous = coordinate
        result.append(row)
    if not result:
        raise EvidenceError(f"evidence file is empty: {path}")
    return tuple(result)


def load_instruction_rows(
    path: Path,
    registry: SourceRegistry,
    source: VerifiedSource | None = None,
) -> tuple[InstructionRow, ...]:
    previous: InstructionRow | None = None
    result: list[InstructionRow] = []
    for context, value in _rows(path):
        if not isinstance(value, dict):
            raise EvidenceError(f"{context} must contain an object")
        _fields(value, INSTRUCTION_FIELDS, context)
        address = value["address"]
        if isinstance(address, bool) or not isinstance(address, int) or address < 0:
            raise EvidenceError(f"{context}.address must be a nonnegative integer")
        instruction = _text(value["instruction"], f"{context}.instruction")
        block, offset, length, digest = _range(
            {key: value[key] for key in RANGE_FIELDS}, context, registry, source
        )
        normalized = (address, instruction, block, offset, length, digest)
        if previous is not None and normalized <= previous:
            raise EvidenceError(f"{path.name} must be sorted and contain no duplicates")
        previous = normalized
        result.append(normalized)
    if not result:
        raise EvidenceError(f"evidence file is empty: {path}")
    return tuple(result)


def range_object(row: RangeRow) -> dict[str, object]:
    block, offset, length, digest = row
    return {"block": block, "offset": offset, "length": length, "sha256": digest}


def instruction_object(row: InstructionRow) -> dict[str, object]:
    address, instruction, block, offset, length, digest = row
    return {
        "address": address,
        "instruction": instruction,
        "block": block,
        "offset": offset,
        "length": length,
        "sha256": digest,
    }


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def load_evidence(
    root: Path,
    registry: SourceRegistry | None = None,
    source: VerifiedSource | None = None,
) -> EvidenceCounts:
    if source is not None:
        if registry is not None and registry != source.registry:
            raise EvidenceError("source registry does not match the requested registry")
        registry = source.registry
    registry = registry or load_registry()
    directory = root / "evidence"
    if not directory.is_dir():
        raise EvidenceError(f"missing evidence directory: {directory}")
    public_files = {
        path.name
        for path in directory.iterdir()
        if path.is_file() and not path.name.startswith(".")
    }
    if public_files != EVIDENCE_FILES:
        missing = sorted(EVIDENCE_FILES - public_files)
        unexpected = sorted(public_files - EVIDENCE_FILES)
        parts = []
        if missing:
            parts.append(f"missing {', '.join(missing)}")
        if unexpected:
            parts.append(f"unexpected {', '.join(unexpected)}")
        raise EvidenceError(f"evidence directory: {'; '.join(parts)}")
    ranges = load_range_rows(directory / "ranges.jsonl", registry, source)
    instructions = load_instruction_rows(
        directory / "instructions.jsonl", registry, source
    )
    return EvidenceCounts(ranges=len(ranges), instructions=len(instructions))
