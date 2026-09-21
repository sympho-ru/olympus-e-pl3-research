"""Check the public reference's navigation and mechanical evidence references."""

from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import pytest


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = sorted(
    [*ROOT.glob("*.md"), *ROOT.joinpath("docs").rglob("*.md"),
     *ROOT.joinpath("tests/fixtures").rglob("*.md")]
)


def prose(path: Path) -> str:
    # Fenced examples describe a format; their placeholder links are not links.
    return re.sub(r"^```[^\n]*\n.*?^```\s*$", "", path.read_text(), flags=re.M | re.S)


def fragments(text: str) -> set[str]:
    anchors = set(re.findall(r'<a id="([^"]+)"\s*></a>', text))
    counts: Counter[str] = Counter()
    for heading in re.findall(r"^#{1,6} (.+)$", text, re.M):
        name = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts[name]
        counts[name] += 1
        anchors.add(f"{name}-{count}" if count else name)
    return anchors


def test_relative_document_links_and_fragments() -> None:
    problems = []
    for path in DOCUMENTS:
        text = prose(path)
        explicit = re.findall(r'<a id="([^"]+)"\s*></a>', text)
        assert len(explicit) == len(set(explicit)), f"Duplicate anchors in {path}"
        for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", text):
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            destination = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not destination.exists():
                problems.append(f"{path.relative_to(ROOT)}: missing {target}")
            elif url.fragment and destination.suffix == ".md":
                if unquote(url.fragment) not in fragments(prose(destination)):
                    problems.append(f"{path.relative_to(ROOT)}: missing fragment {target}")
    assert not problems, "\n".join(problems)


def test_map_counts_match_canonical_evidence() -> None:
    text = (ROOT / "docs/FIRMWARE_MAP.md").read_text()
    table = text.split("## Canonical coverage\n", 1)[1].split("\n## ", 1)[0]
    published = {
        int(block): (int(ranges.replace(",", "")), int(instructions.replace(",", "")))
        for block, ranges, instructions in re.findall(
            r"^\| (\d+) \| ([\d,]+) \| ([\d,]+) \|$", table, re.M
        )
    }
    actual = []
    for name in ("ranges", "instructions"):
        with (ROOT / f"evidence/{name}.jsonl").open() as rows:
            actual.append(Counter(json.loads(line)["block"] for line in rows))
    assert published == {
        block: (actual[0][block], actual[1][block])
        for block in actual[0].keys() | actual[1].keys()
    }


def source_tables(text: str):
    """Read declared coordinate tables by header, never by their last column."""
    header = None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|"):
            header = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if {"Block", "Offset", "Length"}.issubset(cells):
            assert len(cells) == len(set(cells)), f"Duplicate columns at line {number}"
            header = cells
        elif header and not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            assert len(cells) == len(header), f"Malformed source row at line {number}"
            yield number, dict(zip(header, cells))


def validate_source_tables(text: str, ranges: set, instructions: list) -> int:
    checked = 0
    for line, row in source_tables(text):
        try:
            block = int(row["Block"])
            offset_text = row["Offset"].strip("`")
            assert re.fullmatch(r"0x[0-9a-fA-F]+", offset_text)
            assert re.fullmatch(r"(?:\d+|\d{1,3}(?:,\d{3})+)", row["Length"])
            offset = int(offset_text, 16)
            length = int(row["Length"].replace(",", ""))
            assert length > 0
            kind = row.get("Reference", "Range")
            if kind == "Range":
                assert (block, offset, length) in ranges, "Not an exact canonical range"
            elif kind == "Instruction span":
                address_text = row["Recorded address"].strip("`")
                assert re.fullmatch(r"0x[0-9a-fA-F]+", address_text)
                delta = int(address_text, 16) - offset
                selected = [
                    item for item in instructions
                    if item["block"] == block
                    and offset <= item["offset"] < offset + length
                    and item["address"] - item["offset"] == delta
                ]
                covered = {
                    byte for item in selected
                    for byte in range(item["offset"], item["offset"] + item["length"])
                }
                assert covered == set(range(offset, offset + length)), "Instruction span has gaps or a partial boundary"
            else:
                raise AssertionError(f"Unknown reference type: {kind}")
        except (ValueError, KeyError, AssertionError) as exc:
            raise AssertionError(f"Source table line {line}: {row}: {exc}") from exc
        checked += 1
    return checked


def canonical_references():
    ranges = {
        (row["block"], row["offset"], row["length"])
        for row in map(json.loads, (ROOT / "evidence/ranges.jsonl").read_text().splitlines())
    }
    instructions = list(map(json.loads, (ROOT / "evidence/instructions.jsonl").read_text().splitlines()))
    return ranges, instructions


def test_source_anchor_tables() -> None:
    ranges, instructions = canonical_references()
    checked = 0
    for path in ROOT.joinpath("docs/firmware").rglob("*.md"):
        try:
            checked += validate_source_tables(prose(path), ranges, instructions)
        except AssertionError as exc:
            raise AssertionError(f"{path.relative_to(ROOT)}: {exc}") from exc
    assert checked, "No source anchor tables found"


def test_range_table_extra_columns_and_formatted_lengths() -> None:
    text = "| Offset | Length | Role | Block | Support |\n|---|---:|---|---:|---|\n| `0x00b1df68` | 2,528 | Names | 0 | Range only |"
    ranges = {(0, 0x00b1df68, 2528)}
    assert validate_source_tables(text, ranges, []) == 1
    with pytest.raises(AssertionError, match="Not an exact canonical range"):
        validate_source_tables(text.replace("0x00b1df68", "0x00b1df69"), ranges, [])
    with pytest.raises(AssertionError, match="Malformed source row"):
        validate_source_tables(text + "\n| 0 | missing cells |", ranges, [])


@pytest.mark.parametrize("old,new", [
    ("0x0059b994", "0x0059b995"),
    ("| 21 |", "| 20 |"),
    ("0x4085b994", "0x4085b995"),
    ("Instruction span", "Unknown"),
])
def test_native_request_table_changes_are_checked(old: str, new: str) -> None:
    text = prose(ROOT / "docs/firmware/STILL_OBJECTS.md")
    start = text.index("| Role |", text.index('id="native-still-request"'))
    table = text[start:].split("\n\n", 1)[0]
    ranges, instructions = canonical_references()
    assert validate_source_tables(table, ranges, instructions) == 4
    assert old in table
    with pytest.raises(AssertionError):
        validate_source_tables(table.replace(old, new, 1), ranges, instructions)


def test_existing_document_fragments_remain_available() -> None:
    legacy = json.loads((ROOT / "tests/fixtures/docs/legacy-fragments.json").read_text())
    for name, anchors in legacy.items():
        assert set(anchors) <= fragments(prose(ROOT / name)), f"Lost legacy link in {name}"
