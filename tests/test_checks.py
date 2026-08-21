from __future__ import annotations

import json
import subprocess
from pathlib import Path

from epl3_research.checks import run_checks
from epl3_research.evidence import EvidenceCounts, load_evidence


ROOT = Path(__file__).resolve().parents[1]


def make_project(root: Path, synthetic_source) -> None:
    contents = {
        ".gitignore": ".private/\n",
        "README.md": (
            "This distribution contains no Olympus firmware image.\n"
            "This project is not endorsed by OM Digital Solutions or Olympus.\n"
        ),
        "AUTHORS.md": "# Authors\n\n- Fixture Author\n",
        "LICENSE": "Apache License\nVersion 2.0\n",
        "LICENSE-DOCUMENTATION": "CC BY 4.0 evidence metadata AUTHORS.md\n",
        "CONTRIBUTING.md": "public fixture\n",
        "pyproject.toml": 'license = {text = "Apache-2.0"}\n',
    }
    for name, content in contents.items():
        (root / name).write_text(content, encoding="utf-8")
    docs = root / "docs"
    docs.mkdir()
    for name in (
        "ANALYSIS.md",
        "EVIDENCE.md",
        "FIRMWARE_MAP.md",
        "OBTAINING_FIRMWARE.md",
        "RESEARCH.md",
    ):
        (docs / name).write_text("public fixture\n", encoding="utf-8")
    evidence = root / "evidence"
    evidence.mkdir()
    (evidence / "ranges.jsonl").write_text(
        json.dumps(
            {
                "block": 0,
                "offset": 8,
                "length": 16,
                "sha256": synthetic_source.slice_sha256(0, 8, 16),
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
    (evidence / "instructions.jsonl").write_text(
        '{"address":1,"instruction":"nop","block":0,"offset":0,"length":1,'
        '"sha256":"' + synthetic_source.slice_sha256(0, 0, 1) + '"}\n',
        encoding="utf-8",
    )


def default_terms(root: Path, contents: str = "NeverPublishThisName\n") -> Path:
    directory = root / ".private"
    directory.mkdir(exist_ok=True)
    path = directory / "release-denylist.txt"
    path.write_text(contents, encoding="utf-8")
    return path


def git(root: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
    )


def initialize_git(root: Path, *, commit: bool) -> None:
    git(root, "init", "-q")
    if not commit:
        return
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "Fixture Author")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "fixture")


def test_contributor_checks_validate_flat_evidence(
    tmp_path: Path, synthetic_source
) -> None:
    make_project(tmp_path, synthetic_source)
    terms = default_terms(tmp_path)
    structural = run_checks(tmp_path, "structural")
    source_bound = run_checks(
        tmp_path, "source", synthetic_source, private_terms_path=terms
    )
    assert structural.ok
    assert source_bound.ok


def test_release_checks_flat_evidence_and_history(tmp_path: Path, synthetic_source) -> None:
    make_project(tmp_path, synthetic_source)
    initialize_git(tmp_path, commit=True)
    default_terms(tmp_path)
    result = run_checks(tmp_path, "release", synthetic_source)
    assert result.ok
    assert result.history_scanned


def test_release_rejects_non_git_directory(tmp_path: Path, synthetic_source) -> None:
    make_project(tmp_path, synthetic_source)
    default_terms(tmp_path)

    result = run_checks(tmp_path, "release", synthetic_source)

    assert not result.ok
    assert not result.history_scanned
    assert "cannot audit Git history reachable from HEAD" in result.problems


def test_release_rejects_repository_without_head(
    tmp_path: Path, synthetic_source
) -> None:
    make_project(tmp_path, synthetic_source)
    initialize_git(tmp_path, commit=False)
    default_terms(tmp_path)

    result = run_checks(tmp_path, "release", synthetic_source)

    assert not result.ok
    assert not result.history_scanned
    assert "cannot audit Git history reachable from HEAD" in result.problems


def test_release_rejects_pending_incoming_files(tmp_path: Path, synthetic_source) -> None:
    make_project(tmp_path, synthetic_source)
    initialize_git(tmp_path, commit=True)
    default_terms(tmp_path)
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    (incoming / ("ranges-" + "0" * 64 + ".jsonl")).write_text("proposal\n")
    result = run_checks(tmp_path, "release", synthetic_source)
    assert "release contains 1 pending incoming contribution file(s)" in result.problems


def test_release_private_terms_are_fail_closed(tmp_path: Path, synthetic_source) -> None:
    make_project(tmp_path, synthetic_source)
    initialize_git(tmp_path, commit=True)

    missing = run_checks(tmp_path, "release", synthetic_source)
    assert any("cannot read private-term file" in item for item in missing.problems)

    default_terms(tmp_path, "# comments are not effective\n\n")
    empty = run_checks(tmp_path, "release", synthetic_source)
    assert any("has no effective terms" in item for item in empty.problems)

    opted_out = run_checks(
        tmp_path, "release", synthetic_source, no_private_terms=True
    )
    assert opted_out.ok


def test_default_and_override_private_terms_scan_the_tree(
    tmp_path: Path, synthetic_source
) -> None:
    make_project(tmp_path, synthetic_source)
    initialize_git(tmp_path, commit=True)
    default_terms(tmp_path, "NeverPublishThisName\n")
    (tmp_path / "README.md").write_text("neverpublishthisname\n", encoding="utf-8")
    default_result = run_checks(tmp_path, "release", synthetic_source)
    assert any("configured-private-term" in item for item in default_result.problems)
    assert all("NeverPublishThisName" not in item for item in default_result.problems)

    override = tmp_path / ".private" / "override.txt"
    override.write_text("DifferentPrivateName\n", encoding="utf-8")
    override_result = run_checks(
        tmp_path, "release", synthetic_source, private_terms_path=override
    )
    assert not any("configured-private-term" in item for item in override_result.problems)


def test_public_corpus_retains_the_authenticated_range_and_instruction_data() -> None:
    assert load_evidence(ROOT) == EvidenceCounts(ranges=12420, instructions=39415)
    ranges = {
        (item["block"], item["offset"], item["length"], item["sha256"])
        for item in (
            json.loads(line)
            for line in (ROOT / "evidence" / "ranges.jsonl").read_text().splitlines()
        )
    }
    assert {
        (0, 0x00820000, 30, "28df1ac852d06e22d1d9e551bf3742162a5703bd467140422e90b218f059fac4"),
        (0, 0x00B8211E, 9, "376cb97fc05688293ab81d0e3ca1e2dd8aff8ddaacbd84e9c4296f9bf256f549"),
        (0, 0x00D30841, 423, "82c827858c7edabda470589eb8917419f172967b6ef99b8dec0bed1fad869a70"),
        (0, 0x00D30A45, 88, "b0da7be4133c889bb79a3322c85ded7d9fbdd464e1fb02d532e42a8f5558240e"),
        (0, 0x00D58CE4, 64, "e6b372bff872edb26f7a95e59cf8ac20600b64a88a0bd2fe2441f5238e1c83f0"),
    }.issubset(ranges)
