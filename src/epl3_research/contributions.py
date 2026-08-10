from __future__ import annotations

import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .audit import audit_paths
from .evidence import (
    InstructionRow,
    RangeRow,
    instruction_object,
    load_evidence,
    load_instruction_rows,
    load_range_rows,
    range_object,
    write_jsonl,
)
from .source import VerifiedSource, sha256_bytes


INCOMING_RE = re.compile(r"(ranges|instructions)-([0-9a-f]{64})\.jsonl")
CANONICAL_PATHS = ("evidence/ranges.jsonl", "evidence/instructions.jsonl")


class ContributionError(ValueError):
    """A proposed contribution cannot be verified or accepted."""


@dataclass(frozen=True)
class ContributionReport:
    files: int
    new_ranges: int
    duplicate_ranges: int
    new_instructions: int
    duplicate_instructions: int

    @property
    def instruction_decodes_to_review(self) -> int:
        return self.new_instructions


@dataclass(frozen=True)
class _Analysis:
    report: ContributionReport
    canonical_ranges: tuple[RangeRow, ...]
    canonical_instructions: tuple[InstructionRow, ...]
    new_ranges: tuple[RangeRow, ...]
    new_instructions: tuple[InstructionRow, ...]
    paths: tuple[Path, ...]


def pending_contribution_files(root: Path) -> tuple[Path, ...]:
    directory = root / "incoming"
    if not directory.exists():
        return ()
    if not directory.is_dir():
        raise ContributionError(f"incoming path is not a directory: {directory}")
    return tuple(
        sorted(
            path
            for path in directory.rglob("*")
            if path.is_file() and not path.name.startswith(".")
        )
    )


def _contribution_paths(root: Path, selected: list[Path] | None) -> tuple[Path, ...]:
    incoming = (root / "incoming").resolve()
    paths = pending_contribution_files(root) if selected is None else tuple(selected)
    if not paths:
        raise ContributionError("no incoming contribution files found")
    normalized: list[Path] = []
    for supplied in paths:
        path = (supplied if supplied.is_absolute() else root / supplied).resolve()
        if path.parent != incoming:
            raise ContributionError(f"contribution must be a direct child of incoming/: {supplied}")
        if not path.is_file():
            raise ContributionError(f"contribution file does not exist: {supplied}")
        if INCOMING_RE.fullmatch(path.name) is None:
            raise ContributionError(f"invalid contribution filename: {path.name}")
        normalized.append(path)
    if len(normalized) != len(set(normalized)):
        raise ContributionError("the same contribution file was supplied more than once")
    return tuple(sorted(normalized))


def _load_submitted(
    root: Path,
    source: VerifiedSource,
    selected: list[Path] | None,
) -> tuple[tuple[Path, ...], list[RangeRow], list[InstructionRow]]:
    paths = _contribution_paths(root, selected)
    ranges: list[RangeRow] = []
    instructions: list[InstructionRow] = []
    for path in paths:
        match = INCOMING_RE.fullmatch(path.name)
        assert match is not None
        kind, expected_digest = match.groups()
        actual_digest = sha256_bytes(path.read_bytes())
        if actual_digest != expected_digest:
            raise ContributionError(
                f"filename digest mismatch for {path.name}: actual {actual_digest}"
            )
        if kind == "ranges":
            ranges.extend(load_range_rows(path, source.registry, source))
        else:
            instructions.extend(load_instruction_rows(path, source.registry, source))
    return paths, ranges, instructions


def _canonical_rows(
    root: Path,
    source: VerifiedSource,
) -> tuple[tuple[RangeRow, ...], tuple[InstructionRow, ...]]:
    load_evidence(root, source.registry)
    evidence = root / "evidence"
    return (
        load_range_rows(evidence / "ranges.jsonl", source.registry),
        load_instruction_rows(evidence / "instructions.jsonl", source.registry),
    )


