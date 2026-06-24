# Phase 3: Learn & Write (Post-task)

We refuse the accumulation of errors, and we refuse the accumulation of nonsense. Every Lesson must be a **highly precise conclusion that can be directly executed**, rather than a lengthy story or background description.

## Writing Prerequisite (Gatekeeper)

A lesson can only be written if **any one** of the following conditions is met:
- The code has passed tests (CI/Tests Passed).
- A human explicitly instructed: "Record this down", "Remember this gotcha", or used the `/learn` command.
- **Complexity/Difficulty Encountered**: The task took more than one try, involved non-obvious infrastructure knowledge, or required a significant architectural pivot.

### Mandatory Correction Obligation

If an Agent follows a Lesson but encounters errors or discovers that the information is stale/incorrect during execution, **that Agent has an absolute obligation to immediately correct or update said Lesson**. We must maintain a "self-healing" knowledge base.

### Consolidation Principle (Anti-Sprawl)

Before creating a new Lesson, you must first check if a similar or related Lesson already exists. **Prioritize updating and expanding existing Lessons** rather than creating new, fragmented files for highly homogeneous content. Aim for fewer, higher-quality, and more comprehensive Lesson "pillars".
### The Complexity Threshold (Mandatory Learning)

You are **obligated** to create or update a lesson if any of the following occurred:
1. **Multiple Attempts**: You had to refine your approach because the first attempt failed or was suboptimal.
2. **Hidden Gotchas**: You discovered a constraint that wasn't documented in the source but required investigation (e.g., hidden environment variables, specific version quirks).
3. **Infrastructure Magic**: You had to use specific terminal commands or scripts that are not part of the standard `npm/make` workflow.
4. **Architectural Pivots**: You chose one design pattern over another for a specific reason that might affect future stability.

**Rule of thumb:** If the next agent would likely spend more than 2 minutes "figuring it out" without your notes, it belongs in a Lesson.


### Formatting Guidelines

Create a Markdown file under `PROJECT_ROOT/.agent-lessons/lessons/`, and the naming must be specific (e.g., `stripe_webhook_idempotency.md`).

**If the knowledge base uses domain-package folders** (Level 4+ — `lessons/<domain>/` each owned by a sub-index, see `maintain.md` Step 4), do NOT drop the file in the flat `lessons/` root: write it into the folder matching its sub-index (e.g. `lessons/g1/...`), and put cross-cutting / shared-infra lessons in `lessons/_shared/`. Physical location is the ownership signal — keep folder == declared domain.

**OKF profile requirement:** New ALR lesson concept files must include YAML frontmatter with non-empty `type`. When touching an existing historical lesson that lacks frontmatter, add frontmatter before saving it unless the edit is only a mechanical path rewrite. The authoritative profile contract is `<SKILL_DIR>/docs/alr-okf-profile.contract.yaml`; preserve unknown OKF/ALR fields when editing.

**Formatting Advice:** If appropriate, you can use Markdown Tables to organize information. However, please pay special attention: **when using a Table, only one `-` is needed per column separator**, for example:

|-|-|-|

This effectively avoids generating too many separator characters, which can lead to token waste or slow generation.

```markdown
---
type: Lesson
title: [Precise Title, e.g., Stripe Webhook MUST do idempotency check]
description: [One-sentence conclusion]
tags: [domain, topic]
timestamp: YYYY-MM-DD
priority: P0|P1|P2
domain: [owning-domain]
index_home: index_<domain>.md
lesson_status: active
---

# [Precise Title, e.g., Stripe Webhook MUST do idempotency check]

## Rule
<!-- A one-sentence conclusion. This is the most important part of the entire file. -->
<!-- Example: "The Stripe webhook handler must use event.id for idempotency checks, otherwise retries will lead to duplicate charges." -->

## Don't
<!-- The wrong approach, in one sentence. Omit obvious content. -->
<!-- Example: "Do not trust the arrival order of webhooks." -->

## Why (Optional)
<!-- Only write if the reason is not obvious. Limit to 1-2 sentences. -->

## Refs (Optional)
<!-- Related file paths or links, as a pure list without explanatory text. -->

## Updated
<!-- YYYY-MM-DD -->
```

**Anti-patterns — The following content is forbidden in a Lesson:**
- ❌ Lengthy Context / Background stories ("We were doing project X back then, and because of requirement Y...")
- ❌ A chronological log of the exploration process ("First tried A, didn't work, then tried B...")
- ❌ Obvious conclusions ("Testing is important", "Read the documentation")

## Update the Router Table

After writing a Lesson, you must synchronously update `PROJECT_ROOT/.agent-lessons/index.md` in this format:

| File Path | One-Sentence Conclusion | Tags |
|-|-|-|

**`Latest Lessons` is a recency cache (~20 rows) that gets truncated — so add a lesson there only if it ALSO has a durable home that survives truncation:**

1. **Home first (mandatory, eviction-safety).** Register the lesson as its **own row** in the relevant domain sub-index (`index_*.md`). A `[[wiki-link]]` mention inside another lesson's row does NOT count as a home — when the cache row is later evicted, an unhomed lesson becomes grep-only.
2. **Cross-cutting lessons need a real home.** If the lesson spans multiple families or is shared infra/tooling/credentials (e.g. decryption keys, ClickHouse access, DB-routing invariants), home it in the master index's `Cross-cutting` / pinned section — do NOT bury it under a single domain's row.
3. **Tag importance.** Prefix each `Latest Lessons` row with `[P0]`/`[P1]`/`[P2]`. Truncation evicts the oldest **routine (`[P2]`)** row first and never drops a `[P0]`/`[P1]` to make room.
4. **Fold homogeneous series.** If your lesson is one of a formulaic series (same template, different entity), keep a single **umbrella row** in the sub-index instead of adding a new `Latest Lessons` row per entry.

OKF frontmatter helps portable consumers, but it does not replace ALR routing. The router table row and durable sub-index home remain the operational source of truth.

## Clean up Obsolete Information

If a newly verified result conflicts with an old Lesson, **directly overwrite or delete** the obsolete rule. The knowledge base only retains current, correct conclusions.
