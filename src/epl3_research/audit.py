from __future__ import annotations

import ast
import base64
import binascii
import json
import re
import subprocess
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Iterable, Iterator

from .source import VerifiedSource, sha256_bytes


IGNORED_PARTS = frozenset(
    {".git", ".private", ".pytest_cache", ".ruff_cache", "__pycache__", "build", "dist"}
)
BINARY_SUFFIXES = frozenset(
    {".bin", ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar", ".dmg", ".iso", ".img", ".fw"}
)
HEX_RE = re.compile(r"(?<![0-9A-Fa-f])(?P<value>[0-9A-Fa-f]{16,})(?![0-9A-Fa-f])")
BASE64_RE = re.compile(
    r"(?<![A-Za-z0-9+/=])(?P<value>(?:[A-Za-z0-9+/]{4}){2,}"
    r"(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)(?![A-Za-z0-9+/=])"
)
BYTE_ESCAPE_RE = re.compile(r"(?P<value>(?:\\x[0-9A-Fa-f]{2})+)")
FROMHEX_RE = re.compile(
    r"bytes\.fromhex\(\s*(?P<quote>['\"])(?P<value>[0-9A-Fa-f\s]+)(?P=quote)\s*\)"
)
URL_RE = re.compile(r"https?://[^\s\"'`<>]+", re.IGNORECASE)
WINDOWS_DRIVE_RE = re.compile(r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/])")
WINDOWS_UNC_RE = re.compile(r"(?<!\\)\\\\[^\\\s]+\\[^\\\s]+")
PRIVATE_ROOT_NAMES = ("Volumes", "Users", "home", "private", "tmp")
PRIVATE_NESTED_ROOTS = (("var", "folders"),)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
)


def is_carrier_key(key: str) -> bool:
    return key in {"bytes_hex", "context_hex", "preimage_hex"} or key.endswith(
        ("_bytes_hex", "_preimage_hex", "_payload_hex", "_window_hex")
    )


@dataclass(frozen=True)
class DecodedCandidate:
    representation: str
    offset: int
    value: bytes


@dataclass(frozen=True)
class AuditFinding:
    path: str
    representation: str
    offset: int
    length: int
    sha256: str | None
    detail: str

    def render(self) -> str:
        digest = f", sha256={self.sha256}" if self.sha256 else ""
        return (
            f"{self.path}: {self.representation} at {self.offset} "
            f"({self.length} bytes{digest}): {self.detail}"
        )


def load_contract() -> dict[str, object]:
    resource = files("epl3_research").joinpath("data/literal-audit-v1.json")
    return json.loads(resource.read_text(encoding="utf-8"))


def load_private_terms(path: Path) -> tuple[str, ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"cannot read private-term file {path}: {error}") from error
    terms: list[str] = []
    seen: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        folded = stripped.casefold()
        if folded not in seen:
            seen.add(folded)
            terms.append(folded)
    if not terms:
        raise ValueError(f"private-term file has no effective terms: {path}")
    return tuple(terms)


def _decode_base64(value: str) -> bytes | None:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError):
        return None


def text_candidates(text: str, suffix: str = "") -> Iterator[DecodedCandidate]:
    minimum = int(load_contract()["untyped_minimum_bytes"])
    for match in HEX_RE.finditer(text):
        try:
            value = bytes.fromhex(match.group("value"))
        except ValueError:
            continue
        if len(value) >= minimum:
            yield DecodedCandidate("contiguous-hex", match.start("value"), value)
    for match in BASE64_RE.finditer(text):
        decoded = _decode_base64(match.group("value"))
        if decoded is not None and len(decoded) >= minimum:
            yield DecodedCandidate("base64", match.start("value"), decoded)
    for match in BYTE_ESCAPE_RE.finditer(text):
        value = bytes.fromhex(match.group("value").replace("\\x", ""))
        if value:
            yield DecodedCandidate("python-byte-escape", match.start("value"), value)
    for match in FROMHEX_RE.finditer(text):
        try:
            value = bytes.fromhex(match.group("value"))
        except ValueError:
            continue
        if value:
            yield DecodedCandidate("python-bytes-fromhex", match.start("value"), value)
    if suffix == ".py":
        yield from _python_integer_arrays(text, minimum)
    elif suffix == ".json":
        yield from _json_integer_arrays(text, minimum)


