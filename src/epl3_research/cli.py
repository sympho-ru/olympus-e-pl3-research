from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checks import run_checks
from .contributions import (
    ContributionError,
    ContributionReport,
    accept_contribution,
    check_contribution,
)
from .evidence import EvidenceError, load_instruction_rows
from .decoding import verify_instructions
from .source import SourceVerificationError, sha256_bytes, source_summary, verify_source


def project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        pyproject = candidate / "pyproject.toml"
        if pyproject.exists() and "olympus-e-pl3-research" in pyproject.read_text(encoding="utf-8"):
            return candidate
    return current


def _base_zero_int(value: str) -> int:
    try:
        return int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"expected an integer, got {value!r}") from error


def _nonnegative_int(value: str) -> int:
    result = _base_zero_int(value)
    if result < 0:
        raise argparse.ArgumentTypeError("value must be nonnegative")
    return result


def _positive_int(value: str) -> int:
    result = _base_zero_int(value)
    if result < 1:
        raise argparse.ArgumentTypeError("value must be positive")
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epl3-research",
        description="Offline Olympus E-PL3 research verification tooling.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    verify = commands.add_parser("verify-source", help="verify the official source and decoded blocks")
    verify.add_argument("--image", required=True)

    reference = commands.add_parser("source-range", help="print a verified byte-free source range")
    reference.add_argument("--image", required=True)
    reference.add_argument("--block", required=True, type=_nonnegative_int)
    reference.add_argument("--offset", required=True, type=_nonnegative_int)
    reference.add_argument("--length", required=True, type=_positive_int)

    extract = commands.add_parser(
        "extract-blocks",
        help="write verified decoded blocks to a local-private directory",
    )
    extract.add_argument("--image", required=True)
    extract.add_argument("--output", required=True, type=Path)

    check = commands.add_parser("check", help="run structural, source-bound, or release checks")
    check.add_argument("--source", help="verified official image for source-bound checks")
    check.add_argument("--release", action="store_true", help="also reject pending contributions and audit current HEAD history")
    term_group = check.add_mutually_exclusive_group()
    term_group.add_argument("--private-terms", type=Path, help="local newline-delimited private-term file")
    term_group.add_argument("--no-private-terms", action="store_true", help="explicitly opt out of release private-term scanning")
    check.add_argument("--root", type=Path, help="repository root; defaults to the current checkout")

    contribution = commands.add_parser(
        "check-contribution", help="verify incoming PR files without changing canonical evidence"
    )
    contribution.add_argument("--base", required=True, help="target branch ref or commit")
    contribution.add_argument("--source", required=True, help="verified official image")
    contribution.add_argument(
        "--root", type=Path, help="repository root; defaults to the current checkout"
    )

    accept = commands.add_parser(
        "accept-contribution", help="merge verified incoming files into canonical evidence"
    )
    accept.add_argument("--source", required=True, help="verified official image")
    accept.add_argument(
        "--root", type=Path, help="repository root; defaults to the current checkout"
    )
    accept.add_argument("files", nargs="+", type=Path, help="incoming files to consume")
    for command in (contribution, accept):
        command.add_argument("--objdump", help="GNU MN103 objdump 2.45; or MN103_OBJDUMP")
        command.add_argument("--overlap-review", type=Path, help="exact overlapping row pairs and review reasons")
    screen = commands.add_parser("screen-instructions", help="report decode defects and overlaps without changing evidence")
    screen.add_argument("--source", required=True)
    screen.add_argument("--root", type=Path)
    screen.add_argument("--objdump")
    screen.add_argument("--output", required=True, type=Path)
    screen.add_argument("files", nargs="*", type=Path, help="selected instruction JSONL; omitted screens canonical corpus")
    return parser


def _print_contribution_report(prefix: str, report: ContributionReport) -> None:
    print(f"{prefix}: {report.files} contribution file(s)")
    print(
        f"ranges: {report.new_ranges} new, {report.duplicate_ranges} duplicate"
    )
    print(
        "instructions: "
        f"{report.new_instructions} new, {report.duplicate_instructions} duplicate"
    )
    print(f"instruction decodes requiring review: {report.instruction_decodes_to_review}")
    if report.new_instructions or report.duplicate_instructions:
        print("contextual decode gate passed; start anchors and semantic claims still require review")


