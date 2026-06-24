#!/usr/bin/env python3
"""Report ALR/OKF references, backlinks, and broken internal links."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict

from okf_common import (
    build_markdown_index,
    default_profile_path,
    diagnostic,
    extract_links,
    is_external_link,
    iter_markdown_files,
    load_profile,
    print_error,
    redact_secret_like_value,
    relpath,
    resolve_bundle,
    resolve_internal_link,
)
from okf_common import OkfUsageError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report links, backlinks, and broken internal links for an ALR/OKF bundle."
    )
    parser.add_argument("--bundle", required=True, help="Explicit ALR bundle root to scan.")
    parser.add_argument(
        "--profile",
        default=str(default_profile_path()),
        help="ALR OKF profile contract YAML. Defaults to docs/alr-okf-profile.contract.yaml.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument(
        "--strict-links",
        action="store_true",
        help="Treat broken internal links as errors and exit 2.",
    )
    parser.add_argument(
        "--include-archives",
        action="store_true",
        help="Include _archive Markdown files in reference reporting.",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    profile = load_profile(args.profile)
    root = resolve_bundle(args.bundle)
    markdown_files = iter_markdown_files(
        root, include_archives=args.include_archives, profile=profile
    )
    md_index = build_markdown_index(root, include_archives=args.include_archives, profile=profile)
    diagnostics: list[dict[str, object]] = []
    links: list[dict[str, object]] = []
    backlinks: dict[str, set[str]] = defaultdict(set)
    counts: Counter[str] = Counter()
    scanned: list[str] = []

    for path in markdown_files:
        rel = relpath(path, root)
        scanned.append(rel)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            diagnostics.append(diagnostic("OKF_NON_UTF8", "error", rel, "file is not valid UTF-8"))
            continue
        for link in extract_links(text):
            target = link["target"]
            output_target = redact_secret_like_value(target)
            if is_external_link(target):
                counts["external"] += 1
                links.append(
                    {
                        "source": rel,
                        "target": output_target,
                        "kind": link["kind"],
                        "classification": "external",
                        "resolved": None,
                    }
                )
                continue
            resolved = resolve_internal_link(root, rel, target, md_index)
            if resolved is None:
                counts["broken_internal"] += 1
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
                        target=output_target,
                        link_kind=link["kind"],
                    )
                )
                links.append(
                    {
                        "source": rel,
                        "target": output_target,
                        "kind": link["kind"],
                        "classification": "broken_internal",
                        "resolved": None,
                    }
                )
            else:
                counts["internal"] += 1
                backlinks[resolved].add(rel)
                links.append(
                    {
                        "source": rel,
                        "target": output_target,
                        "kind": link["kind"],
                        "classification": "internal",
                        "resolved": resolved,
                    }
                )

    summary = {
        "files": len(scanned),
        "links": len(links),
        "internal": counts.get("internal", 0),
        "external": counts.get("external", 0),
        "broken_internal": counts.get("broken_internal", 0),
        "diagnostics": len(diagnostics),
    }
    result = {
        "root": str(root),
        "files_scanned": scanned,
        "summary": summary,
        "links": links,
        "backlinks": {key: sorted(value) for key, value in sorted(backlinks.items())},
        "diagnostics": diagnostics,
    }
    exit_code = 2 if args.strict_links and summary["broken_internal"] else 0
    return exit_code, result


def emit_text(result: dict[str, object]) -> None:
    summary = result["summary"]
    print(f"ALR/OKF refs root: {result['root']}")
    print(f"files_scanned: {summary['files']}")
    print(
        "links: "
        f"internal={summary['internal']} external={summary['external']} "
        f"broken_internal={summary['broken_internal']} total={summary['links']}"
    )
    print(f"backlink_targets: {len(result['backlinks'])}")
    for item in result["diagnostics"]:
        print(
            f"{item['severity']} {item['code']} {item['path']}: "
            f"{item['message']} target={item.get('target', '')}"
        )


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
