#!/usr/bin/env bash
# install.sh — 在當前工作目錄下初始化 .agent-lessons 知識庫結構
# 用法: bash /path/to/install.sh
#   或由 Agent 在目標專案目錄中執行

set -euo pipefail

TARGET_DIR="${1:-.}"  # 預設為當前目錄，也可傳入指定路徑

LESSONS_ROOT="${TARGET_DIR}/.agent-lessons"
LESSONS_DIR="${LESSONS_ROOT}/lessons"
INDEX_FILE="${LESSONS_ROOT}/index.md"

# --- 防呆：如果已存在就跳過 ---
if [ -d "$LESSONS_ROOT" ]; then
  echo "⚠️  .agent-lessons/ 已存在於 $(cd "$TARGET_DIR" && pwd)，跳過初始化。"
  exit 0
fi

# --- 建立目錄結構 ---
mkdir -p "$LESSONS_DIR"

# --- 建立 index.md 路由表模板 ---
cat > "$INDEX_FILE" << 'EOF'
# Agent Lessons — 路由表 (Index)

> 此檔案是 Agent 記憶系統的入口。Agent 在開始任務前會搜尋此路由表，
> 找到相關的歷史經驗後再按需讀取對應的 lesson 檔案。

<!-- 格式範例：
| 檔案路徑 | 一句話描述 | Tags |
|----------|-----------|------|
| lessons/example_gotcha.md | 說明某坑的成因與解法 | db, migration |
-->

| 檔案路徑 | 一句話描述 | Tags |
|----------|-----------|------|

EOF

# --- 建立 lesson 模板檔 ---
cat > "${LESSONS_DIR}/_template.md" << 'EOF'
# [精準標題 — 一句話說明規則]

## Rule
<!-- 一句話結論，未來 Agent 可直接當指令遵守 -->

## Don't
<!-- 錯誤做法，一句話 -->

## Why（選填）
<!-- 只在原因不明顯時才寫，限 1-2 句 -->

## Refs（選填）
<!-- 相關檔案路徑或連結，純列表 -->

## Updated
<!-- YYYY-MM-DD -->
EOF

echo "✅ .agent-lessons/ 已初始化於 $(cd "$TARGET_DIR" && pwd)"
echo "   - ${INDEX_FILE}"
echo "   - ${LESSONS_DIR}/_template.md"
