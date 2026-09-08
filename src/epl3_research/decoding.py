"""Byte-free MN103 decode reports; successful decoding is not path reachability."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from .evidence import InstructionRow, instruction_object
from .source import VerifiedSource

# GNU binutils 2.45 opcodes/m10300-dis.c: FMT_D9 and the longest forms
# consume seven bytes. Lookahead comes from the architecture, not row length.
MAX_INSTRUCTION_BYTES = 7


def row_id(row: InstructionRow) -> str:
    return hashlib.sha256(json.dumps(instruction_object(row), sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def normalized_text(text: str) -> str:
    return " ".join(text.split())


@dataclass(frozen=True)
class Instruction:
    address: int
    data: bytes
    text: str


def parse_disassembly(output: str) -> list[Instruction]:
    """Join objdump continuation lines and reject broken byte coverage."""
    result: list[Instruction] = []
    for line in output.splitlines():
        match = re.match(r"^\s*([0-9a-fA-F]+):\s*(.*)$", line)
        if not match:
            continue
        address = int(match[1], 16)
        # Tabs separate byte display from mnemonic; continuation lines have no text.
        fields = match[2].split("\t", 1)
        raw = fields[0].strip()
        if re.fullmatch(r"Address 0x[0-9a-fA-F]+ is out of bounds\.", raw):
            break  # Partial lookahead at the end is not an instruction.
        if not re.fullmatch(r"[0-9a-fA-F]{2}(?:\s+[0-9a-fA-F]{2})*", raw):
            raise ValueError("unrecognized objdump byte column")
        data = bytes.fromhex(raw)
        text = fields[1].strip() if len(fields) == 2 else ""
        if text:
            result.append(Instruction(address, data, normalized_text(text)))
        else:
            if not result or result[-1].address + len(result[-1].data) != address:
                raise ValueError("orphan or noncontiguous objdump continuation")
            previous = result.pop()
            result.append(Instruction(previous.address, previous.data + data, previous.text))
    return result


class Decoder:
    def __init__(self, source: VerifiedSource, executable: str | None = None):
        self.source = source
        requested = executable or os.environ.get("MN103_OBJDUMP", "mn10300-elf-objdump")
        self.executable = shutil.which(requested)
        if not self.executable:
            raise ValueError("MN103 objdump missing; set MN103_OBJDUMP or --objdump")
        self.version = self._run("--version").splitlines()[0]
        if self.version != "GNU objdump (GNU Binutils) 2.45":
            raise ValueError("decode verification requires GNU objdump 2.45")
        targets = self._run("-i")
        if "mn10300" not in targets or "binary" not in targets:
            raise ValueError("objdump lacks MN103/binary support")
        self.tool_sha256 = hashlib.sha256(Path(self.executable).read_bytes()).hexdigest()

    def _run(self, *args: str) -> str:
        env = dict(os.environ, LC_ALL="C")
        result = subprocess.run([self.executable, *args], capture_output=True, text=True, env=env)
        if result.returncode:
            # Tool diagnostics can contain private paths or firmware bytes.
            raise ValueError(f"objdump failed with exit code {result.returncode}")
        return result.stdout

    def window(self, block: int, offset: int, address: int, length: int) -> list[Instruction]:
        self.source.validate_range(block, offset, length)
        data = self.source.blocks[block][offset:offset + length]
        with tempfile.NamedTemporaryFile() as window:
            window.write(data)
            window.flush()
            output = self._run("-D", "-z", "-b", "binary", "-m", "mn10300",
                               "--insn-width=16", f"--adjust-vma={address}", window.name)
        decoded = parse_disassembly(output)
        cursor = address
        for item in decoded:
            start = item.address - address
            if item.address != cursor or item.data != data[start:start + len(item.data)]:
                raise ValueError("objdump output does not match contiguous source bytes")
            cursor += len(item.data)
        return decoded


def overlaps(rows: tuple[InstructionRow, ...], minimum_length: int = 0) -> list[tuple[InstructionRow, InstructionRow]]:
    """Source intersections, including different mappings and different lengths."""
    groups: dict[int, list[InstructionRow]] = defaultdict(list)
    for row in set(rows):
        groups[row[2]].append(row)
    pairs = []
    for group in groups.values():
        active: list[InstructionRow] = []
        for row in sorted(group, key=lambda r: (r[3], r)):
            active = [old for old in active if old[3] + max(old[4], minimum_length) > row[3]]
            pairs.extend((old, row) for old in active)
            active.append(row)
    return pairs


def verify_instructions(source: VerifiedSource, rows: tuple[InstructionRow, ...],
                        canonical: tuple[InstructionRow, ...] = (), *,
                        executable: str | None = None) -> dict:
    """Decode contiguous submitted spans plus complete lookahead; inspect overlaps.

    Starts are hypotheses. Interior starts are reproduced separately, never
    silently promoted to boundaries on the surrounding instruction stream.
    """
    selected = set(rows)
    pairs = [(a, b) for a, b in overlaps(tuple(selected | set(canonical)), MAX_INSTRUCTION_BYTES)
             if a in selected or b in selected]
    neighbors = {r for pair in pairs for r in pair} - selected
    targets = selected | neighbors
    decoder = Decoder(source, executable) if targets else None
    decoded: dict[tuple[int, int, int], Instruction] = {}
    groups: dict[tuple[int, int], list[InstructionRow]] = defaultdict(list)
    for row in targets:
        if row[2] != 0:
            raise ValueError("MN103 verification currently supports block 0 only; other architectures require a separate verifier")
        source.validate_range(row[2], row[3], row[4])
        groups[(row[2], row[0] - row[3])].append(row)
    for (block, mapping), group in sorted(groups.items()):
        ordered = sorted(group, key=lambda r: r[3])
        # Merge touching cited intervals to decode actual surrounding streams.
        spans: list[list[int]] = []
        for row in ordered:
            start, end = row[3], row[3] + row[4]
            if spans and start <= spans[-1][1]:
                spans[-1][1] = max(spans[-1][1], end)
            else:
                spans.append([start, end])
        for start, end in spans:
            end = min(len(source.blocks[block]), end + MAX_INSTRUCTION_BYTES - 1)
            for item in decoder.window(block, start, start + mapping, end - start):
                decoded[(block, item.address - mapping, item.address)] = item
        for row in ordered:
            key = (block, row[3], row[0])
            if key not in decoded:
                # An operand-interior hypothesis must be decoded independently.
                length = min(MAX_INSTRUCTION_BYTES, len(source.blocks[block]) - row[3])
                items = decoder.window(block, row[3], row[0], length)
                if items:
                    decoded[key] = items[0]
    # Use observed widths as well as recorded widths: a stale short predecessor
    # can hide an interior start beyond its recorded endpoint.
    def extent(row):
        item = decoded.get((row[2], row[3], row[0]))
        return row[3] + max(row[4], len(item.data) if item else 0)
    pairs = [(a, b) for a, b in pairs if a[3] < extent(b) and b[3] < extent(a)]
    relevant = selected | {r for pair in pairs for r in pair}
    results = []
    for row in sorted(relevant):
        item = decoded.get((row[2], row[3], row[0]))
        reasons = []
        if source.slice_sha256(row[2], row[3], row[4]) != row[5]:
            reasons.append("source_digest_mismatch")
        if not item or item.text.startswith(".") or "unknown" in item.text.lower():
            reasons.append("not_an_instruction")
        if item and len(item.data) != row[4]:
            reasons.append("length_mismatch")
        if item and item.text != normalized_text(row[1]):
            reasons.append("text_mismatch")
        results.append({"row": instruction_object(row), "row_id": row_id(row),
                        "role": "submitted" if row in selected else "overlapping_canonical",
                        "status": "fail" if reasons else "pass", "reasons": reasons,
                        "observed_length": len(item.data) if item else None,
                        "observed_instruction": item.text if item else None})
    return {"schema": "epl3-decode-screen/v1",
            "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source_id": source.registry.source_id,
            "source_sha256": source.image_sha256, "architecture": "mn10300",
            "tool": decoder.version if decoder else None,
            "tool_sha256": decoder.tool_sha256 if decoder else None,
            "boundary_status": "decode_only_start_anchors_not_proven",
            "results": results,
            "overlaps": [{"rows": sorted([row_id(a), row_id(b)]),
                          "kind": "same_start" if a[3] == b[3] else "interior_start"}
                         for a, b in pairs]}


def require_verified(report: dict, review_path: Path | None = None) -> None:
    failures = [r for r in report["results"] if r["status"] != "pass"]
    if failures:
        first = failures[0]
        raise ValueError(f"decode verification failed for {len(failures)} row(s); "
                         f"first address={first['row']['address']}: {','.join(first['reasons'])}; "
                         "run screen-instructions for the report")
    expected = {tuple(item["rows"]) for item in report["overlaps"]}
    reviewed = set()
    if review_path is not None:
        value = json.loads(review_path.read_text())
        if not isinstance(value, dict) or set(value) != {"overlaps"} or not isinstance(value["overlaps"], list):
            raise ValueError("overlap review must contain an overlaps list")
        for entry in value["overlaps"]:
            if (not isinstance(entry, dict) or set(entry) != {"rows", "reason"}
                    or not isinstance(entry["reason"], str) or not entry["reason"].strip()
                    or not isinstance(entry["rows"], list) or len(entry["rows"]) != 2
                    or any(not isinstance(r, str) or not re.fullmatch('[0-9a-f]{64}', r) for r in entry["rows"])):
                raise ValueError("overlap review needs exact row IDs and a nonempty reason")
            pair = tuple(sorted(entry["rows"]))
            if pair in reviewed:
                raise ValueError("duplicate overlap review")
            reviewed.add(pair)
    if reviewed - expected:
        raise ValueError("stale or unrelated overlap review")
    if expected - reviewed:
        raise ValueError(f"{len(expected - reviewed)} overlap(s) require explicit adjudication; "
                         "run screen-instructions and supply --overlap-review")
