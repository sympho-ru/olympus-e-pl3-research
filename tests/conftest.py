from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from epl3_research.source import BlockIdentity, SourceRegistry, VerifiedSource


@pytest.fixture
def synthetic_source(tmp_path: Path) -> VerifiedSource:
    payload = bytes.fromhex("d31f8a72b405e96c47fa108d62ce395b")
    block = b"prefix--" + payload + b"--middle--" + payload.upper() + b"--suffix"
    registry = SourceRegistry(
        schema="epl3-source/v1",
        source_id="synthetic-source",
        filename="SYNTHETIC.BIN",
        size=0,
        sha256=hashlib.sha256(b"").hexdigest(),
        blocks=(BlockIdentity(0, len(block), hashlib.sha256(block).hexdigest()),),
    )
    return VerifiedSource(registry, tmp_path / "SYNTHETIC.BIN", registry.sha256, (block,))