def _analyze(
    root: Path,
    source: VerifiedSource,
    selected: list[Path] | None = None,
) -> _Analysis:
    canonical_ranges, canonical_instructions = _canonical_rows(root, source)
    paths, submitted_ranges, submitted_instructions = _load_submitted(
        root, source, selected
    )
    audit_findings = audit_paths(root, paths, source)
    if audit_findings:
        raise ContributionError(audit_findings[0].render())

    known_ranges = set(canonical_ranges)
    range_by_coordinate = {row[:3]: row for row in canonical_ranges}
    new_ranges: set[RangeRow] = set()
    duplicate_ranges = 0
    for row in submitted_ranges:
        if row in known_ranges or row in new_ranges:
            duplicate_ranges += 1
            continue
        coordinate = row[:3]
        if coordinate in range_by_coordinate:
            raise ContributionError(
                "range conflict at "
                f"block={row[0]}, offset={row[1]}, length={row[2]}"
            )
        range_by_coordinate[coordinate] = row
        new_ranges.add(row)

    known_instructions = set(canonical_instructions)
    instruction_by_key: dict[tuple[int, int, int, int], set[InstructionRow]] = defaultdict(set)
    for row in canonical_instructions:
        instruction_by_key[(row[0], row[2], row[3], row[4])].add(row)
    new_instructions: set[InstructionRow] = set()
    duplicate_instructions = 0
    for row in submitted_instructions:
        if row in known_instructions or row in new_instructions:
            duplicate_instructions += 1
            continue
        key = (row[0], row[2], row[3], row[4])
        if key in instruction_by_key:
            raise ContributionError(
                "instruction conflict at "
                f"address={row[0]}, block={row[2]}, offset={row[3]}, length={row[4]}"
            )
        instruction_by_key[key].add(row)
        new_instructions.add(row)

    report = ContributionReport(
        files=len(paths),
        new_ranges=len(new_ranges),
        duplicate_ranges=duplicate_ranges,
        new_instructions=len(new_instructions),
        duplicate_instructions=duplicate_instructions,
    )
    return _Analysis(
        report,
        canonical_ranges,
        canonical_instructions,
        tuple(sorted(new_ranges)),
        tuple(sorted(new_instructions)),
        paths,
    )


def _git(root: Path, *arguments: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
        ).stdout
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode("utf-8", errors="replace").strip()
        raise ContributionError(detail or f"git {' '.join(arguments)} failed") from error


def _verify_pr_scope(root: Path, base: str) -> None:
    _git(root, "rev-parse", "--verify", f"{base}^{{commit}}")
    try:
        subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", base, "HEAD"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as error:
        raise ContributionError(
            f"base {base!r} is not an ancestor of HEAD; update the contribution branch"
        ) from error

    base_incoming = _git(root, "ls-tree", "-r", "--name-only", base, "--", "incoming")
    if base_incoming.strip():
        raise ContributionError(f"base {base!r} contains pending incoming files")

    for relative in CANONICAL_PATHS:
        expected = _git(root, "show", f"{base}:{relative}")
        path = root / relative
        if not path.is_file() or path.read_bytes() != expected:
            raise ContributionError(f"contributor modified canonical file {relative}")

    changed = _git(root, "diff", "--name-only", base, "--").decode("utf-8").splitlines()
    disallowed = [
        path
        for path in changed
        if INCOMING_RE.fullmatch(Path(path).name) is None
        or Path(path).parent.as_posix() != "incoming"
    ]
    if disallowed:
        raise ContributionError(
            "contribution changes paths outside incoming/: " + ", ".join(sorted(disallowed))
        )


def check_contribution(
    root: Path,
    base: str,
    source: VerifiedSource,
) -> ContributionReport:
    _verify_pr_scope(root, base)
    return _analyze(root, source).report


def accept_contribution(
    root: Path,
    source: VerifiedSource,
    paths: list[Path],
) -> ContributionReport:
    analysis = _analyze(root, source, paths)
    if analysis.new_ranges:
        merged_ranges = sorted(set(analysis.canonical_ranges) | set(analysis.new_ranges))
        write_jsonl(
            root / "evidence" / "ranges.jsonl",
            [range_object(row) for row in merged_ranges],
        )
    if analysis.new_instructions:
        merged_instructions = sorted(
            set(analysis.canonical_instructions) | set(analysis.new_instructions)
        )
        write_jsonl(
            root / "evidence" / "instructions.jsonl",
            [instruction_object(row) for row in merged_instructions],
        )
    for path in analysis.paths:
        path.unlink()
    return analysis.report
