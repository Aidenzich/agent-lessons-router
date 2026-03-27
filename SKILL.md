---
name: agent-lessons-router
description: 專案的架構決策與歷史踩坑紀錄（Gotchas）。在執行任何架構修改、API 串接或 Debug 任務前，必須先透過此 Skill 檢索相關上下文。同時規範了如何將新經驗寫入本地知識庫。
tags: [workflow, architecture, knowledge-base, memory]
---

# Agent-Lessons-Router

本專案採用「漸進式揭露 (Progressive Disclosure)」來管理 AI 上下文。你**絕對不能**憑空猜測系統架構或過去的決策，也**絕對不能**在未經驗證的情況下隨意新增經驗。

請嚴格遵守以下標準作業流程 (SOP)：

---

## Phase 0: 初始化 (Bootstrap)

確認當前工作目錄下是否存在 `.agent-lessons/` 資料夾。如果**不存在**，執行本 Skill 內附的安裝腳本進行初始化：
 
```bash
bash <SKILL_DIR>/scripts/install.sh
```

如果已存在則跳過，直接進入 Phase 1。

---

## Phase 1: 讀取與檢索 (Recall / Pre-task)

在開始編寫程式碼或進行 Debug 之前，你必須先尋找是否已有相關的歷史經驗：

1. **讀取路由表：** 靜默讀取 `.agent-lessons/index.md`。
2. **關鍵字比對：** 根據你當前的任務目標（例如：處理資料庫、修改金流、認證機制），在 `index.md` 中尋找對應的 Tags 或檔案路徑。
3. **按需讀取 (Progressive Disclosure)：** 如果找到高度相關的實體檔案（例如 `lessons/db_sqlite.md`），請明確讀取該檔案的完整內容，並將其視為**最高優先級的架構約束**。
4. **無紀錄則略過：** 如果 `index.md` 中沒有相關紀錄，代表這是一個新領域，你可以基於現有程式碼結構直接開始工作。**不要**去讀取無關的經驗檔以免污染你的 Context。 
5. **依序 fallback 到：** 
   - 最近的 agent-facing project
   - guidance repo-local skills / tool config 
   - source structure


---

## Phase 2: 寫入與學習 (Learn / Post-task)

當任務結束且需要記錄經驗時，讀取 `<SKILL_DIR>/docs/learn.md` 並遵循其中的完整寫入 SOP。

---

## Phase 3: 維護與壓縮 (Maintain / On-demand)

當人類下達「優化 agent-context」、「整理知識庫」或 `/maintain` 指令時，讀取 `<SKILL_DIR>/docs/maintain.md` 並遵循其中的維護 SOP。此階段會根據知識庫規模，執行合併重複 lesson、銳化標題、演進 index 結構、淘汰過時資訊等操作。