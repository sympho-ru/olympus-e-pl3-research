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
    assert load_evidence(ROOT) == EvidenceCounts(ranges=17185, instructions=53015)
    ranges = {
        (item["block"], item["offset"], item["length"], item["sha256"])
        for item in (
            json.loads(line)
            for line in (ROOT / "evidence" / "ranges.jsonl").read_text().splitlines()
        )
    }
    assert {
        (0, 0x000000C9, 8, "a85b65a989076dc6134715cca1c83638972f21e909dd7c809a0febf8f63a7e1c"),
        (0, 0x00820000, 30, "28df1ac852d06e22d1d9e551bf3742162a5703bd467140422e90b218f059fac4"),
        (0, 0x00B8211E, 9, "376cb97fc05688293ab81d0e3ca1e2dd8aff8ddaacbd84e9c4296f9bf256f549"),
        (0, 0x00D2D8B1, 6, "37a01e1ccb7b2fdbfe3dd2763c67ece71a6b72ce13d3306e1c7b637282faad95"),
        (0, 0x00D2F6D5, 432, "7d118be63b57e7988289dc3f988e051e37d443eae312fc7dfeb40924e6a029ea"),
        (0, 0x00D30841, 423, "82c827858c7edabda470589eb8917419f172967b6ef99b8dec0bed1fad869a70"),
        (0, 0x00D30A45, 88, "b0da7be4133c889bb79a3322c85ded7d9fbdd464e1fb02d532e42a8f5558240e"),
        (0, 0x00D58CE4, 64, "e6b372bff872edb26f7a95e59cf8ac20600b64a88a0bd2fe2441f5238e1c83f0"),
        (0, 0x007EE993, 72, "fcc6879ab7645e0ff1dd3288e01a9db530ee8447a5949600bf38b39d4cb431ee"),
        (0, 0x007EF127, 97, "9cd48c7b4c46a1f1619e2ebe3d86a4e2d497b4612f60b8a850705eb600ec3583"),
        (0, 0x007ECB2F, 59, "248bb3a90d1401624b7c2e14625550d122e7ad3c057323bd5180a06cef8a1bfb"),
        (0, 0x0081BD5C, 97, "e79ecefb60529e2f10e08a4a630510707d3e383b4b4f22ff950dbc0e7b8b7772"),
        (0, 0x007EB634, 14, "a75f157a18ce9b1d59e1ecc079663518b9e4641f0fb07ff5ba5521b2a65e8515"),
        (0, 0x007F271E, 15, "5b374e4da71e929f55e6adc9d4415cfd8b5a6f48503773cdbb9900e86cb8f969"),
        (0, 0x008F76D8, 8, "89c5202539fac5c0133c4eba27ce56658126dd43dc7de8c875b9a25c7e88b618"),
        (0, 0x008F7718, 4, "5d4a149dd3e30aaea523a0e174d15c12e9d5d96b34d1e5de8ffc00dc0ea67c37"),
        (0, 0x008F7720, 8, "8f259958610dd52cfa92041a434d1facb911b06e14946510095edeaf4f9cd3f0"),
        (1, 0x00000020, 16, "df65e960cbdd0c66d36ccd099ecd424dd6fddbb963390070c31acbcdf5805c59"),
        (4, 0x0000122A, 4, "96641b39a9b61dff06ed20aaaa2005e31c193e281fc69aae5a00edfaa311cfa0"),
    }.issubset(ranges)
