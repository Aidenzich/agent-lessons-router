---
name: agent-lessons-router
description: Architectural decisions and historical gotchas. Supports fast trigger via `/alr` or `alr`. Before executing any architectural changes, API integrations, or debugging tasks, you MUST retrieve the relevant context through this Skill. It also defines how to write new experiences into the local knowledge base.
tags: [workflow, architecture, knowledge-base, memory, alr]
---

# Agent-Lessons-Router (ALR)

This project adopts "Progressive Disclosure" to manage AI context. You **absolutely must NOT** guess the system architecture or past decisions out of thin air, and you **absolutely must NOT** casually add new experiences without validation.

Please strictly follow the Standard Operating Procedure (SOP) below:

---

## Terminology & Boundaries

為了避免混淆，Agent 必須區分以下兩個物理路徑：

- **PROJECT_ROOT (當前工作目錄)**：專案代碼所在的目錄。所有 **專案專屬 (Project-specific)** 的知識、Lesson、自動化腳本（`.agent-lessons/scripts/`）都必須存放在此目錄下的 `.agent-lessons/` 資料夾內。
- **SKILL_DIR (Skill 安裝目錄)**：本 Skill 邏輯所在的目錄。僅用於存放 **工具核心 (Tool-core)** 的 SOP 指引（`docs/`）、通用安裝腳本（`scripts/`）或跨專案的基礎設施邏輯。**嚴禁**將單一專案的 Lesson 或業務腳本存入此目錄。

原則：**知識隨專案走 (Local)，工具隨 Skill 走 (Global)。**

---

## Phase 0: Bootstrap

Check if the `.agent-lessons/` directory exists in the current working directory. If it **does NOT exist**, execute the installation script included in this Skill to initialize it:
 
```bash
bash <SKILL_DIR>/scripts/install.sh
```

If it already exists, skip this step and proceed directly to Phase 1.

---

## Phase 1: Recall & Retrieve (Pre-task)

Before starting to write code or debug, you must first check if there are any related historical experiences:

1. **Read the Router Table:** Start by reading `.agent-lessons/index.md` to get the big picture.
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

When the review passes, the task is fully completed, and there is a need to record the experience, read `<SKILL_DIR>/docs/learn.md` and follow its complete writing SOP. **所有新 Lesson 與專案腳本必須寫入 `PROJECT_ROOT/.agent-lessons/`。**

---

## Phase 4: Maintain & Compress (On-demand)

When the human user issues commands like "optimize agent-context," "organize knowledge base," or `/maintain`, read `<SKILL_DIR>/docs/maintain.md` and follow its maintenance SOP. Depending on the size of the knowledge base, this phase involves operations such as merging duplicate lessons, sharpening titles, evolving the index structure, and deprecating outdated information.