def _python_integer_arrays(text: str, minimum: int) -> Iterator[DecodedCandidate]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if not isinstance(node, (ast.List, ast.Tuple)) or len(node.elts) < minimum:
            continue
        values: list[int] = []
        for child in node.elts:
            if not isinstance(child, ast.Constant) or not isinstance(child.value, int):
                break
            if child.value < 0 or child.value > 255:
                break
            values.append(child.value)
        else:
            yield DecodedCandidate(
                "integer-byte-array",
                max(0, int(getattr(node, "col_offset", 0))),
                bytes(values),
            )


def _json_integer_arrays(text: str, minimum: int) -> Iterator[DecodedCandidate]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError:
        return

    def walk(value: object) -> Iterator[DecodedCandidate]:
        if isinstance(value, list):
            if len(value) >= minimum and all(
                isinstance(item, int) and not isinstance(item, bool) and 0 <= item <= 255
                for item in value
            ):
                yield DecodedCandidate("integer-byte-array", 0, bytes(value))
            for item in value:
                yield from walk(item)
        elif isinstance(value, dict):
            for item in value.values():
                yield from walk(item)

    yield from walk(document)


def _is_source_bytes(
    value: bytes,
    blocks: Iterable[bytes],
    cache: dict[bytes, bool],
) -> bool:
    if not value:
        return False
    if value not in cache:
        cache[value] = any(value in block for block in blocks)
    return cache[value]


def _walk_json(value: object) -> Iterator[tuple[str | None, object]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield None, child
            yield from _walk_json(child)


def _json_policy_findings(path: str, text: str) -> list[AuditFinding]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        return [AuditFinding(path, "invalid-json", error.pos, 0, None, error.msg)]
    findings: list[AuditFinding] = []
    for key, value in _walk_json(document):
        if (
            key is not None
            and is_carrier_key(key)
            and isinstance(value, str)
            and value
            and re.fullmatch(r"[0-9A-Fa-f]+", value)
            and len(value) % 2 == 0
        ):
            raw = bytes.fromhex(value)
            findings.append(
                AuditFinding(
                    path,
                    "raw-carrier-field",
                    0,
                    len(raw),
                    sha256_bytes(raw),
                    f"field {key!r} must be absent from the public tree",
                )
            )
    return findings


def _url_spans(text: str) -> list[tuple[int, int]]:
    return [match.span() for match in URL_RE.finditer(text)]


def _inside(position: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in spans)


def _text_hygiene_findings(
    path: str,
    text: str,
    private_terms: tuple[str, ...],
) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                AuditFinding(path, "secret-or-private-key", match.start(), 0, None, "credential-shaped text")
            )
    url_spans = _url_spans(text)
    needles = ["/" + root + "/" for root in PRIVATE_ROOT_NAMES]
    needles.extend("/" + "/".join(parts) + "/" for parts in PRIVATE_NESTED_ROOTS)
    for needle in needles:
        start = 0
        while True:
            position = text.find(needle, start)
            if position < 0:
                break
            if not _inside(position, url_spans):
                findings.append(
                    AuditFinding(
                        path,
                        "private-absolute-path",
                        position,
                        0,
                        None,
                        "high-confidence workstation path",
                    )
                )
            start = position + len(needle)
    for pattern in (WINDOWS_DRIVE_RE, WINDOWS_UNC_RE):
        for match in pattern.finditer(text):
            if not _inside(match.start(), url_spans):
                findings.append(
                    AuditFinding(
                        path,
                        "private-absolute-path",
                        match.start(),
                        0,
                        None,
                        "high-confidence workstation path",
                    )
                )
    folded = text.casefold()
    for term in private_terms:
        start = 0
        while True:
            position = folded.find(term, start)
            if position < 0:
                break
            findings.append(
                AuditFinding(
                    path,
                    "configured-private-term",
                    position,
                    0,
                    None,
                    "configured private identifier",
                )
            )
            start = position + len(term)
    return findings


def _fallback_public_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if path.is_symlink() or path.is_file():
            result.append(path)
    return sorted(result)


def public_files(root: Path) -> list[Path]:
    git = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        check=False,
        capture_output=True,
    )
    if git.returncode != 0:
        return _fallback_public_files(root)
    result: list[Path] = []
    for item in git.stdout.split(b"\0"):
        if not item:
            continue
        path = root / item.decode("utf-8", errors="strict")
        if path.is_symlink() or path.is_file():
            result.append(path)
    return sorted(result)


