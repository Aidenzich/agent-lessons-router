---
type: Agent Memory Profile
title: ALR OKF Profile
description: OKF-compatible profile rules for Agent-Lessons-Router bundles.
tags: [alr, okf, agent-memory, profile, contract]
timestamp: 2026-06-24
profile: alr-agent-memory
profile_version: "0.1"
---

# ALR OKF Profile

ALR is an OKF-compatible Agent Memory Profile. OKF supplies the portable file substrate: UTF-8 Markdown, YAML frontmatter for concepts, reserved indexes, optional logs, links, and permissive consumers. ALR supplies the operational consumption protocol: find-up bootstrap, deterministic router indexes, priority-aware retrieval, domain sub-index ownership, recency-cache hygiene, and Learn/Maintain SOP.

OKF compatibility is additive. Tools must not replace ALR routing tables with a generic catalog layout, infer a second routing authority from metadata, or reject historical ALR content merely because optional OKF fields are absent.

## Bundle Root

An ALR bundle root is the `.agent-lessons/` directory discovered by the ALR find-up algorithm:

1. Start at the current working directory.
2. If `.agent-lessons/` exists, that directory is `PROJECT_ROOT/.agent-lessons`.
3. Otherwise move to the parent and repeat until `/`.
4. If no ancestor has `.agent-lessons/`, initialize in the current working directory with the ALR installer.

Bootstrap tools must use parent-only find-up. Broad recursive scans from a monorepo or workspace root are not valid ALR discovery, including relative scans such as `find .. -name .agent-lessons -type d -print` from inside a large workspace. If a broad discovery scan is started by mistake, abort it and retry with parent-only find-up instead of waiting for it to traverse generated workspaces or dependency trees.

## File Classes

ALR bundles contain these file classes:

| Class | Paths | OKF treatment | ALR treatment |
|-|-|-|-|
| Lesson concepts | `lessons/**/*.md`, except reserved index/log names | OKF concept documents; new or migrated files should have parseable frontmatter with `type` | Atomic operational rules read after router selection |
| Context concepts | `context/**/*.md` | OKF concept documents | Project mental model and stable context |
| Repository guides | `repos/**/*.md` | OKF concept documents | Source-reading routes for repos and services |
| Artifacts and references | `artifacts/**/*.md`, `references/**/*.md` when present | OKF concept documents unless the filename is reserved | Longer supporting material; not a replacement for lesson rows |
| Router indexes | `index.md`, `index_*.md`, directory `index.md` files | Reserved OKF index files for progressive disclosure | Deterministic ALR router tables and domain sub-index homes |
| Logs | `log.md`, `**/log.md` when present | Reserved OKF log files | Optional update history |
| Archives | `_archive/**`, `**/_archive/**` | Preserved historical material; may be partial OKF | Not a primary routing surface |

## Lesson Concepts

New ALR lesson concept files should include YAML frontmatter with at least:

```yaml
---
type: Lesson
---
```

Recommended frontmatter:

```yaml
title: <short human title>
description: <one-sentence rule>
tags: [<domain>, <topic>]
timestamp: <ISO 8601 date or datetime>
```

ALR extension fields are producer-defined OKF fields and must be preserved:

| Field | Meaning |
|-|-|
| `priority` | Retrieval and cache importance: `P0`, `P1`, or `P2`. |
| `domain` | Owning routing domain, matching the durable sub-index and usually the folder under `lessons/`. |
| `index_home` | Durable router home such as `index_workspace.md` or `index_q1.md`. |
| `lesson_status` | Lifecycle state such as `active`, `superseded`, `archived`, or `draft`. |
| `supersedes` / `superseded_by` | Optional bundle-relative paths for replacement chains. |

Historical ALR notes without frontmatter remain readable. Migration tools may add frontmatter, but consumers must continue to parse and route old files through indexes, filenames, paths, headings, and body text.

## Index Compatibility

`index.md` and `index_*.md` are reserved index files. They are not concepts and must not be required to carry concept frontmatter. The bundle-root `index.md` may use the OKF root-version exception if needed, but ALR tools must not require it.

ALR index rules:

- Root `index.md` is the master router and first read after find-up.
- `index_*.md` files are domain sub-indexes and the durable homes for lesson rows.
- Index rows are routing data. Do not derive a conflicting route from lesson frontmatter.
- A lesson in `Latest Lessons` must also have a durable row in a domain sub-index or pinned/cross-cutting table.
- `Latest Lessons` is a recency cache, not the system of record.
- Cache rows should include `[P0]`, `[P1]`, or `[P2]`; truncation evicts older routine `[P2]` rows before important `[P0]`/`[P1]` rows.
- Domain-package folders such as `lessons/workspace/` or `lessons/q1/` must match their owning domain sub-index when the bundle uses Level 4+ maintenance structure.

OKF-aware tools may synthesize navigation from frontmatter for display, but ALR consumers must still use router indexes for operational lookup and must preserve index table structure when round-tripping.

## Retrieval Protocol

ALR consumption is deterministic:

1. Bootstrap with find-up.
2. Read root `index.md`.
3. Pick the closest `index_*.md` by task domain, tags, or explicit router row.
4. Read only the relevant lesson files or supporting artifacts.
5. Treat P0/P1 lessons and directly matching domain lessons as stronger than recency-only cache hits.
6. When blocked or unsure, consult lessons before guessing.

Broken internal links are warning-level by default. OKF requires consumers to tolerate broken links because knowledge can be partial, archived, or future-facing. Strict tools may fail broken links only when explicitly configured.

## Learn And Maintain SOP

The profile preserves the ALR SOP:

- `docs/learn.md` controls when and how to write new lessons.
- `docs/maintain.md` controls compression, folder ownership, sub-index evolution, archive handling, and Latest Lessons cache hygiene.
- New lessons should be concise operational conclusions, not chronological logs.
- New or moved lessons must update the durable router home before or together with any Latest Lessons cache entry.
- Maintain operations must preserve unknown OKF/profile frontmatter fields.

## Migration Policy

Historical ALR bundles are partially OKF-compatible by consumption even when individual lesson files lack frontmatter. Migration should be incremental:

1. Do not block reading old lessons because optional OKF metadata is missing.
2. Add `type: Lesson` or a more specific OKF type when a lesson is touched or migrated.
3. Preserve existing headings, router-table rows, wiki links, markdown links, and unknown frontmatter fields.
4. Keep `index.md` and `index_*.md` as router indexes.
5. Keep archived or obsolete material under `_archive/` and avoid making archives the primary routing surface.

## Safe Tooling Rules

Tools that lint, migrate, index, or expose ALR bundles must load `docs/alr-okf-profile.contract.yaml` first. Downstream tasks should fail fast if the contract is absent after dependency merge/adoption.

Default safety rules:

- Do not print full lesson bodies by default; use file paths, headings, frontmatter, and short snippets.
- Do not print secrets or credential-like values. Redact by default.
- Preserve unknown fields and unknown types.
- Warn on broken links by default; strict mode may fail.
- Treat `.agent-lessons/` as project knowledge, not product runtime data.
- Do not write project-specific lessons into the installed skill directory.
- Do not create a second routing authority from OKF metadata; ALR router indexes remain authoritative.
