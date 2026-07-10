#!/usr/bin/env python3
"""Stateless, bounded candidate reduction for native ALR recall."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


LESSON_PATH_RE = re.compile(r"(?:^|[\s`|\[(])(?P<path>lessons/[A-Za-z0-9_./-]+\.md)")
TOKEN_RE = re.compile(r"[a-z0-9]+|[\u3400-\u9fff]+", re.IGNORECASE)
CJK_RE = re.compile(r"[\u3400-\u9fff]")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
GENERIC_TERMS = {
    "app",
    "build",
    "code",
    "data",
    "error",
    "file",
    "issue",
    "process",
    "runtime",
    "service",
    "system",
    "task",
    "test",
}


class RecallUsageError(Exception):
    pass


@dataclass
class Anchor:
    raw: str
    alternatives: list[str]


@dataclass
class Candidate:
    path: str
    path_text: str
    index_text: str = ""
    metadata_text: str = ""
    description: str = ""
    score: int = 0
    matched_anchors: list[str] = field(default_factory=list)
    match_fields: dict[str, list[str]] = field(default_factory=dict)


def normalize(text: str) -> str:
    text = text.casefold().replace("_", " ").replace("-", " ").replace("/", " ")
    return " ".join(TOKEN_RE.findall(text))


def tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(normalize(text)))


def parse_anchor(raw: str) -> Anchor:
    alternatives = [normalize(item) for item in raw.split("|") if normalize(item)]
    if not alternatives:
        raise RecallUsageError("anchor must contain at least one non-empty alternative")
    discriminative = False
    for alternative in alternatives:
        meaningful = [token for token in tokens(alternative) if len(token) > 2 and token not in GENERIC_TERMS]
        if meaningful or CJK_RE.search(alternative):
            discriminative = True
            break
    if not discriminative:
        raise RecallUsageError(f"anchor is too generic: {raw!r}")
    return Anchor(raw=raw, alternatives=alternatives)


def detect_language(text: str) -> str:
    cjk = len(CJK_RE.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk and latin:
        return "mixed"
    if cjk:
        return "cjk"
    if latin:
        return "latin"
    return "unknown"


def strip_markdown(text: str) -> str:
    text = re.sub(r"[`*_#]", "", text)
    text = re.sub(r"\[([^]]+)]\([^)]*\)", r"\1", text)
    return " ".join(text.split())


def frontmatter_summary(path: Path) -> tuple[str, str]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            text = handle.read(8192)
    except (OSError, UnicodeDecodeError):
        return "", ""

    fields: list[str] = []
    description = ""
    match = FRONTMATTER_RE.match(text)
    if match:
        block = match.group(1)
        for key in ("title", "description", "tags", "domain", "type"):
            value_match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+)$", block)
            if value_match:
                value = value_match.group(1).strip().strip("'\"")
                fields.append(value)
                if key == "description":
                    description = value
    if not description:
        body = text[match.end() :] if match else text
        lines = [strip_markdown(line) for line in body.splitlines() if strip_markdown(line)]
        description = " ".join(lines[:2])[:360]
        fields.extend(lines[:2])
    return " ".join(fields), description[:360]


def load_candidates(bundle: Path, domain: str | None) -> dict[str, Candidate]:
    lessons_root = bundle / "lessons"
    if not lessons_root.is_dir():
        raise RecallUsageError(f"missing lessons directory: {lessons_root}")

    candidates: dict[str, Candidate] = {}
    domain_prefix = f"lessons/{domain.strip('/')}/" if domain else "lessons/"

    for path in sorted(lessons_root.rglob("*.md")):
        relative = path.relative_to(bundle).as_posix()
        if not relative.startswith(domain_prefix):
            continue
        metadata_text, description = frontmatter_summary(path)
        candidates[relative] = Candidate(
            path=relative,
            path_text=normalize(relative.removeprefix("lessons/").removesuffix(".md")),
            metadata_text=normalize(metadata_text),
            description=description,
        )

    for index_path in sorted(bundle.glob("index*.md")):
        try:
            lines = index_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line in lines:
            for match in LESSON_PATH_RE.finditer(line):
                relative = match.group("path")
                candidate = candidates.get(relative)
                if candidate is None:
                    continue
                candidate.index_text = f"{candidate.index_text} {normalize(strip_markdown(line))}".strip()
                if not candidate.description:
                    candidate.description = strip_markdown(line)[:360]
    return candidates


def alternative_matches(alternative: str, text: str, text_tokens: set[str]) -> bool:
    if alternative in text:
        return True
    alternative_tokens = tokens(alternative)
    return bool(alternative_tokens) and alternative_tokens.issubset(text_tokens)


def matching_alternative(anchor: Anchor, text: str) -> str | None:
    text_tokens = tokens(text)
    for alternative in anchor.alternatives:
        if alternative_matches(alternative, text, text_tokens):
            return alternative
    return None


def query_identifiers(query: str) -> list[str]:
    identifiers = re.findall(r"`([^`]+)`|\b([A-Za-z][A-Za-z0-9]*(?:[_-][A-Za-z0-9]+)+)\b", query)
    values = [left or right for left, right in identifiers]
    return list(dict.fromkeys(normalize(value) for value in values if normalize(value)))


def score_candidate(candidate: Candidate, anchors: list[Anchor], identifiers: list[str]) -> Candidate:
    fields = {
        "path": candidate.path_text,
        "index": candidate.index_text,
        "metadata": candidate.metadata_text,
    }
    field_weights = {"path": 12, "index": 7, "metadata": 5}
    matched: list[str] = []
    match_fields: dict[str, list[str]] = {}
    score = 0

    for anchor in anchors:
        best_field = None
        best_alternative = None
        for field_name, field_text in fields.items():
            alternative = matching_alternative(anchor, field_text)
            if alternative and (best_field is None or field_weights[field_name] > field_weights[best_field]):
                best_field = field_name
                best_alternative = alternative
        if best_field is not None and best_alternative is not None:
            matched.append(anchor.raw)
            match_fields.setdefault(best_field, []).append(best_alternative)
            score += field_weights[best_field] + 5

    combined = " ".join(fields.values())
    for identifier in identifiers:
        if identifier in combined:
            score += 20

    coverage = len(matched)
    if coverage == len(anchors):
        score += 20
    elif coverage >= 2:
        score += 6
    candidate.score = score
    candidate.matched_anchors = matched
    candidate.match_fields = match_fields
    return candidate


def reduce_candidates(
    bundle: Path,
    query: str,
    anchor_values: list[str],
    limit: int,
    domain: str | None,
) -> dict[str, object]:
    if not 2 <= len(anchor_values) <= 6:
        raise RecallUsageError("provide between 2 and 6 --anchor concept groups")
    if not 1 <= limit <= 10:
        raise RecallUsageError("--limit must be between 1 and 10")
    anchors = [parse_anchor(value) for value in anchor_values]
    identifiers = query_identifiers(query)
    candidates = load_candidates(bundle, domain)
    scored = [score_candidate(candidate, anchors, identifiers) for candidate in candidates.values()]
    scored = [candidate for candidate in scored if candidate.matched_anchors]
    scored.sort(key=lambda item: (-item.score, -len(item.matched_anchors), item.path))

    results = []
    for candidate in scored[:limit]:
        results.append(
            {
                "path": candidate.path,
                "score": candidate.score,
                "coverage": f"{len(candidate.matched_anchors)}/{len(anchors)}",
                "matched_anchors": candidate.matched_anchors,
                "match_fields": candidate.match_fields,
                "description": candidate.description,
            }
        )
    anchor_languages = sorted({detect_language(anchor.raw) for anchor in anchors})
    return {
        "query": query,
        "query_language": detect_language(query),
        "anchor_languages": anchor_languages,
        "domain": domain,
        "candidates_scanned": len(candidates),
        "results": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reduce an ALR bundle to bounded recall candidates.")
    parser.add_argument("--bundle", required=True, help="ALR bundle root containing index*.md and lessons/.")
    parser.add_argument("--query", required=True, help="Original user query, preserved for language and identifier signals.")
    parser.add_argument(
        "--anchor",
        action="append",
        default=[],
        help="Concept group; separate multilingual alternatives with |. Repeat 2-6 times.",
    )
    parser.add_argument("--domain", help="Optional lesson domain such as workspace, q1, g1, or _shared.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser.parse_args()


def emit_text(result: dict[str, object]) -> None:
    print(
        f"query_language={result['query_language']} "
        f"anchor_languages={','.join(result['anchor_languages'])} "
        f"scanned={result['candidates_scanned']}"
    )
    for item in result["results"]:
        print(f"{item['score']:>3} {item['coverage']} {item['path']}")
        print(f"    matched: {', '.join(item['matched_anchors'])}")
        if item["description"]:
            print(f"    {item['description']}")


def main() -> int:
    args = parse_args()
    try:
        bundle = Path(args.bundle).expanduser().resolve(strict=True)
        if not bundle.is_dir() or bundle == bundle.parent:
            raise RecallUsageError(f"invalid bundle directory: {bundle}")
        result = reduce_candidates(bundle, args.query, args.anchor, args.limit, args.domain)
    except (OSError, RecallUsageError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        emit_text(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
