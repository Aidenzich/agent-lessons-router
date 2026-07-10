---
name: agent-lessons-router
description: |
  CRITICAL DIRECTIVE: Knowledge Persistence & Routing & Memory Management
  Always prioritize writing project experiences, environment variables configs like git token , PR, operational rules, and known pitfalls (gotchas) to the .agent-lessons/ directory as physical files. Do NOT rely solely on your internal memory.

  You must understand that ALR (Agent Lessons Router) lessons SUPERSEDE your internal memory. ALR serves as the authoritative, project-level knowledge base. Because ALR lessons are shared across all agents and utilize deterministic index routing, they are structurally stronger, permanent, and vastly superior to ephemeral memory for enforcing system architecture and preventing regressions.

metadata:
  tags: [workflow, architecture, knowledge-base, memory, alr, ddd, debugging, SOP, parity]

---

# Agent-Lessons-Router (ALR)

This project adopts "Progressive Disclosure" to manage AI context. You **absolutely must NOT** guess the system architecture or past decisions out of thin air, and you **absolutely must NOT** casually add new experiences without validation.

Please strictly follow the Standard Operating Procedure (SOP) below:

---

## Core Philosophy

**When in doubt, encountering a technical block, or facing an unknown project state, your first and most critical action is to consult the existing lessons (`.agent-lessons/`).** Do not rely on assumptions or general knowledge; always prioritize the project's historical records and architectural decisions preserved in the lessons. Consulting lessons is a "survival instinct," not just a pre-task step.

## OKF-Compatible Agent Memory Profile

ALR is an OKF-compatible Agent Memory Profile: OKF is the portable markdown plus frontmatter file format, while ALR is the consumption protocol that tells agents how to find, prioritize, route, read, write, and maintain project memory. OKF compatibility is additive and must not flatten ALR into a generic catalog or replace ALR router semantics.

The authoritative profile contract lives in `docs/alr-okf-profile.contract.yaml`, with human-readable rules in `docs/alr-okf-profile.md`. Tools that lint, migrate, index, or round-trip ALR bundles must load that contract instead of duplicating rules from prose. Unknown OKF or ALR profile fields must be preserved, not rejected or silently discarded.

ALR indexes remain deterministic router indexes and OKF progressive-disclosure indexes. `index.md` and `index_*.md` are reserved routing files, not lesson concepts. They must preserve find-up bootstrap, P0/P1/P2 priority, domain sub-index homes, Latest Lessons as a recency cache, Learn/Maintain SOP, and the rule to consult lessons before guessing.

## Continuous Triggering & Injection

You must treat ALR as an active, continuous verification tool rather than a one-time startup script. Specifically, you must proactively trigger ALR searches in the following scenarios:

- **Example 1: Post-Implementation Verification**: Immediately after finishing a coding task (before declaring it complete or sending it for review), you must instinctively consult `.agent-lessons/` to verify: "Did I forget any established project constraints, edge cases, or review rules?"
- **Example 2: TODO List Injection**: Whenever you are creating a TODO list or Implementation Plan, you must deliberately inject "Consult ALR for relevant lessons" as a mandatory sub-task at the end of *every major phase*. This ensures that the project context and rules are continuously refreshed and injected into your memory.

---

## Terminology & Boundaries

To avoid confusion, the Agent must distinguish between the following two physical paths:

- **PROJECT_ROOT**: The nearest ancestor directory (including the current directory) that contains a `.agent-lessons/` folder. This is where all **project-specific** knowledge, lessons, and automation scripts must reside. If no such directory exists after a hierarchical search, it defaults to the Current Working Directory (CWD).
- **SKILL_DIR (Skill Installation Directory)**: The directory where this Skill's logic resides. It is used only for storing **tool-core** SOP guidelines (`docs/`), universal installation scripts (`scripts/`), or cross-project infrastructure logic. It is **strictly forbidden** to save project-specific lessons or scripts into this directory.

Principle: **Knowledge stay at the highest relevant level (Lessons Root), tools stay with the Skill (Global).**

---

## Phase 0: Bootstrap & Hierarchical Search (Find-Up)

**Before initializing, you must check if a lessons folder already exists in an ancestor directory.** This avoids redundant initializations in subprojects of a monorepo.

1. **Find-Up Logic**: Start at the current directory. If `.agent-lessons/` is NOT present, move to the parent directory and repeat until found or the root `/` is reached.
2. **Set PROJECT_ROOT**: Once `.agent-lessons/` is found, that directory is your `PROJECT_ROOT`. 
3. **Fallback Initialization**: If NO ancestor contains `.agent-lessons/`, execute the installation script in the **current working directory**:
 
 ```bash
 bash <SKILL_DIR>/scripts/install.sh
 ```

### Search Safety Rules

