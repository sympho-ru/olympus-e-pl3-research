from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from epl3_research import cli
from epl3_research.source import (
    BlockIdentity,
    SourceRegistry,
    SourceVerificationError,
    source_checksum,
    verify_source,
)


def header(body_length: int, checksum: int) -> bytes:
    value = bytearray(32)
    value[0:2] = b"OE"
    value[2:4] = b"E0"
    value[8:12] = (0x1000).to_bytes(4, "little")
    value[12:16] = body_length.to_bytes(4, "little")
    value[16:18] = (0x0160).to_bytes(2, "little")
    value[20:22] = (0).to_bytes(2, "little")
    value[28:32] = checksum.to_bytes(4, "little")
    return bytes(value)


def fake_source(tmp_path: Path) -> tuple[Path, SourceRegistry, bytes]:
    body = b"synthetic-block!"  # 16 bytes; no vendor material.
    head = header(len(body), 0)
    checksum = source_checksum(head + body + head[:-4])
    image = head + body + header(len(body), checksum)
    path = tmp_path / "SYNTHETIC.BIN"
    path.write_bytes(image)
    registry = SourceRegistry(
        schema="epl3-source/v1",
        source_id="synthetic",
        filename=path.name,
        size=len(image),
        sha256=hashlib.sha256(image).hexdigest(),
        blocks=(BlockIdentity(0, len(body), hashlib.sha256(body).hexdigest()),),
    )
    return path, registry, body


def test_verify_source_accepts_exact_container(tmp_path: Path) -> None:
    path, registry, body = fake_source(tmp_path)
    verified = verify_source(path, registry)
    assert verified.blocks == (body,)


def test_verify_source_reports_filename_size_and_hash(tmp_path: Path) -> None:
    path, registry, _ = fake_source(tmp_path)
    renamed = path.with_name("WRONG.BIN")
    renamed.write_bytes(path.read_bytes())
    with pytest.raises(SourceVerificationError, match="filename: expected SYNTHETIC.BIN, actual WRONG.BIN"):
        verify_source(renamed, registry)

    path.write_bytes(path.read_bytes()[:-1])
    with pytest.raises(SourceVerificationError, match=r"size: expected 80, actual 79"):
        verify_source(path, registry)

    path, registry, _ = fake_source(tmp_path)
    changed = bytearray(path.read_bytes())
    changed[32] ^= 1
    path.write_bytes(changed)
    with pytest.raises(SourceVerificationError, match="source SHA-256: expected"):
        verify_source(path, registry)


def test_verify_source_reports_decoded_block_identity(tmp_path: Path) -> None:
    path, registry, _ = fake_source(tmp_path)
    wrong = SourceRegistry(
        registry.schema,
        registry.source_id,
        registry.filename,
        registry.size,
        registry.sha256,
        (BlockIdentity(0, registry.blocks[0].size, "0" * 64),),
    )
    with pytest.raises(SourceVerificationError, match="decoded block 0 SHA-256"):
        verify_source(path, wrong)


@pytest.mark.parametrize("offset", ["8", "0x8"])
def test_source_range_cli_accepts_decimal_and_hex_without_emitting_bytes(
    tmp_path: Path, synthetic_source, monkeypatch, capsys, offset: str
) -> None:
    monkeypatch.setattr(cli, "verify_source", lambda _path: synthetic_source)
    before = set(tmp_path.iterdir())
    result = cli.main(
        [
            "source-range",
            "--image",
            "unused.bin",
            "--block",
            "0",
            "--offset",
            offset,
            "--length",
            "16",
        ]
    )
    output = capsys.readouterr().out
    value = __import__("json").loads(output)
    assert result == 0
    assert set(value) == {"block", "offset", "length", "sha256"}
    assert value["offset"] == 8
    assert value["length"] == 16
    assert value["sha256"] == hashlib.sha256(
        synthetic_source.blocks[0][8:24]
    ).hexdigest()
    assert synthetic_source.blocks[0][8:24].hex() not in output
    assert set(tmp_path.iterdir()) == before


def test_source_range_cli_rejects_out_of_bounds_slice(
    synthetic_source, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(cli, "verify_source", lambda _path: synthetic_source)
    result = cli.main(
        [
            "source-range",
            "--image",
            "unused.bin",
            "--block",
            "0",
            "--offset",
            "0xffff",
            "--length",
            "1",
        ]
    )
    assert result == 2
    assert "slice outside block" in capsys.readouterr().err


def test_extract_blocks_cli_writes_only_verified_private_blocks(
    tmp_path: Path, synthetic_source, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(cli, "verify_source", lambda _path: synthetic_source)
    monkeypatch.setattr(cli, "project_root", lambda: tmp_path)
    output = tmp_path / ".private" / "decoded"

    result = cli.main(
        [
            "extract-blocks",
            "--image",
            "unused.bin",
            "--output",
            str(output),
        ]
    )

    stdout = capsys.readouterr().out
    report = json.loads(stdout)
    assert result == 0
    assert (output / "block-0.bin").read_bytes() == synthetic_source.blocks[0]
    assert report == {
        "blocks": [
            {
                "block": 0,
                "file": "block-0.bin",
                "sha256": hashlib.sha256(synthetic_source.blocks[0]).hexdigest(),
                "size": len(synthetic_source.blocks[0]),
            }
        ],
        "verified": True,
    }
    assert synthetic_source.blocks[0].hex() not in stdout


def test_extract_blocks_cli_rejects_public_repository_output(
    tmp_path: Path, synthetic_source, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(cli, "verify_source", lambda _path: synthetic_source)
    monkeypatch.setattr(cli, "project_root", lambda: tmp_path)
    output = tmp_path / "decoded"

    result = cli.main(
        [
            "extract-blocks",
            "--image",
            "unused.bin",
            "--output",
            str(output),
        ]
    )

    assert result == 2
    assert "must be written under .private" in capsys.readouterr().err
    assert not output.exists()


def test_extract_blocks_cli_never_overwrites_existing_block(
    tmp_path: Path, synthetic_source, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(cli, "verify_source", lambda _path: synthetic_source)
    monkeypatch.setattr(cli, "project_root", lambda: tmp_path)
    output = tmp_path / ".private" / "decoded"
    output.mkdir(parents=True)
    existing = output / "block-0.bin"
    existing.write_bytes(b"keep me")

    result = cli.main(
        [
            "extract-blocks",
            "--image",
            "unused.bin",
            "--output",
            str(output),
        ]
    )

    assert result == 2
    assert "refusing to overwrite" in capsys.readouterr().err
    assert existing.read_bytes() == b"keep me"
