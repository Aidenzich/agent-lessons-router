#!/usr/bin/env python3
"""Lint an ALR/OKF bundle without printing lesson bodies."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from okf_common import (
    build_markdown_index,
    classify_file,
    default_profile_path,
    diagnostic,
    extract_links,
    is_external_link,
    iter_markdown_files,
    load_profile,
    parse_frontmatter,
    print_error,
    redact_secret_like_value,
    relpath,
    resolve_bundle,
    resolve_internal_link,
)
from okf_common import OkfUsageError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint an Agent-Lessons-Router bundle against the ALR OKF profile."
    )
    parser.add_argument("--bundle", required=True, help="Explicit ALR bundle root to scan.")
    parser.add_argument(
        "--profile",
        default=str(default_profile_path()),
        help="ALR OKF profile contract YAML. Defaults to docs/alr-okf-profile.contract.yaml.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict", action="store_true", help="Exit 2 on OKF/profile lint errors.")
    parser.add_argument(
        "--strict-links",
        action="store_true",
        help="Treat broken internal links as errors and exit 2.",
    )
    parser.add_argument(
        "--include-artifacts",
        action="store_true",
        help="Include artifacts/**/*.md in concept frontmatter linting.",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    profile = load_profile(args.profile)
    root = resolve_bundle(args.bundle)
    markdown_files = iter_markdown_files(root, include_archives=False, profile=profile)
    md_index = build_markdown_index(root, include_archives=False, profile=profile)
    diagnostics: list[dict[str, object]] = []
    classes: Counter[str] = Counter()
    scanned: list[str] = []

    for path in markdown_files:
        rel = relpath(path, root)
        file_class = classify_file(rel, profile, include_artifacts=args.include_artifacts)
        classes[file_class] += 1
        scanned.append(rel)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            diagnostics.append(diagnostic("OKF_NON_UTF8", "error", rel, "file is not valid UTF-8"))
            continue

        if file_class in {"lesson", "context", "repo-guide", "artifact", "reference"}:
            frontmatter, parse_error = parse_frontmatter(text)
            if parse_error:
                diagnostics.append(
                    diagnostic("OKF_FRONTMATTER_PARSE_ERROR", "error", rel, parse_error)
                )
            elif frontmatter is None:
                diagnostics.append(
                    diagnostic(
                        "OKF_MISSING_FRONTMATTER",
                        "warning",
                        rel,
                        "concept file has no YAML frontmatter; historical ALR files are tolerated",
                    )
                )
            else:
                missing = [
                    key
                    for key in profile.get("required_frontmatter", [])
                    if not str(frontmatter.get(key, "")).strip()
                ]
                for key in missing:
                    diagnostics.append(
                        diagnostic(
                            "OKF_MISSING_TYPE" if key == "type" else "OKF_MISSING_REQUIRED_FRONTMATTER",
                            "error",
                            rel,
                            f"concept frontmatter is missing non-empty top-level {key!r}",
                        )
                    )
                metadata = frontmatter.get("metadata")
                if "type" in missing and isinstance(metadata, dict) and metadata.get("type"):
                    diagnostics.append(
                        diagnostic(
                            "ALR_NESTED_METADATA_TYPE",
                            "warning",
                            rel,
                            "metadata.type is present, but OKF requires top-level type",
                        )
                    )

        for link in extract_links(text):
            target = link["target"]
            if is_external_link(target):
                continue
            resolved = resolve_internal_link(root, rel, target, md_index)
            if resolved is None:
                default_link_severity = profile.get("tooling_contract", {}).get(
                    "default_link_check_severity", "warning"
                )
                strict_link_severity = profile.get("tooling_contract", {}).get(
                    "strict_link_check_severity", "error"
                )
                severity = strict_link_severity if args.strict_links else default_link_severity
                diagnostics.append(
                    diagnostic(
                        "OKF_BROKEN_INTERNAL_LINK",
                        severity,
                        rel,
                        "internal link target was not found",
                        target=redact_secret_like_value(target),
                        link_kind=link["kind"],
                    )
                )

    severity_counts = Counter(str(item["severity"]) for item in diagnostics)
    code_counts = Counter(str(item["code"]) for item in diagnostics)
    summary = {
        "diagnostics": len(diagnostics),
        "errors": severity_counts.get("error", 0),
        "warnings": severity_counts.get("warning", 0),
        "codes": dict(sorted(code_counts.items())),
        "file_classes": dict(sorted(classes.items())),
    }
    result = {
        "root": str(root),
        "files_scanned": scanned,
        "summary": summary,
        "diagnostics": diagnostics,
    }
    exit_code = 0
    if args.strict and summary["errors"]:
        exit_code = 2
    if args.strict_links and any(item["code"] == "OKF_BROKEN_INTERNAL_LINK" for item in diagnostics):
        exit_code = 2
    return exit_code, result


def emit_text(result: dict[str, object]) -> None:
    summary = result["summary"]
    print(f"ALR/OKF lint root: {result['root']}")
    print(f"files_scanned: {len(result['files_scanned'])}")
    print(
        "diagnostics: "
        f"errors={summary['errors']} warnings={summary['warnings']} total={summary['diagnostics']}"
    )
    print(f"file_classes: {json.dumps(summary['file_classes'], sort_keys=True)}")
    for item in result["diagnostics"]:
        extra = ""
        if "target" in item:
            extra = f" target={item['target']}"
        print(f"{item['severity']} {item['code']} {item['path']}: {item['message']}{extra}")


def main() -> int:
    args = parse_args()
    try:
        exit_code, result = run(args)
    except OkfUsageError as exc:
        print_error(str(exc))
        return 1
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        emit_text(result)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
