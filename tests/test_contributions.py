from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from epl3_research import cli
from epl3_research.contributions import (
    ContributionError,
    accept_contribution,
    check_contribution,
)
from epl3_research.evidence import EvidenceCounts, load_evidence, write_jsonl
from epl3_research.source import sha256_bytes


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def range_row(source, offset: int, length: int = 1) -> dict[str, object]:
    return {
        "block": 0,
        "offset": offset,
        "length": length,
        "sha256": source.slice_sha256(0, offset, length),
    }


def instruction_row(
    source, address: int, offset: int, instruction: str
) -> dict[str, object]:
    return {
        "address": address,
        "instruction": instruction,
        "block": 0,
        "offset": offset,
        "length": 1,
        "sha256": source.slice_sha256(0, offset, 1),
    }


def write_canonical(root: Path, source) -> None:
    evidence = root / "evidence"
    evidence.mkdir()
    write_jsonl(evidence / "ranges.jsonl", [range_row(source, 8)])
    write_jsonl(
        evidence / "instructions.jsonl",
        [instruction_row(source, 0x1000, 0, "nop")],
    )


def write_incoming(
    root: Path, kind: str, rows: list[dict[str, object]]
) -> Path:
    directory = root / "incoming"
    directory.mkdir(exist_ok=True)
    temporary = directory / f"{kind}.tmp"
    write_jsonl(temporary, rows)
    digest = sha256_bytes(temporary.read_bytes())
    output = directory / f"{kind}-{digest}.jsonl"
    temporary.replace(output)
    return output


def init_repository(root: Path, source) -> str:
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.invalid")
    write_canonical(root, source)
    git(root, "add", "evidence")
    git(root, "commit", "-q", "-m", "canonical evidence")
    return git(root, "rev-parse", "HEAD")


def test_contributor_pr_verifies_only_content_addressed_incoming_files(
    tmp_path: Path, synthetic_source
) -> None:
    base = init_repository(tmp_path, synthetic_source)
    range_path = write_incoming(
        tmp_path, "ranges", [range_row(synthetic_source, 24, 4)]
    )
    instruction_path = write_incoming(
        tmp_path,
        "instructions",
        [instruction_row(synthetic_source, 0x1010, 16, "mov d0,d1")],
    )
    git(tmp_path, "add", "incoming")
    git(tmp_path, "commit", "-q", "-m", "propose evidence")

    report = check_contribution(tmp_path, base, synthetic_source)
    assert report.files == 2
    assert report.new_ranges == 1
    assert report.new_instructions == 1
    assert report.instruction_decodes_to_review == 1
    assert load_evidence(tmp_path) == EvidenceCounts(1, 1)
    assert range_path.is_file() and instruction_path.is_file()


def test_contribution_rejects_canonical_edits_and_filename_tampering(
    tmp_path: Path, synthetic_source
) -> None:
    base = init_repository(tmp_path, synthetic_source)
    path = write_incoming(tmp_path, "ranges", [range_row(synthetic_source, 24)])
    path.write_text(path.read_text() + "\n", encoding="utf-8")
    with pytest.raises(ContributionError, match="filename digest mismatch"):
        check_contribution(tmp_path, base, synthetic_source)

    path.unlink()
    write_incoming(tmp_path, "ranges", [range_row(synthetic_source, 24)])
    (tmp_path / "evidence" / "ranges.jsonl").write_text(
        (tmp_path / "evidence" / "ranges.jsonl").read_text() + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ContributionError, match="modified canonical"):
        check_contribution(tmp_path, base, synthetic_source)


def test_maintainer_accepts_independent_files_by_set_union_and_consumes_them(
    tmp_path: Path, synthetic_source
) -> None:
    write_canonical(tmp_path, synthetic_source)
    first = write_incoming(
        tmp_path,
        "ranges",
        [range_row(synthetic_source, 8), range_row(synthetic_source, 24)],
    )
    second = write_incoming(
        tmp_path,
        "instructions",
        [
            instruction_row(synthetic_source, 0x1000, 0, "nop"),
            instruction_row(synthetic_source, 0x1010, 16, "mov d0,d1"),
        ],
    )

    report = accept_contribution(
        tmp_path,
        synthetic_source,
        [Path("incoming") / first.name, Path("incoming") / second.name],
    )
    assert report.new_ranges == 1 and report.duplicate_ranges == 1
    assert report.new_instructions == 1 and report.duplicate_instructions == 1
    assert load_evidence(tmp_path) == EvidenceCounts(2, 2)
    assert not first.exists() and not second.exists()


def test_instruction_disagreement_fails_before_canonical_mutation(
    tmp_path: Path, synthetic_source
) -> None:
    write_canonical(tmp_path, synthetic_source)
    before = (tmp_path / "evidence" / "instructions.jsonl").read_bytes()
    conflict = write_incoming(
        tmp_path,
        "instructions",
        [instruction_row(synthetic_source, 0x1000, 0, "different decode")],
    )
    with pytest.raises(ContributionError, match="instruction conflict"):
        accept_contribution(tmp_path, synthetic_source, [conflict])
    assert (tmp_path / "evidence" / "instructions.jsonl").read_bytes() == before
    assert conflict.exists()


def test_contribution_rejects_encoded_firmware_payload_in_instruction_text(
    tmp_path: Path, synthetic_source
) -> None:
    write_canonical(tmp_path, synthetic_source)
    payload = synthetic_source.blocks[0][0:8].hex()
    leak = write_incoming(
        tmp_path,
        "instructions",
        [instruction_row(synthetic_source, 0x1010, 16, payload)],
    )
    with pytest.raises(ContributionError, match="contiguous-hex"):
        accept_contribution(tmp_path, synthetic_source, [leak])
    assert leak.exists()


def test_contribution_commands_are_wired_end_to_end(
    tmp_path: Path, synthetic_source, monkeypatch, capsys
) -> None:
    base = init_repository(tmp_path, synthetic_source)
    incoming = write_incoming(
        tmp_path, "ranges", [range_row(synthetic_source, 24)]
    )
    git(tmp_path, "add", "incoming")
    git(tmp_path, "commit", "-q", "-m", "propose range")
    monkeypatch.setattr(cli, "verify_source", lambda _path: synthetic_source)

    checked = cli.main(
        [
            "check-contribution",
            "--base",
            base,
            "--source",
            "unused.bin",
            "--root",
            str(tmp_path),
        ]
    )
    assert checked == 0
    assert "PASS: 1 contribution file(s)" in capsys.readouterr().out

    accepted = cli.main(
        [
            "accept-contribution",
            "--source",
            "unused.bin",
            "--root",
            str(tmp_path),
            str(incoming),
        ]
    )
    assert accepted == 0
    assert "ACCEPTED: 1 contribution file(s)" in capsys.readouterr().out
    assert load_evidence(tmp_path) == EvidenceCounts(2, 1)
