# Phase 3: Learn & Write (Post-task)

We refuse the accumulation of errors, and we refuse the accumulation of nonsense. Every Lesson must be a **highly precise conclusion that can be directly executed**, rather than a lengthy story or background description.

## Terminal Authoring Gate (Gatekeeper)

For new lessons and ordinary updates, timing and worthiness are separate gates. Both must pass.

### 1. Timing gate

Persist a lesson only when one of these is true:

- **Terminal handoff:** the requested deliverable is complete, required verification and review have
  passed, and no known finding or rework remains.
- **Explicit human instruction:** the user says to record the conclusion now or invokes `/learn`.
- **Verified urgent correction:** an existing active lesson has been independently proven stale or
  unsafe, and leaving it active could continue to mislead this or another agent.

Passing one focused test, completing one phase, encountering a retry, or discovering a plausible
gotcha does **not** make an active task terminal. While work remains, retain proposed lessons only as
candidate notes in task context or the working plan. Do not write a draft lesson, update router
indexes, or synchronize a derived memory store.

For a genuinely ended or blocked task, a verified durable finding may be written at handoff, but an
unresolved hypothesis may not. State the evidence boundary precisely.

### 2. Worthiness gate

After the timing gate passes, write only when **any one** of these is true:

- The completed and verified work produced a durable, non-obvious operational conclusion.
- A human explicitly instructed: "Record this down", "Remember this gotcha", or used `/learn`.
- **Complexity/Difficulty Encountered**: the completed task took more than one try, involved
  non-obvious infrastructure knowledge, or required a significant architectural pivot.

Tests passing support the conclusion, but are not by themselves a reason to create a lesson and do
not override the timing gate.

### Mandatory Correction Obligation

If an Agent follows a Lesson and independently proves during execution that the active rule is
stale or unsafe, **that Agent has an absolute obligation to correct it without waiting for ordinary
post-task authoring**. This exception is narrow:

- Persist only the verified correction, not the surrounding unresolved diagnosis.
- Preserve the evidence boundary and correction lineage.
- Re-run the relevant retrieval or read-back check after the correction.
- If the lesson is merely incomplete, ambiguous, or suspected, keep a candidate note and wait for
  the terminal handoff gate.

We must maintain a self-healing knowledge base without publishing provisional conclusions.

### Consolidation Principle (Anti-Sprawl)

Before creating a new Lesson, you must first check if a similar or related Lesson already exists. **Prioritize updating and expanding existing Lessons** rather than creating new, fragmented files for highly homogeneous content. Aim for fewer, higher-quality, and more comprehensive Lesson "pillars".
### The Complexity Threshold (Mandatory Learning)

At terminal handoff, you are **obligated** to create or update a lesson if any of the following occurred:
1. **Multiple Attempts**: You had to refine your approach because the first attempt failed or was suboptimal.
2. **Hidden Gotchas**: You discovered a constraint that wasn't documented in the source but required investigation (e.g., hidden environment variables, specific version quirks).
3. **Infrastructure Magic**: You had to use specific terminal commands or scripts that are not part of the standard `npm/make` workflow.
4. **Architectural Pivots**: You chose one design pattern over another for a specific reason that might affect future stability.

**Rule of thumb:** If the next agent would likely spend more than 2 minutes "figuring it out" without your notes, it belongs in a Lesson.

This threshold decides whether a completed task must teach ALR. It never authorizes writing while
implementation, verification, review, or rework is still active.


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

## Related (Mandatory when a related lesson exists)
<!-- [[wiki-link]] every EXISTING lesson that shares this one's subsystem, mechanism, or failure-mode, each with a ≤1-line note on how it differs/relates. See "Link Related Lessons" below. If genuinely none exists, omit the section. -->
<!-- Example: "- [[loop_manager_ratelimit_backoff_ignores_resetsat]] — dispatcher-level backoff (different layer than this harness-level gap)." -->

## Refs (Optional)
<!-- Non-lesson pointers only: source file paths, URLs, tickets. A pure list without explanatory text. Lesson-to-lesson links belong in Related, not here. -->

## Updated
<!-- YYYY-MM-DD -->
```

**Anti-patterns — The following content is forbidden in a Lesson:**
- ❌ Lengthy Context / Background stories ("We were doing project X back then, and because of requirement Y...")
- ❌ A chronological log of the exploration process ("First tried A, didn't work, then tried B...")
- ❌ Obvious conclusions ("Testing is important", "Read the documentation")

## Link Related Lessons (Mandatory)

A lesson is a node in a knowledge graph, not an island. Before finalizing, you **must** connect it to what already exists:

1. **Find neighbors.** Run one ALR recall (`alr_recall.py`) with the new lesson's core concepts to surface existing lessons that share its **subsystem, mechanism, or failure-mode**. (You already did a Consolidation check for *merge* candidates; this is the same search reused for *linking* the ones too distinct to merge.)
2. **Link them in `## Related`.** For every highly-related existing lesson, add a `[[wiki-link]]` in the new lesson's `## Related` section with a ≤1-line note on how it **differs or relates** (same layer? sibling bug? opposite side of a contrast? prerequisite?). A bare link with no distinction note is not enough — the note is what stops a future agent from conflating two adjacent lessons.
3. **Backlink (bidirectional).** If a neighbor is close enough that an agent reading *it* would also want *this* one, add a reciprocal `[[wiki-link]]` into that neighbor's `## Related`/`Don't` line. Cross-links must not be one-way, or half the graph is undiscoverable from the other half.
4. **Scope discipline.** Link only genuinely related lessons (shared entity/mechanism/failure-mode). Do NOT spray links to loosely-topical or same-domain-but-unrelated lessons — link spam is as harmful as no links. If truly nothing is related, omit `## Related` (do not invent neighbors).

Note: `[[wiki-link]]` uses the target lesson's **file name** (slug), and is unaffected by later folder migrations. A `## Related` link is a navigation aid; it still does NOT count as the target's durable home (see the Router Table rules below).

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
