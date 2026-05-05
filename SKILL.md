---
name: agent-lessons-router
description: |
  CRITICAL DIRECTIVE: Knowledge Persistence & Routing & Memory Management
  Always prioritize writing project experiences, environment variables configs like git token , PR, operational rules, and known pitfalls (gotchas) to the .agent-lessons/ directory as physical files. Do NOT rely solely on your internal memory.

  You must understand that ALR (Agent Lessons Router) lessons SUPERSEDE your internal memory. ALR serves as the authoritative, project-level knowledge base. Because ALR lessons are shared across all agents and utilize deterministic index routing, they are structurally stronger, permanent, and vastly superior to ephemeral memory for enforcing system architecture and preventing regressions.

tags: [workflow, architecture, knowledge-base, memory, alr, ddd, debugging, SOP, parity]

---

# Agent-Lessons-Router (ALR)

This project adopts "Progressive Disclosure" to manage AI context. You **absolutely must NOT** guess the system architecture or past decisions out of thin air, and you **absolutely must NOT** casually add new experiences without validation.

Please strictly follow the Standard Operating Procedure (SOP) below:

---

## Core Philosophy

**When in doubt, encountering a technical block, or facing an unknown project state, your first and most critical action is to consult the existing lessons (`.agent-lessons/`).** Do not rely on assumptions or general knowledge; always prioritize the project's historical records and architectural decisions preserved in the lessons. Consulting lessons is a "survival instinct," not just a pre-task step.

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

---

## Phase 1: Recall & Retrieve (Pre-task & Troubleshooting)

Before starting to write code or debug, **and immediately upon any command failure or technical block**, you must check if there are any related historical experiences in the **discovered `PROJECT_ROOT`**:

1. **Read the Router Table:** Start by reading `PROJECT_ROOT/.agent-lessons/index.md` to get the big picture.
2. **Domain-Specific Indexes:** Pay attention to any `index_*.md` files (e.g., `index_g1.md`, `index_workspace.md`). These sub-indexes contain highly dense, domain-specific experiences.
3. **Keyword & Topic Matching:** Based on your current task (e.g., Trello/Gitea integration, G1 parity), identify and read the `index_*.md` file that is **closest to your objective**.
4. **On-Demand Reading (Progressive Disclosure):** From the chosen index, explicitly read the full content of relevant lesson files. Treat them as the highest priority architectural constraints.
5. **Skip if No Records:** If no relevant records exist across all indexes, it is unexplored territory. Do not read irrelevant files.
5. **Fallback Sequentially To:** 
   - The most recent agent-facing project
   - Guidance repo-local skills / tool config
   - Source structure

---

## Phase 2: Review & Retrospection (Post-execution)

Before the implementation enters its final phase, you must read `<SKILL_DIR>/docs/retro.md` and forcibly engage in self-review (or initiate a Subagent for review). This phase aims to combat "Happy Path" blind spots and ensure the modifications fully align with the user's deep intentions and the project's edge conditions. If any discrepancies are found, you must immediately rework and fix them.

---

## Phase 3: Learn & Write (Post-task)

When the review passes, the task is fully completed, and there is a need to record the experience, read `<SKILL_DIR>/docs/learn.md` and follow its complete writing SOP. **All new lessons and project-specific scripts must be written to the discovered `PROJECT_ROOT/.agent-lessons/`.**

> [!IMPORTANT]
> **Mandatory Learning & L1 Cache Rule**: If an iteration involved complexity, difficulty, or required non-obvious infrastructure knowledge, you **MUST** record a new lesson or update an existing one. When adding a new lesson to the master index (`index.md`), you must append it to the `Latest Lessons` table but **strictly truncate the table to the 20 most recent entries**. This acts as an L1 Cache mimicking a "newer memory is more important" model, preventing index bloat while older lessons safely reside in their domain-specific sub-indexes.

---

## Phase 4: Maintain & Compress (On-demand)

When the human user issues commands like "optimize agent-context," "organize knowledge base," or `/maintain`, read `<SKILL_DIR>/docs/maintain.md` and follow its maintenance SOP. Depending on the size of the knowledge base, this phase involves operations such as merging duplicate lessons, sharpening titles, evolving the index structure, and deprecating outdated information.

---



## Skill Directory Structure

- **scripts/** - Contains ALR infrastructure scripts (e.g., `install.sh`).
- **docs/** - Contains detailed SOP guidelines for each phase (`retro.md`, `learn.md`, `maintain.md`).
- **lesson_scripts/** - (Reserved/Internal) Universal helper patterns for the router logic itself.