ALR lookup must be cheap, bounded, and deterministic. Do **not** launch broad recursive `find` commands from a monorepo/workspace root just to locate `.agent-lessons`; those scans can traverse copied workspaces, `node_modules`, `.git`, generated `dist`, and other huge dependency trees. This includes seemingly small commands like `find .. -name .agent-lessons -type d -print` when the current directory lives inside a large workspace.

Use only a parent-only find-up loop for bootstrap:

```bash
dir="$PWD"
while [ "$dir" != "/" ]; do
  if [ -d "$dir/.agent-lessons" ]; then
    printf '%s\n' "$dir"
    break
  fi
  dir="$(dirname "$dir")"
done
```

If a content search is truly required after `PROJECT_ROOT` is known, search only inside `PROJECT_ROOT/.agent-lessons` with `rg` first. If `find` is unavoidable, prune heavy directories explicitly:

```bash
find "$PROJECT_ROOT/.agent-lessons" \
  \( -name .git -o -name node_modules -o -name dist -o -name .agents-workspace -o -name .repos \) -prune -o \
  -type f -name '*.md' -print
```

Forbidden patterns:

```bash
rg --files "$PROJECT_ROOT/.agent-lessons"
rg --files .
sed -n '1,220p' "$PROJECT_ROOT/.agent-lessons/index.md"
sed -n '1,260p' "$PROJECT_ROOT/.agent-lessons/index_workspace.md"
find /path/to/workspace -path '*/.agent-lessons/*' -print
find .. -name .agent-lessons -type d -print
find .. -name .agent-lessons -type d -prune
find "$PROJECT_ROOT" -name index.md -path '*/.agent-lessons/index.md' -print
```

If you accidentally start a broad discovery scan, stop it immediately (for example by interrupting the running tool/session) and retry with parent-only find-up. Do not wait for the broad scan to finish. When an existing automation uses broad ALR discovery, fix the automation before running another batch. Do not leave orphaned `find` processes scanning agent workspaces or dependency folders.

Raw `rg --files` output is inventory, not recall. Never print it into model context. A precise, bounded filename pipeline is allowed because lesson slugs are semantic summaries: `rg --files "$ALR/lessons" | rg -i '<paired-pattern>' | sed -n '1,12p'`. Likewise, do not read a fixed large prefix of an index just because it exists: large router indexes are lookup tables, not onboarding documents.

---

## Phase 1: Recall & Retrieve (Pre-task & Troubleshooting)

Before starting to write code or debug, **and immediately upon any command failure or technical block**, check for relevant history in the discovered `PROJECT_ROOT` using this reducer-first procedure:

1. **Compile concept groups once:** Extract 2-5 discriminative concept groups. Cover every material query clause: entity/component, operation/mechanism, and relation/outcome. Put original-language and concise target-language implementation alternatives in the same group, preserving literal identifiers. Example: `本地記憶|local memory|memory runtime`. Do not spend separate tool calls on each language, omit the entity anchor, or replace a predictive/contrast relation with a generic cost term.
2. **Run the stateless reducer:** Call `<SKILL_DIR>/scripts/alr_recall.py` once with the original query and repeated `--anchor` groups. It scans lesson paths, router rows, and frontmatter summaries locally, then returns at most five candidates; it does not build a database, read lesson bodies, or emit the raw corpus inventory.
   - Treat exit 0 plus valid JSON as a successful, trusted result. Never repeat an identical reducer call, inspect/debug the reducer source, change `TMPDIR`, or probe the Python runtime after success.
3. **Accept candidates by coverage, not rank alone:** Read at most one candidate whose description directly covers the query's material clauses. If every candidate covers fewer than half the anchors or clearly misses the entity/relation, do not read a body; correct the anchors and make at most one more reducer call.
4. **Stop after direct support:** Once the read lesson directly supports every material clause, answer immediately. Do not run confirmatory `rg`, read sibling lessons, or search for the user's exact wording.
5. **Use native fallback only when needed:** Only after two inadequate reducer calls, use one precise filtered-filename or router-index search. Select the closest `index_<domain>.md`; read only matching rows plus small context, not a fixed 200+ line prefix.
6. **Widen one step at a time:** Widen only when the reducer and precise fallback produced no adequate concrete lesson path. Relax one constraint or search the selected domain's lessons with the same paired-concept rule. Search all lesson domains only as the final ALR fallback.
7. **Fallback outside ALR:** If no relevant record exists after bounded widening, continue sequentially to the most recent agent-facing project guidance, repo-local skills/tool config, then source structure. Do not read irrelevant lessons.

Preferred command shape:

