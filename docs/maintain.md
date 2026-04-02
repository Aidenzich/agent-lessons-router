# Phase 3: 維護與壓縮 (Maintain / On-demand)

當收到人類指令「優化 agent-context」、「整理知識庫」或 `/maintain` 時，請依據下方 SOP 對 `.agent-lessons/` 目錄執行全域或局部的壓縮與整理。核心原則：提煉規則、降低雜訊。

---

## Step 1: 評估規模與制定策略

統計 `lessons/` 目錄下的實體檔案數量（排除模板檔），決定當前維護策略別：

| 數量級別 | 檔案數 | 建議 Index 結構 | 核心操作要求 |
| :--- | :--- | :--- | :--- |
| Level 1 | ≤ 10 | 單一平面路由表 | 檢查標題精準度。 |
| Level 2 | 11–30 | 單一分段路由表 (依領域劃分 `##`) | 合併重複項目，按領域分群 Index。 |
| Level 3 | 31–60 | 總 Index + 領域 Sub-index | 拆分 Index 檔案，積極合併關聯規則。 |
| Level 4 | > 60 | 總 Index + 領域 Sub-index | 強制提煉泛化規則，大範圍清理過期檔案。 |

---

## Step 2: 萃取與合併 (Merge & Generalize)

掃描所有 Lesson 檔案，找出主題或領域高度重疊的群組（例如多篇皆涉及同一資料庫或 API 坑點）。

1. **提煉而非拼接：** 從 N 篇重疊紀錄中，萃取出一條更泛化、精準的底層約束規則 (Rule)，寫入一篇新的合併檔。禁止單純將舊文字首尾相連。
2. **刪除舊檔：** 徹底刪除被合併的原始檔案。
3. **驗證標準：** 新規則必須能用一句話總結，確保未來的 Agent 能直接讀懂並遵守。

---

## Step 3: 標題與檔名銳化 (Sharpening)

標題與檔名必須是結論的極致壓縮。Agent 掃描 Index 時，不應需要讀取檔案內容才能判斷其關聯性。

- [Bad] `db_issue.md` (摘要：資料庫有個問題)
- [Good] `sqlite_wal_must_disable_in_readonly.md` (摘要：SQLite 唯讀模式必須關閉 WAL)

---

## Step 4: 演進 Index 結構 (Structure Evolution)

依據 Step 1 的級別重構路由表：

- **Level 2 (分段)：** 在單一 `index.md` 內使用 Markdown 標題（如 `## Database`, `## Auth`）將表格邏輯分群。
- **Level 3+ (拆分)：** 建立多層級路由。總 `index.md` 僅保留領域摘要與指向 Sub-index 的連結（如 `[Database Lessons](index_db.md)`），由各領域的 Sub-index 負責條列具體的 Lesson 檔案路徑與摘要。

---

## Step 5: 核實與淘汰過期資訊 (Verify & Prune Obsolete Data)

必須主動核實各 Lesson 描述的狀態是否與專案當前的程式碼一致。直接刪除（或更新）符合以下任一條件的 Lesson，並同步移除其在 Index 中的紀錄：

1. 該紀錄依賴的套件或 API 已不在本專案中使用。
2. 該結論已被更新的 Lesson 完全涵蓋或推翻。
3. 經核實確認所描述的問題已在 codebase 中被徹底修復或重構，不再適用（狀態不屬實或已過期）。
4. 最後更新日 (`Updated`) 超過 6 個月，且未被近期的任何任務引用過。

---

## 執行回報 (Report)

維護作業結束後，向人類輸出簡潔的維護摘要：
1. 合併了幾篇、刪除了幾篇。
2. Index 結構是否發生級別變更。
3. 當前知識庫的總規模狀態 (總檔案數與對應的 Level)。