from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

import pytest

from epl3_research.audit import (
    audit_git_history,
    audit_tree,
    load_private_terms,
    text_candidates,
)


PAYLOAD = bytes.fromhex("d31f8a72b405e96c47fa108d62ce395b")


def git(root: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )


def init_git(root: Path) -> None:
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.invalid")


@pytest.mark.parametrize(
    ("name", "content", "representation"),
    [
        ("sample.txt", PAYLOAD.hex(), "contiguous-hex"),
        ("sample.txt", base64.b64encode(PAYLOAD).decode(), "base64"),
        ("sample.txt", "".join(f"\\x{value:02x}" for value in PAYLOAD), "python-byte-escape"),
        ("sample.py", f'bytes.fromhex("{PAYLOAD.hex()}")', "python-bytes-fromhex"),
        ("sample.json", json.dumps(list(PAYLOAD)), "integer-byte-array"),
    ],
)
def test_each_declared_text_decoder_finds_source_bytes(
    tmp_path: Path, synthetic_source, name: str, content: str, representation: str
) -> None:
    (tmp_path / name).write_text(content, encoding="utf-8")
    findings = audit_tree(tmp_path, synthetic_source)
    assert representation in {item.representation for item in findings}


def test_binary_and_archive_policy_is_content_independent(tmp_path: Path, synthetic_source) -> None:
    (tmp_path / "payload.bin").write_bytes(PAYLOAD)
    assert "binary-or-archive" in {
        item.representation for item in audit_tree(tmp_path, synthetic_source)
    }


def test_benign_controls_and_plain_ascii_identifier_are_out_of_scope(
    tmp_path: Path, synthetic_source
) -> None:
    identifier = "BIPOP_GET_LINKED_THUMBNAIL"
    (tmp_path / "safe.json").write_text(
        json.dumps(
            {
                "address_hex": "0x00100020",
                "sha256": "0" * 64,
                "functional_identifier": identifier,
            }
        ),
        encoding="utf-8",
    )
    assert list(text_candidates(identifier)) == []
    assert audit_tree(tmp_path, synthetic_source) == []


def test_raw_carrier_is_rejected_without_source(tmp_path: Path) -> None:
    (tmp_path / "unsafe.json").write_text(
        json.dumps({"bytes_hex": "d31f"}), encoding="utf-8"
    )
    assert "raw-carrier-field" in {item.representation for item in audit_tree(tmp_path)}


def test_private_terms_are_case_insensitive_and_diagnostics_are_redacted(
    tmp_path: Path, synthetic_source
) -> None:
    private = tmp_path / ".private"
    private.mkdir()
    term_file = private / "terms.txt"
    term_file.write_text("# local only\nInternalProjectCodename\n", encoding="utf-8")
    terms = load_private_terms(term_file)
    (tmp_path / "note.txt").write_text("internalprojectcodename", encoding="utf-8")
    findings = audit_tree(tmp_path, synthetic_source, terms)
    matches = [item for item in findings if item.representation == "configured-private-term"]
    assert len(matches) == 1
    assert "InternalProjectCodename" not in matches[0].render()
    assert "internalprojectcodename" not in matches[0].render()


@pytest.mark.parametrize(
    "text",
    [
        "/" + "Volumes" + "/project/file.txt",
        "/" + "Users" + "/person/file.txt",
        "/" + "home" + "/person/file.txt",
        "/" + "private" + "/scratch/file.txt",
        "/" + "tmp" + "/scratch/file.txt",
        "/" + "var" + "/folders/xx/file.txt",
        "C:" + chr(92) + "work" + chr(92) + "file.txt",
        chr(92) * 2 + "server" + chr(92) + "share" + chr(92) + "file.txt",
    ],
)
def test_high_confidence_workstation_paths_are_rejected(
    tmp_path: Path, synthetic_source, text: str
) -> None:
    (tmp_path / "note.txt").write_text(text, encoding="utf-8")
    assert "private-absolute-path" in {
        item.representation for item in audit_tree(tmp_path, synthetic_source)
    }


def test_relative_urls_and_firmware_internal_paths_are_benign(
    tmp_path: Path, synthetic_source
) -> None:
    volume_url = "https://example.invalid/" + "Volumes" + "/archive"
    user_url = "https://example.invalid/" + "Users" + "/guide"
    (tmp_path / "note.txt").write_text(
        "\n".join(("relative/path.txt", volume_url, user_url, "/firmware/internal/resource")),
        encoding="utf-8",
    )
    assert audit_tree(tmp_path, synthetic_source) == []


def test_ignored_desktop_metadata_is_skipped_but_force_tracked_binary_fails(
    tmp_path: Path, synthetic_source
) -> None:
    init_git(tmp_path)
    (tmp_path / ".gitignore").write_text(".DS_Store\n", encoding="utf-8")
    metadata = tmp_path / ".DS_Store"
    metadata.write_bytes(bytes((0, 255)))
    assert audit_tree(tmp_path, synthetic_source) == []
    git(tmp_path, "add", "-f", ".DS_Store")
    assert "binary-or-archive" in {
        item.representation for item in audit_tree(tmp_path, synthetic_source)
    }


def test_history_audit_is_limited_to_current_head(
    tmp_path: Path, synthetic_source
) -> None:
    init_git(tmp_path)
    clean = tmp_path / "clean.txt"
    clean.write_text("clean public record\n", encoding="utf-8")
    git(tmp_path, "add", "clean.txt")
    git(tmp_path, "commit", "-q", "-m", "clean base")

    git(tmp_path, "switch", "-q", "-c", "agent-side")
    leak = tmp_path / "candidate.txt"
    leak.write_text(PAYLOAD.hex() + " InternalProjectCodename\n", encoding="utf-8")
    git(tmp_path, "add", "candidate.txt")
    git(tmp_path, "commit", "-q", "-m", "unmerged candidate")

    git(tmp_path, "switch", "-q", "main")
    assert audit_git_history(tmp_path, synthetic_source, ("internalprojectcodename",)) == []

    git(tmp_path, "switch", "-q", "agent-side")
    representations = {
        item.representation
        for item in audit_git_history(
            tmp_path, synthetic_source, ("internalprojectcodename",)
        )
    }
    assert "contiguous-hex" in representations
    assert "configured-private-term" in representations
