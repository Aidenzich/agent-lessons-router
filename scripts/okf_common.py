#!/usr/bin/env python3
"""Shared helpers for ALR/OKF read-only tooling."""

from __future__ import annotations

import fnmatch
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse, urlsplit, urlunsplit

import yaml

PRUNE_DIRS = {".git", "node_modules", "dist", ".agents-workspace", ".repos"}
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]\n|#]+)(?:#[^\]\n|]+)?(?:\|[^\]\n]+)?\]\]")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.S)
BLOCK_SCALAR_MARKERS = {"|", ">", "|-", ">-", "|+", ">+"}
SECRET_QUERY_RE = re.compile(
    r"(?i)([?&;](?:access[_-]?token|api[_-]?key|auth[_-]?token|client[_-]?secret|"
    r"credential|password|passwd|secret|token)=)[^&#;\s/]+"
)
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b((?:access[_-]?token|api[_-]?key|auth[_-]?token|client[_-]?secret|"
    r"credential|password|passwd|secret|token)=)[^&#;\s/]+"
)
SECRET_PATH_RE = re.compile(
    r"(?i)(/(?:access[_-]?token|api[_-]?key|auth[_-]?token|client[_-]?secret|"
    r"credential|password|passwd|secret|token)/)[^/?#;\s]+"
)


class OkfUsageError(Exception):
    pass


def default_profile_path() -> Path:
    return Path(__file__).resolve().parents[1] / "docs" / "alr-okf-profile.contract.yaml"


def load_profile(path: str | Path) -> dict[str, Any]:
    profile_path = Path(path).expanduser()
    if not profile_path.exists():
        raise OkfUsageError(f"profile not found: {profile_path}")
    try:
        with profile_path.open("r", encoding="utf-8") as handle:
            profile = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        raise OkfUsageError(f"invalid profile YAML: {profile_path}: {exc}") from exc
    if not isinstance(profile, dict):
        raise OkfUsageError(f"invalid profile contract: expected YAML mapping: {profile_path}")

    required = [
        "profile",
        "bundle",
        "reserved_index_files",
        "concept_roots",
        "required_frontmatter",
        "link_policy",
        "tooling_contract",
    ]
    missing = [key for key in required if key not in profile]
    if missing:
        raise OkfUsageError(f"invalid profile contract: missing {', '.join(missing)}")
    return profile


def resolve_bundle(path: str | Path) -> Path:
    bundle = Path(path).expanduser()
    try:
        resolved = bundle.resolve(strict=True)
    except FileNotFoundError as exc:
        raise OkfUsageError(f"bundle not found: {bundle}") from exc
    if not resolved.is_dir():
        raise OkfUsageError(f"bundle is not a directory: {resolved}")
    if resolved == resolved.parent:
        raise OkfUsageError("refusing to scan filesystem root as a bundle")
    return resolved


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return False


def archive_dir_names(profile: dict[str, Any]) -> set[str]:
    names = set()
    for pattern in profile.get("archive_roots", []):
        path = str(pattern).strip("/")
        for part in Path(path).parts:
            if part and "*" not in part:
                names.add(part)
    return names or {"_archive"}


def is_archive_path(rel: str, profile: dict[str, Any]) -> bool:
    archive_names = archive_dir_names(profile)
    return any(part in archive_names for part in Path(rel).parts)


def is_reserved_index(rel: str, profile: dict[str, Any]) -> bool:
    name = Path(rel).name
    for pattern in profile.get("reserved_index_files", []):
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def is_reserved_log(rel: str, profile: dict[str, Any]) -> bool:
    name = Path(rel).name
    for pattern in profile.get("reserved_log_files", []):
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def iter_markdown_files(
    root: Path, include_archives: bool = False, profile: dict[str, Any] | None = None
) -> list[Path]:
    files: list[Path] = []
    archive_names = archive_dir_names(profile or {}) if not include_archives else set()
    for current, dirs, filenames in os.walk(root):
        current_path = Path(current)
        pruned = set(PRUNE_DIRS)
        if not include_archives:
            pruned.update(archive_names)
        dirs[:] = [dirname for dirname in dirs if dirname not in pruned]
        for filename in filenames:
            path = current_path / filename
            if path.suffix.lower() in MARKDOWN_EXTENSIONS and is_under(path, root):
                files.append(path)
    return sorted(files)


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, None
    raw = match.group(1)
    data: dict[str, Any] = {}
    lines = raw.splitlines()
    stack: list[tuple[int, dict[str, Any] | list[Any]]] = [(-1, data)]
    index = 0
    while index < len(lines):
        line = lines[index]
        lineno = index + 1
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        target = stack[-1][1] if stack else data

        if stripped.startswith("- "):
            if not isinstance(target, list):
                return None, f"line {lineno}: unsupported YAML frontmatter"
            target.append(parse_scalar(stripped[2:].strip()))
            index += 1
            continue

        if ":" not in stripped:
            return None, f"line {lineno}: unsupported YAML frontmatter"
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            return None, f"line {lineno}: empty frontmatter key"
        if not isinstance(target, dict):
            return None, f"line {lineno}: unsupported YAML frontmatter"
        if value == "":
            nested: dict[str, Any] | list[Any] = _empty_yaml_container_for_next_line(lines, lineno)
            target[key] = nested
            stack.append((indent, nested))
        elif value in BLOCK_SCALAR_MARKERS:
            block_value, index = _parse_block_scalar(lines, index, indent)
            target[key] = block_value
            continue
        else:
            target[key] = parse_scalar(value)
        index += 1
    return data, None


def _parse_block_scalar(lines: list[str], start_index: int, parent_indent: int) -> tuple[str, int]:
    block_lines: list[str] = []
    index = start_index + 1
    content_indent: int | None = None
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            block_lines.append("")
            index += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= parent_indent:
            break
        if content_indent is None or indent < content_indent:
            content_indent = indent
        block_lines.append(line[content_indent:])
        index += 1
    return "\n".join(block_lines), index


def _empty_yaml_container_for_next_line(lines: list[str], current_lineno: int) -> dict[str, Any] | list[Any]:
    current_line = lines[current_lineno - 1]
    current_indent = len(current_line) - len(current_line.lstrip(" "))
    for next_line in lines[current_lineno:]:
        if not next_line.strip() or next_line.lstrip().startswith("#"):
            continue
        next_indent = len(next_line) - len(next_line.lstrip(" "))
        if next_indent <= current_indent:
            return {}
        if next_line.strip().startswith("- "):
            return []
        return {}
    return {}


def parse_scalar(value: str) -> Any:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [item.strip().strip("'\"") for item in body.split(",")]
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    return value


def classify_file(rel: str, profile: dict[str, Any], include_artifacts: bool = False) -> str:
    if is_reserved_index(rel, profile):
        return "index"
    if is_reserved_log(rel, profile):
        return "log"
    if is_archive_path(rel, profile):
        return "archive"
    for root_spec in profile.get("concept_roots", []):
        root = root_spec.get("path", "").strip("/")
        if not root:
            continue
        if rel == root or rel.startswith(root + "/"):
            if root == "artifacts" and not include_artifacts:
                return "artifact-excluded"
            return str(root_spec.get("class", root))
    return "other"


def diagnostic(code: str, severity: str, path: str, message: str, **extra: Any) -> dict[str, Any]:
    item = {"code": code, "severity": severity, "path": path, "message": message}
    item.update(extra)
    return item


def redact_secret_like_value(value: str) -> str:
    redacted = redact_url_userinfo(value)
    redacted = SECRET_QUERY_RE.sub(r"\1[REDACTED]", redacted)
    redacted = SECRET_ASSIGNMENT_RE.sub(r"\1[REDACTED]", redacted)
    return SECRET_PATH_RE.sub(r"\1[REDACTED]", redacted)


def redact_url_userinfo(value: str) -> str:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return value
    if not parsed.scheme or not parsed.netloc or "@" not in parsed.netloc:
        return value
    hostport = parsed.netloc.rsplit("@", 1)[1]
    return urlunsplit(
        (parsed.scheme, f"[REDACTED]@{hostport}", parsed.path, parsed.query, parsed.fragment)
    )


def extract_links(text: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for match in MARKDOWN_LINK_RE.finditer(text):
        links.append({"kind": "markdown", "target": match.group(1).strip()})
    for match in WIKI_LINK_RE.finditer(text):
        links.append({"kind": "wiki", "target": match.group(1).strip()})
    return links


def is_external_link(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme) or target.startswith("mailto:")


def strip_fragment(target: str) -> str:
    return target.split("#", 1)[0]


def build_markdown_index(
    root: Path, include_archives: bool = False, profile: dict[str, Any] | None = None
) -> dict[str, set[str]]:
    files = iter_markdown_files(root, include_archives=include_archives, profile=profile)
    rels = {relpath(path, root) for path in files}
    index: dict[str, set[str]] = {"__rels__": rels}
    for rel in rels:
        path = Path(rel)
        index.setdefault(path.name, set()).add(rel)
        index.setdefault(path.stem, set()).add(rel)
    return index


def resolve_internal_link(root: Path, source_rel: str, target: str, md_index: dict[str, set[str]]) -> str | None:
    raw = unquote(strip_fragment(target).strip())
    if raw == "":
        return source_rel
    root_base = root.resolve(strict=False)
    if raw.startswith("/"):
        candidate_paths = [root_base / raw.lstrip("/")]
    elif target.startswith("[[") and target.endswith("]]"):
        candidate_paths = [root_base / raw]
    else:
        candidate_paths = [root_base / Path(source_rel).parent / raw]

    expanded: list[str] = []
    for candidate in candidate_paths:
        try:
            clean = candidate.resolve(strict=False).relative_to(root_base).as_posix()
        except ValueError:
            continue
        expanded.append(clean)
        if Path(clean).suffix == "":
            expanded.append(clean + ".md")
            expanded.append((Path(clean) / "index.md").as_posix())

    rels = md_index.get("__rels__", set())
    for candidate in expanded:
        normalized = Path(candidate).as_posix()
        if normalized in rels:
            return normalized
    if raw in md_index and len(md_index[raw]) == 1:
        return next(iter(md_index[raw]))
    name = Path(raw).name
    if name in md_index and len(md_index[name]) == 1:
        return next(iter(md_index[name]))
    if Path(raw).suffix == "":
        md_name = name + ".md"
        if md_name in md_index and len(md_index[md_name]) == 1:
            return next(iter(md_index[md_name]))
    return None


def print_error(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