def _extract_blocks(
    root: Path, output: Path, blocks: tuple[bytes, ...]
) -> list[dict[str, object]]:
    root = root.resolve()
    output = output.resolve()
    private = (root / ".private").resolve()
    if output.is_relative_to(root) and not (
        output == private or output.is_relative_to(private)
    ):
        raise ValueError(
            "decoded blocks inside the repository must be written under .private/"
        )

    targets = [output / f"block-{index}.bin" for index in range(len(blocks))]
    existing = [target for target in targets if target.exists()]
    if existing:
        raise ValueError(f"refusing to overwrite decoded block: {existing[0]}")

    output.mkdir(parents=True, exist_ok=True)
    result: list[dict[str, object]] = []
    for index, (target, block) in enumerate(zip(targets, blocks, strict=True)):
        with target.open("xb") as stream:
            stream.write(block)
        result.append(
            {
                "block": index,
                "file": target.name,
                "size": len(block),
                "sha256": sha256_bytes(block),
            }
        )
    return result


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "verify-source":
            source = verify_source(Path(args.image))
            print(json.dumps(source_summary(source), indent=2, sort_keys=True))
            return 0
        if args.command == "source-range":
            source = verify_source(Path(args.image))
            source.validate_range(args.block, args.offset, args.length)
            print(
                json.dumps(
                    {
                        "block": args.block,
                        "offset": args.offset,
                        "length": args.length,
                        "sha256": source.slice_sha256(
                            args.block, args.offset, args.length
                        ),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        if args.command == "extract-blocks":
            source = verify_source(Path(args.image))
            blocks = _extract_blocks(project_root(), args.output, source.blocks)
            print(
                json.dumps(
                    {"blocks": blocks, "verified": True}, indent=2, sort_keys=True
                )
            )
            return 0
        if args.command == "check-contribution":
            root = (args.root or project_root()).resolve()
            source = verify_source(Path(args.source))
            report = check_contribution(root, args.base, source, objdump=args.objdump, overlap_review=args.overlap_review)
            _print_contribution_report("PASS", report)
            return 0
        if args.command == "accept-contribution":
            root = (args.root or project_root()).resolve()
            source = verify_source(Path(args.source))
            report = accept_contribution(root, source, args.files, objdump=args.objdump, overlap_review=args.overlap_review)
            _print_contribution_report("ACCEPTED", report)
            return 0
        if args.command == "screen-instructions":
            root = (args.root or project_root()).resolve()
            source = verify_source(Path(args.source))
            canonical = load_instruction_rows(root / "evidence/instructions.jsonl", source.registry)
            rows = tuple(row for path in args.files for row in load_instruction_rows(
                path if path.is_absolute() else root / path, source.registry, source
            )) if args.files else canonical
            report = verify_instructions(source, rows, canonical, executable=args.objdump)
            report["canonical_instructions_sha256"] = sha256_bytes((root / "evidence/instructions.jsonl").read_bytes())
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
            failures = sum(row["status"] == "fail" for row in report["results"])
            print(json.dumps({"checked": len(report["results"]), "failed": failures,
                              "overlaps": len(report["overlaps"]), "report": str(args.output)}))
            return 1 if failures or report["overlaps"] else 0
        if args.command == "check":
            root = (args.root or project_root()).resolve()
            if args.release and not args.source:
                raise ValueError("check --release requires --source")
            if args.private_terms and not args.source:
                raise ValueError("--private-terms requires --source")
            if args.no_private_terms and not args.release:
                raise ValueError("--no-private-terms is valid only with --release")
            source = verify_source(Path(args.source)) if args.source else None
            mode = "release" if args.release else "source" if source is not None else "structural"
            result = run_checks(
                root,
                mode,
                source,
                private_terms_path=args.private_terms,
                no_private_terms=args.no_private_terms,
            )
            if result.ok:
                print(f"PASS: {result.checks} {mode} checks")
                return 0
            print(f"FAIL: {len(result.problems)} problem(s)", file=sys.stderr)
            for problem in result.problems:
                print(f"- {problem}", file=sys.stderr)
            return 1
    except (
        OSError,
        SourceVerificationError,
        EvidenceError,
        ContributionError,
        ValueError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    raise AssertionError("unreachable")
