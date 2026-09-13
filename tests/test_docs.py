"""Check the public reference's navigation and mechanical evidence references."""

from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


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


def test_source_anchor_tables_name_exact_canonical_ranges() -> None:
    with (ROOT / "evidence/ranges.jsonl").open() as rows:
        ranges = {
            (row["block"], row["offset"], row["length"])
            for row in map(json.loads, rows)
        }
    checked = set()
    for path in ROOT.joinpath("docs/firmware").glob("*.md"):
        for block, offset, length in re.findall(
            r"\| (\d+) \| `(0x[0-9a-f]+)` \| (\d+) \|$", prose(path), re.M
        ):
            anchor = (int(block), int(offset, 16), int(length))
            assert anchor in ranges, f"{path.name}: noncanonical range {anchor}"
            checked.add(anchor)
    assert checked, "No source anchor tables found"
