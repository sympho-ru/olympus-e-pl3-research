from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .audit import audit_git_history, audit_tree, load_contract, load_private_terms
from .contributions import ContributionError, pending_contribution_files
from .evidence import EvidenceError, load_evidence
from .source import VerifiedSource


DECLARED_REPRESENTATIONS = [
    "contiguous-hex",
    "base64",
    "python-byte-escape",
    "python-bytes-fromhex",
    "integer-byte-array",
    "binary-or-archive",
]


@dataclass(frozen=True)
class CheckResult:
    mode: str
    checks: int
    problems: tuple[str, ...]
    history_scanned: bool

    @property
    def ok(self) -> bool:
        return not self.problems


def _project_files(root: Path) -> list[str]:
    required = [
        "README.md",
        "AUTHORS.md",
        "LICENSE",
        "LICENSE-DOCUMENTATION",
        "CONTRIBUTING.md",
        "docs/ANALYSIS.md",
        "docs/EVIDENCE.md",
        "docs/FIRMWARE_MAP.md",
        "docs/OBTAINING_FIRMWARE.md",
        "docs/RESEARCH.md",
        "pyproject.toml",
    ]
    return [f"missing required file {name}" for name in required if not (root / name).is_file()]


def _licensing(root: Path) -> list[str]:
    expectations = {
        "LICENSE": ("Apache License", "Version 2.0"),
        "LICENSE-DOCUMENTATION": ("CC BY 4.0", "evidence metadata", "AUTHORS.md"),
        "AUTHORS.md": ("# Authors",),
        "README.md": (
            "contains no Olympus firmware image",
            "not endorsed by OM Digital Solutions or Olympus",
        ),
        "pyproject.toml": ('license = {text = "Apache-2.0"}',),
    }
    problems: list[str] = []
    for name, required_text in expectations.items():
        path = root / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if any(value not in text for value in required_text):
            problems.append(f"licensing declaration is incomplete in {name}")
    return problems


def _term_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _private_terms(
    root: Path,
    mode: str,
    path: Path | None,
    no_private_terms: bool,
) -> tuple[tuple[str, ...], list[str]]:
    if no_private_terms and mode != "release":
        return (), ["--no-private-terms is valid only with --release"]
    if no_private_terms:
        return (), []
    selected = path
    if selected is None and mode == "release":
        selected = root / ".private" / "release-denylist.txt"
    if selected is None:
        return (), []
    selected = _term_path(root, selected)
    try:
        return load_private_terms(selected), []
    except ValueError as error:
        return (), [str(error)]


def run_checks(
    root: Path,
    mode: str,
    source: VerifiedSource | None = None,
    private_terms_path: Path | None = None,
    no_private_terms: bool = False,
) -> CheckResult:
    if mode not in {"structural", "source", "release"}:
        raise ValueError(f"unknown check mode {mode!r}")
    problems: list[str] = []
    checks = 0

    problems.extend(_project_files(root))
    checks += 1

    problems.extend(_licensing(root))
    checks += 1

    if mode in {"source", "release"} and source is None:
        problems.append(f"{mode} check requires a verified source")
    try:
        load_evidence(root, source=source if mode in {"source", "release"} else None)
    except EvidenceError as error:
        problems.append(str(error))
    checks += 1

    if mode == "release":
        try:
            pending = pending_contribution_files(root)
            if pending:
                problems.append(
                    f"release contains {len(pending)} pending incoming contribution file(s)"
                )
        except ContributionError as error:
            problems.append(str(error))
    checks += 1

    contract = load_contract()
    if (
        contract.get("schema") != "literal-audit/v1"
        or contract.get("representations") != DECLARED_REPRESENTATIONS
    ):
        problems.append("literal-audit/v1 contract is not the declared closed representation set")
    checks += 1

    private_terms, term_problems = _private_terms(
        root, mode, private_terms_path, no_private_terms
    )
    problems.extend(term_problems)
    checks += 1

    tree_source = source if mode in {"source", "release"} else None
    problems.extend(
        finding.render() for finding in audit_tree(root, tree_source, private_terms)
    )
    checks += 1

    history_scanned = False
    if mode == "release":
        if source is not None:
            problems.extend(
                finding.render()
                for finding in audit_git_history(root, source, private_terms)
            )
            history_scanned = True
        checks += 1

    return CheckResult(mode, checks, tuple(problems), history_scanned)