```bash
ALR="$PROJECT_ROOT/.agent-lessons"
python3 <SKILL_DIR>/scripts/alr_recall.py \
  --bundle "$ALR" \
  --query '<original user problem>' \
  --anchor '本地記憶|local memory|memory runtime' \
  --anchor '寫入|store|persist' \
  --anchor '查詢|recall|lookup' \
  --anchor '佇列|queue|worker' \
  --limit 5

# Fallback only when the reducer has no adequate candidate.
rg --files "$ALR/lessons" \
  | rg -i 'memory.*(store|recall)|(store|recall).*memory' \
  | sed -n '1,12p'
rg -n -i -C 2 -m 8 --glob 'index*.md' \
  'rate.?limit.*(reset|backoff)|(reset|backoff).*rate.?limit' "$ALR" \
  | sed -n '1,60p'
rg -n -i -C 2 -m 20 \
  'app.*header|database.*routing' "$ALR/index_q1.md"
cat "$ALR/lessons/<domain>/<lesson>.md"
```

Recall anti-patterns:

- Printing every lesson before forming a query (`rg --files .` without a precise bounded filter).
- Running separate original-language and translated searches instead of one multilingual reducer call.
- Reading multiple candidate bodies before checking the reducer's highest-coverage path.
- Reading a low-coverage candidate whose description does not cover the entity and relation.
- Running confirmatory searches after a direct lesson already answers every query clause.
- Re-running or debugging a successful reducer invocation instead of consuming its candidates.
- Reading the first 220/260 lines of large indexes without a matched section.
- One giant OR query combining generic words such as `build|host|service|process|runtime|...`.
- Adding a generic standalone branch to an otherwise precise query, such as `reset.*backoff|backoff.*reset|stale`.
- Searching every domain before trying the router indexes and closest domain index.
- Continuing to search a whole domain after router output already exposed a task-matching lesson path.
- Continuing after the decisive lesson is verified merely to collect more sources.

---

## Phase 2: Review & Retrospection (Post-execution)

Before the implementation enters its final phase, you must read `<SKILL_DIR>/docs/retro.md` and forcibly engage in self-review (or initiate a Subagent for review). This phase aims to combat "Happy Path" blind spots and ensure the modifications fully align with the user's deep intentions and the project's edge conditions. If any discrepancies are found, you must immediately rework and fix them.

---

## Phase 3: Learn & Write (Post-task)

When the review passes, the task is fully completed, and there is a need to record the experience, read `<SKILL_DIR>/docs/learn.md` and follow its complete writing SOP. **All new lessons and project-specific scripts must be written to the discovered `PROJECT_ROOT/.agent-lessons/`.**

> [!IMPORTANT]
> **Mandatory Learning & L1 Cache Rule**: If an iteration involved complexity, difficulty, or required non-obvious infrastructure knowledge, you **MUST** record a new lesson or update an existing one.
>
> The master `index.md` `Latest Lessons` table is a **recency cache, not the system of record**. The durable home of every lesson is its **own row in a domain sub-index** (`index_*.md`) or a pinned table. When adding a lesson, follow these in order:
> 1. **Home first, then cache.** Before (or together with) appending to `Latest Lessons`, register the lesson as its **own row** in the relevant sub-index — or, if it is cross-cutting (spans multiple families, or is shared infra/tooling/credentials), in a master-index `Cross-cutting` / pinned section. A lesson must never live *only* in `Latest Lessons`, and a `[[wiki-link]]` inside another lesson's row does **not** count as a home.
> 2. **Importance-aware truncation.** Keep `Latest Lessons` at ~20 rows, but evict by **importance then recency**, never pure FIFO: prefix each row with `[P0]`/`[P1]`/`[P2]`, and when trimming, drop the oldest **routine (`[P2]`)** row — never push out a `[P0]`/`[P1]` to make room for routine work.
> 3. **Fold homogeneous series.** A formulaic series (e.g. many near-identical `*_family_sbe_binding_facts`) gets **one umbrella row** in its sub-index, not N rows in `Latest Lessons`; cache at most the newest one and point to the sub-index for the rest.
>
> Eviction is then always **safe** (the lesson is still reachable via its sub-index home) and **importance-preserving** (a burst of routine work cannot silently flush a high-value lesson out of the cache).

---

## Phase 4: Maintain & Compress (On-demand)

When the human user issues commands like "optimize agent-context," "organize knowledge base," or `/maintain`, read `<SKILL_DIR>/docs/maintain.md` and follow its maintenance SOP. Depending on the size of the knowledge base, this phase involves operations such as merging duplicate lessons, sharpening titles, evolving the index structure, and deprecating outdated information.

---



## Skill Directory Structure

- **scripts/** - Contains ALR infrastructure scripts (e.g., `install.sh`).
- **docs/** - Contains detailed SOP guidelines for each phase (`retro.md`, `learn.md`, `maintain.md`).
- **lesson_scripts/** - (Reserved/Internal) Universal helper patterns for the router logic itself.