def _audit_text(
    virtual_path: str,
    text: str,
    suffix: str,
    source: VerifiedSource | None,
    private_terms: tuple[str, ...],
    source_matches: dict[bytes, bool],
) -> list[AuditFinding]:
    findings = _text_hygiene_findings(virtual_path, text, private_terms)
    if suffix == ".json":
        findings.extend(_json_policy_findings(virtual_path, text))
    if source is not None:
        seen: set[tuple[str, int, str]] = set()
        for candidate in text_candidates(text, suffix):
            digest = sha256_bytes(candidate.value)
            key = (candidate.representation, candidate.offset, digest)
            if key in seen or not _is_source_bytes(
                candidate.value, source.blocks, source_matches
            ):
                continue
            seen.add(key)
            findings.append(
                AuditFinding(
                    virtual_path,
                    candidate.representation,
                    candidate.offset,
                    len(candidate.value),
                    digest,
                    "declared literal representation resolves to official decoded firmware",
                )
            )
    return findings


def audit_tree(
    root: Path,
    source: VerifiedSource | None = None,
    private_terms: tuple[str, ...] = (),
) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    source_matches: dict[bytes, bool] = {}
    for path in public_files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            findings.append(AuditFinding(relative, "symlink", 0, 0, None, "public symlinks are not allowed"))
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            findings.append(
                AuditFinding(relative, "binary-or-archive", 0, path.stat().st_size, None, "forbidden public suffix")
            )
            continue
        value = path.read_bytes()
        try:
            text = value.decode("utf-8")
        except UnicodeDecodeError:
            findings.append(
                AuditFinding(
                    relative,
                    "binary-or-archive",
                    0,
                    len(value),
                    sha256_bytes(value),
                    "non-UTF-8 public file",
                )
            )
            continue
        findings.extend(
            _audit_text(
                relative,
                text,
                path.suffix.lower(),
                source,
                private_terms,
                source_matches,
            )
        )
    return findings


def audit_paths(
    root: Path,
    paths: Iterable[Path],
    source: VerifiedSource | None = None,
    private_terms: tuple[str, ...] = (),
) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    source_matches: dict[bytes, bool] = {}
    for path in sorted(paths):
        relative = path.relative_to(root).as_posix()
        value = path.read_bytes()
        try:
            text = value.decode("utf-8")
        except UnicodeDecodeError:
            findings.append(
                AuditFinding(
                    relative,
                    "binary-or-archive",
                    0,
                    len(value),
                    sha256_bytes(value),
                    "non-UTF-8 contribution file",
                )
            )
            continue
        findings.extend(
            _audit_text(
                relative,
                text,
                path.suffix.lower(),
                source,
                private_terms,
                source_matches,
            )
        )
    return findings


def audit_git_history(
    root: Path,
    source: VerifiedSource,
    private_terms: tuple[str, ...] = (),
) -> list[AuditFinding]:
    git = subprocess.run(
        ["git", "-C", str(root), "rev-list", "--objects", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if git.returncode != 0:
        return []
    findings: list[AuditFinding] = []
    seen: set[str] = set()
    source_matches: dict[bytes, bool] = {}
    for line in git.stdout.splitlines():
        object_id, _, object_path = line.partition(" ")
        if not object_path or object_id in seen:
            continue
        seen.add(object_id)
        object_type = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-t", object_id],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if object_type != "blob":
            continue
        value = subprocess.run(
            ["git", "-C", str(root), "cat-file", "blob", object_id],
            check=True,
            capture_output=True,
        ).stdout
        virtual = f"history:{object_id}:{object_path}"
        suffix = Path(object_path).suffix.lower()
        if suffix in BINARY_SUFFIXES:
            findings.append(
                AuditFinding(virtual, "binary-or-archive", 0, len(value), sha256_bytes(value), "history blob")
            )
            continue
        try:
            text = value.decode("utf-8")
        except UnicodeDecodeError:
            findings.append(
                AuditFinding(virtual, "binary-or-archive", 0, len(value), sha256_bytes(value), "history blob")
            )
            continue
        findings.extend(
            _audit_text(
                virtual,
                text,
                suffix,
                source,
                private_terms,
                source_matches,
            )
        )
    return findings
