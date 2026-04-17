---
name: agent-lessons-router
description: Architectural decisions and historical gotchas. Supports fast trigger via `/alr` or `alr`. Before executing any architectural changes, API integrations, or debugging tasks, OR when encountering any technical friction/failure, you MUST retrieve the relevant context through this Skill. It also defines how to write new experiences into the local knowledge base.
tags: [workflow, architecture, knowledge-base, memory, alr]
---

# Agent-Lessons-Router (ALR)

This project adopts "Progressive Disclosure" to manage AI context. You **absolutely must NOT** guess the system architecture or past decisions out of thin air, and you **absolutely must NOT** casually add new experiences without validation.

Please strictly follow the Standard Operating Procedure (SOP) below:

---

## Core Philosophy

**When in doubt, encountering a technical block, or facing an unknown project state, your first and most critical action is to consult the existing lessons (`.agent-lessons/`).** Do not rely on assumptions or general knowledge; always prioritize the project's historical records and architectural decisions preserved in the lessons. Consulting lessons is a "survival instinct," not just a pre-task step.

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

Before the implementation enters its final phase, you must read `<SKILL_DIR>/docs/review.md` and forcibly engage in self-review (or initiate a Subagent for review). This phase aims to combat "Happy Path" blind spots and ensure the modifications fully align with the user's deep intentions and the project's edge conditions. If any discrepancies are found, you must immediately rework and fix them.

---

## Phase 3: Learn & Write (Post-task)

When the review passes, the task is fully completed, and there is a need to record the experience, read `<SKILL_DIR>/docs/learn.md` and follow its complete writing SOP. **All new lessons and project-specific scripts must be written to the discovered `PROJECT_ROOT/.agent-lessons/`.**
> [!IMPORTANT]
> **Mandatory Learning**: If an iteration involved complexity, difficulty, or required non-obvious infrastructure knowledge, you **MUST** record a new lesson or update an existing one. This is not optional.

---

## Phase 4: Maintain & Compress (On-demand)

When the human user issues commands like "optimize agent-context," "organize knowledge base," or `/maintain`, read `<SKILL_DIR>/docs/maintain.md` and follow its maintenance SOP. Depending on the size of the knowledge base, this phase involves operations such as merging duplicate lessons, sharpening titles, evolving the index structure, and deprecating outdated information.

---

---
## ⚡️ The Keep-Alive Super-power (High Autonomy Mode)

When the mission demands deep execution without friction, the user may invoke the **Keep-Alive Protocol**. This shifts the Agent's baseline from "Reactive" to "Proactive First-Principle Reasoning."
- **Trigger**: User commands like "Keep-alive," "Zero-interruption," or marking the Plan's autonomy as "High."
- **Execution Strategy**: MUST Read `<SKILL_DIR>/docs/keep-me-alive.md` and adhere to its core tenets when triggered.

---

## Skill Directory Structure

- **scripts/** - Contains ALR infrastructure scripts (e.g., `install.sh`).
- **docs/** - Contains detailed SOP guidelines for each phase (`review.md`, `learn.md`, `maintain.md`).
- **lesson_scripts/** - (Reserved/Internal) Universal helper patterns for the router logic itself.
