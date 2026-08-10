from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any


HEADER_SIZE = 0x20
SCRAMBLED_FLAGS = frozenset({0x0100, 0x0101, 0x0102, 0x0103, 0x0104, 0x0105, 0x0106})
DESCRAMBLE_ORDER = (1, 3, 0, 2, 6, 4, 7, 5, 11, 10, 9, 8, 13, 14, 12, 15)
XOR_FF = bytes(value ^ 0xFF for value in range(256))


class SourceVerificationError(ValueError):
    """The supplied source does not match the closed source registry."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True)
class BlockIdentity:
    index: int
    size: int
    sha256: str


@dataclass(frozen=True)
class SourceRegistry:
    schema: str
    source_id: str
    filename: str
    size: int
    sha256: str
    blocks: tuple[BlockIdentity, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SourceRegistry":
        container = value["container"]
        return cls(
            schema=str(value["schema"]),
            source_id=str(value["source_id"]),
            filename=str(container["filename"]),
            size=int(container["size"]),
            sha256=str(container["sha256"]),
            blocks=tuple(
                BlockIdentity(int(item["index"]), int(item["size"]), str(item["sha256"]))
                for item in value["blocks"]
            ),
        )


def load_registry() -> SourceRegistry:
    resource = files("epl3_research").joinpath("data/source.json")
    return SourceRegistry.from_dict(json.loads(resource.read_text(encoding="utf-8")))


@dataclass(frozen=True)
class VerifiedSource:
    registry: SourceRegistry
    image_path: Path
    image_sha256: str
    blocks: tuple[bytes, ...]

    def validate_range(self, block: int, offset: int, length: int) -> None:
        if block < 0 or block >= len(self.blocks):
            raise SourceVerificationError(f"unknown decoded block {block}")
        if offset < 0 or length < 1 or offset + length > len(self.blocks[block]):
            raise SourceVerificationError(
                f"slice outside block {block}: offset={offset}, length={length}, size={len(self.blocks[block])}"
            )

    def slice_sha256(self, block: int, offset: int, length: int) -> str:
        self.validate_range(block, offset, length)
        return sha256_bytes(self.blocks[block][offset : offset + length])


@dataclass(frozen=True)
class Header:
    signature: bytes
    model: bytes
    unknown1: bytes
    load_address: int
    body_length: int
    version: int
    unknown2: bytes
    flags: int
    unknown3: bytes
    checksum: int

    @classmethod
    def parse(cls, value: bytes) -> "Header":
        if len(value) != HEADER_SIZE:
            raise SourceVerificationError(
                f"header size mismatch: expected {HEADER_SIZE}, actual {len(value)}"
            )
        return cls(
            signature=value[0:2],
            model=value[2:4],
            unknown1=value[4:8],
            load_address=int.from_bytes(value[8:12], "little"),
            body_length=int.from_bytes(value[12:16], "little"),
            version=int.from_bytes(value[16:18], "little"),
            unknown2=value[18:20],
            flags=int.from_bytes(value[20:22], "little"),
            unknown3=value[22:28],
            checksum=int.from_bytes(value[28:32], "little"),
        )

    def without_checksum(self) -> tuple[object, ...]:
        return (
            self.signature,
            self.model,
            self.unknown1,
            self.load_address,
            self.body_length,
            self.version,
            self.unknown2,
            self.flags,
            self.unknown3,
        )


def descramble(source: bytes) -> bytes:
    if len(source) % 16:
        raise SourceVerificationError(
            f"scrambled body length must be a multiple of 16; actual {len(source)}"
        )
    output = bytearray(len(source))
    for output_lane, source_lane in enumerate(DESCRAMBLE_ORDER):
        output[output_lane::16] = source[source_lane::16].translate(XOR_FF)
    return bytes(output)


def source_checksum(value: bytes) -> int:
    if len(value) % 4:
        raise SourceVerificationError(
            f"checksum input must be a multiple of 4; actual {len(value)}"
        )
    if sys.byteorder == "little":
        words = memoryview(value).cast("I")
        return (-sum(words)) & 0xFFFFFFFF
    total = 0
    for offset in range(0, len(value), 4):
        total = (total - int.from_bytes(value[offset : offset + 4], "little")) & 0xFFFFFFFF
    return total


def decode_container(value: bytes) -> tuple[bytes, ...]:
    blocks: list[bytes] = []
    position = 0
    while position < len(value):
        index = len(blocks)
        if len(value) - position < HEADER_SIZE:
            raise SourceVerificationError(
                f"container block {index} truncated header at 0x{position:x}"
            )
        header_bytes = value[position : position + HEADER_SIZE]
        header = Header.parse(header_bytes)
        body_start = position + HEADER_SIZE
        body_end = body_start + header.body_length
        tail_end = body_end + HEADER_SIZE
        if tail_end > len(value):
            raise SourceVerificationError(
                f"container block {index} exceeds file: expected end 0x{tail_end:x}, actual 0x{len(value):x}"
            )
        tail_bytes = value[body_end:tail_end]
        tail = Header.parse(tail_bytes)
        if header.without_checksum() != tail.without_checksum():
            raise SourceVerificationError(f"container block {index} header/tail mismatch")
        if header.checksum != 0:
            raise SourceVerificationError(
                f"container block {index} header checksum: expected 0x00000000, actual 0x{header.checksum:08x}"
            )
        if header.flags and header.flags not in SCRAMBLED_FLAGS:
            raise SourceVerificationError(
                f"container block {index} flags: expected known flag, actual 0x{header.flags:04x}"
            )
        encoded = value[body_start:body_end]
        decoded = descramble(encoded) if header.flags else encoded
        actual_checksum = source_checksum(header_bytes + decoded + tail_bytes[:-4])
        if actual_checksum != tail.checksum:
            raise SourceVerificationError(
                f"container block {index} checksum: expected 0x{tail.checksum:08x}, actual 0x{actual_checksum:08x}"
            )
        blocks.append(decoded)
        position = tail_end
    if position != len(value):
        raise SourceVerificationError(
            f"container end mismatch: expected {len(value)}, actual {position}"
        )
    return tuple(blocks)


def verify_source(path: Path, registry: SourceRegistry | None = None) -> VerifiedSource:
    registry = registry or load_registry()
    actual_name = path.name
    if actual_name != registry.filename:
        raise SourceVerificationError(
            f"source filename: expected {registry.filename}, actual {actual_name}"
        )
    try:
        value = path.read_bytes()
    except OSError as error:
        raise SourceVerificationError(f"cannot read source {path}: {error}") from error
    if len(value) != registry.size:
        raise SourceVerificationError(
            f"source size: expected {registry.size}, actual {len(value)}"
        )
    actual_sha256 = sha256_bytes(value)
    if actual_sha256 != registry.sha256:
        raise SourceVerificationError(
            f"source SHA-256: expected {registry.sha256}, actual {actual_sha256}"
        )
    blocks = decode_container(value)
    if len(blocks) != len(registry.blocks):
        raise SourceVerificationError(
            f"decoded block count: expected {len(registry.blocks)}, actual {len(blocks)}"
        )
    for identity, block in zip(registry.blocks, blocks, strict=True):
        if identity.index < 0 or identity.index >= len(blocks):
            raise SourceVerificationError(f"invalid registry block index {identity.index}")
        if len(block) != identity.size:
            raise SourceVerificationError(
                f"decoded block {identity.index} size: expected {identity.size}, actual {len(block)}"
            )
        actual_block_sha256 = sha256_bytes(block)
        if actual_block_sha256 != identity.sha256:
            raise SourceVerificationError(
                f"decoded block {identity.index} SHA-256: expected {identity.sha256}, actual {actual_block_sha256}"
            )
    return VerifiedSource(registry, path, actual_sha256, blocks)


def source_summary(source: VerifiedSource) -> dict[str, object]:
    return {
        "source": source.registry.source_id,
        "image": {
            "filename": source.image_path.name,
            "size": source.registry.size,
            "sha256": source.image_sha256,
        },
        "blocks": [
            {
                "index": identity.index,
                "size": identity.size,
                "sha256": identity.sha256,
            }
            for identity in source.registry.blocks
        ],
        "verified": True,
    }
