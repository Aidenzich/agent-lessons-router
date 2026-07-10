#!/usr/bin/env python3
"""Stateless, bounded candidate reduction for native ALR recall."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
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
STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "been",
    "before",
    "does",
    "from",
    "have",
    "into",
    "many",
    "more",
    "only",
    "should",
    "that",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "what",
    "when",
    "which",
    "with",
    "would",
}
MAX_LESSON_CHARS = 256 * 1024
MAX_EVIDENCE_CHARS = 360
BM25_K1 = 1.2
BM25_B = 0.75


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
    body_text: str = ""
    path_terms: set[str] = field(default_factory=set)
    metadata_terms: set[str] = field(default_factory=set)
    match_terms: dict[str, set[str]] = field(default_factory=dict)
    lexical_counts: Counter[str] = field(default_factory=Counter)
    lexical_length: int = 0
    lexical_score: float = 0.0
    raw_lexical_score: float = 0.0
    anchor_score: int = 0
    anchor_rank: int | None = None
    lexical_rank: int | None = None
    raw_lexical_rank: int | None = None
    retrieval_lanes: list[str] = field(default_factory=list)
    snippet: str = ""
    score: int = 0
    matched_anchors: list[str] = field(default_factory=list)
    match_fields: dict[str, list[str]] = field(default_factory=dict)
    query_overlap: dict[str, list[str]] = field(default_factory=dict)


def normalize(text: str) -> str:
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    text = text.casefold().replace("_", " ").replace("-", " ").replace("/", " ")
    return " ".join(TOKEN_RE.findall(text))


def latin_token_variants(token: str) -> set[str]:
    values = {token}
    if len(token) > 4:
        if token.endswith("s"):
            values.add(token[:-1])
        if token.endswith("ed"):
            values.add(token[:-2])
            values.add(token[:-2] + "e")
        if token.endswith("ing"):
            values.add(token[:-3])
            values.add(token[:-3] + "e")
    return values


def tokens(text: str) -> set[str]:
    values: set[str] = set()
    for token in TOKEN_RE.findall(normalize(text)):
        if CJK_RE.search(token):
            values.add(token)
        else:
            values.update(latin_token_variants(token))
    return values


def lexical_tokens(text: str) -> list[str]:
    values: list[str] = []
    for token in TOKEN_RE.findall(normalize(text)):
        if CJK_RE.search(token):
            values.append(token)
            for size in (2, 3):
                if len(token) >= size:
                    values.extend(token[index : index + size] for index in range(len(token) - size + 1))
        else:
            values.extend(sorted(latin_token_variants(token)))
    return values


def prepare_lexical_documents(candidates: dict[str, Candidate]) -> dict[str, int]:
    document_frequency: Counter[str] = Counter()
    for candidate in candidates.values():
        candidate.path_terms = set(lexical_tokens(candidate.path_text))
        candidate.metadata_terms = set(lexical_tokens(candidate.metadata_text))
        candidate.match_terms = {
            "path": tokens(candidate.path_text),
            "index": tokens(candidate.index_text),
            "metadata": tokens(candidate.metadata_text),
        }
        source = " ".join(
            (
                candidate.path_text,
                candidate.index_text,
                candidate.metadata_text,
                candidate.body_text,
            )
        )
        candidate.lexical_counts = Counter(lexical_tokens(source))
        candidate.lexical_length = sum(candidate.lexical_counts.values())
        document_frequency.update(candidate.lexical_counts.keys())
    return dict(document_frequency)


def discriminative_query_terms(
    query: str,
    document_frequency: dict[str, int],
    document_count: int,
) -> set[str]:
    acronyms = {normalize(value) for value in re.findall(r"\b[A-Z]{2,6}\b", query)}
    rare_threshold = max(3, math.ceil(document_count * 0.02))
    selected: set[str] = set()
    for token in lexical_tokens(query):
        if token in STOPWORDS or token in GENERIC_TERMS:
            continue
        is_cjk = bool(CJK_RE.search(token))
        is_technical_short = bool(re.fullmatch(r"[a-z]+\d+[a-z0-9]*", token))
        is_acronym = token in acronyms
        is_rare = document_frequency.get(token, 0) <= rare_threshold
        if is_cjk or len(token) > 3 or is_technical_short or is_acronym or (len(token) >= 2 and is_rare):
            selected.add(token)
    return selected


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
    text = re.sub(r"[`*#]", "", text)
    text = re.sub(r"\[([^]]+)]\([^)]*\)", r"\1", text)
    return " ".join(text.split())


def read_lesson(path: Path) -> tuple[str, str, str]:
    try:
        text = path.read_text(encoding="utf-8")[:MAX_LESSON_CHARS]
    except (OSError, UnicodeDecodeError):
        return "", "", ""

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
    body = text[match.end() :] if match else text
    return " ".join(fields), description[:MAX_EVIDENCE_CHARS], body


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
        metadata_text, description, body_text = read_lesson(path)
        candidates[relative] = Candidate(
            path=relative,
            path_text=normalize(relative.removeprefix("lessons/").removesuffix(".md")),
            metadata_text=normalize(metadata_text),
            description=description,
            body_text=body_text,
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


def score_lexical_candidates(
    candidates: dict[str, Candidate],
    query_terms: set[str],
    document_frequency: dict[str, int],
    score_attribute: str = "lexical_score",
) -> None:
    document_count = len(candidates)
    average_length = (
        sum(candidate.lexical_length for candidate in candidates.values()) / document_count
        if document_count
        else 1.0
    )
    for candidate in candidates.values():
        score = 0.0
        for term in query_terms:
            frequency = candidate.lexical_counts.get(term, 0)
            if not frequency:
                continue
            frequency_in_documents = document_frequency.get(term, 0)
            inverse_document_frequency = math.log(
                1 + (document_count - frequency_in_documents + 0.5) / (frequency_in_documents + 0.5)
            )
            length_ratio = candidate.lexical_length / average_length if average_length else 0.0
            denominator = frequency + BM25_K1 * (1 - BM25_B + BM25_B * length_ratio)
            score += inverse_document_frequency * frequency * (BM25_K1 + 1) / denominator
            if term in candidate.path_terms:
                score += inverse_document_frequency * 1.5
            elif term in candidate.metadata_terms:
                score += inverse_document_frequency * 0.5
        setattr(candidate, score_attribute, score)


def evidence_snippet(candidate: Candidate, query_terms: set[str]) -> str:
    best_line = ""
    best_score = 0
    for line in candidate.body_text.splitlines():
        cleaned = strip_markdown(line)
        if not cleaned:
            continue
        overlap = query_terms & set(lexical_tokens(cleaned))
        score = len(overlap)
        if score > best_score:
            best_line = cleaned
            best_score = score
    return (best_line or candidate.description)[:MAX_EVIDENCE_CHARS]


def score_candidate(
    candidate: Candidate,
    anchors: list[Anchor],
    identifiers: list[str],
    query_terms: set[str],
) -> Candidate:
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
            alternative = next(
                (
                    item
                    for item in anchor.alternatives
                    if alternative_matches(item, field_text, candidate.match_terms[field_name])
                ),
                None,
            )
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

    overlap_weights = {"path": 3, "index": 1, "metadata": 1}
    query_overlap: dict[str, list[str]] = {}
    overlap_score = 0
    for field_name in fields:
        overlap = sorted(query_terms & candidate.match_terms[field_name])
        if overlap:
            query_overlap[field_name] = overlap
            overlap_score += len(overlap) * overlap_weights[field_name]
    score += min(overlap_score, 18)

    coverage = len(matched)
    if coverage == len(anchors):
        score += 20
    elif coverage >= 2:
        score += 6
    candidate.anchor_score = score
    candidate.score = score
    candidate.matched_anchors = matched
    candidate.match_fields = match_fields
    candidate.query_overlap = query_overlap
    return candidate


def rank_candidates(
    candidates: dict[str, Candidate],
    evidence_terms: set[str],
    limit: int,
) -> list[Candidate]:
    anchor_ranked = [candidate for candidate in candidates.values() if candidate.matched_anchors]
    anchor_ranked.sort(
        key=lambda item: (-item.anchor_score, -len(item.matched_anchors), item.path)
    )
    lexical_ranked = [candidate for candidate in candidates.values() if candidate.lexical_score > 0]
    lexical_ranked.sort(key=lambda item: (-item.lexical_score, item.path))
    raw_lexical_ranked = [
        candidate for candidate in candidates.values() if candidate.raw_lexical_score > 0
    ]
    raw_lexical_ranked.sort(key=lambda item: (-item.raw_lexical_score, item.path))

    for rank, candidate in enumerate(anchor_ranked, 1):
        candidate.anchor_rank = rank
    for rank, candidate in enumerate(lexical_ranked, 1):
        candidate.lexical_rank = rank
    for rank, candidate in enumerate(raw_lexical_ranked, 1):
        candidate.raw_lexical_rank = rank

    # Interleave independent lanes so a bad query compilation cannot erase
    # the strongest raw-query candidate, while anchors still supply semantic aliases.
    selected: list[Candidate] = []
    seen: set[str] = set()
    lane_positions = {"concept_lexical": 0, "anchor": 0, "raw_lexical": 0}
    lanes = (
        ("raw_lexical", raw_lexical_ranked),
        ("concept_lexical", lexical_ranked),
        ("anchor", anchor_ranked),
    )
    while len(selected) < limit:
        progressed = False
        for lane_name, ranked in lanes:
            position = lane_positions[lane_name]
            while position < len(ranked) and ranked[position].path in seen:
                position += 1
            lane_positions[lane_name] = position + 1
            if position >= len(ranked):
                continue
            candidate = ranked[position]
            candidate.retrieval_lanes.append(lane_name)
            candidate.snippet = evidence_snippet(candidate, evidence_terms)
            selected.append(candidate)
            seen.add(candidate.path)
            progressed = True
            if len(selected) >= limit:
                break
        if not progressed:
            break

    for candidate in selected:
        candidate.score = (
            round(candidate.lexical_score * 100)
            + round(candidate.raw_lexical_score * 25)
            + candidate.anchor_score
        )
    return selected


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
    document_frequency = prepare_lexical_documents(candidates)
    raw_query_terms = discriminative_query_terms(query, document_frequency, len(candidates))
    concept_query = " ".join(anchor.raw.replace("|", " ") for anchor in anchors)
    concept_query_terms = discriminative_query_terms(
        concept_query, document_frequency, len(candidates)
    )
    score_lexical_candidates(
        candidates,
        raw_query_terms,
        document_frequency,
        score_attribute="raw_lexical_score",
    )
    score_lexical_candidates(candidates, concept_query_terms, document_frequency)
    for candidate in candidates.values():
        score_candidate(candidate, anchors, identifiers, raw_query_terms)
    ranked = rank_candidates(candidates, raw_query_terms | concept_query_terms, limit)

    results = []
    for candidate in ranked:
        results.append(
            {
                "path": candidate.path,
                "score": candidate.score,
                "anchor_score": candidate.anchor_score,
                "lexical_score": round(candidate.lexical_score, 4),
                "raw_lexical_score": round(candidate.raw_lexical_score, 4),
                "anchor_rank": candidate.anchor_rank,
                "lexical_rank": candidate.lexical_rank,
                "raw_lexical_rank": candidate.raw_lexical_rank,
                "retrieval_lanes": candidate.retrieval_lanes,
                "coverage": f"{len(candidate.matched_anchors)}/{len(anchors)}",
                "matched_anchors": candidate.matched_anchors,
                "match_fields": candidate.match_fields,
                "query_overlap": candidate.query_overlap,
                "description": candidate.description,
                "snippet": candidate.snippet,
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
