#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("alr_recall", ROOT / "scripts" / "alr_recall.py")
assert SPEC and SPEC.loader
ALR_RECALL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ALR_RECALL
SPEC.loader.exec_module(ALR_RECALL)


class AlrRecallTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.bundle = Path(self.temp.name)
        (self.bundle / "lessons/workspace").mkdir(parents=True)
        (self.bundle / "lessons/_shared").mkdir(parents=True)
        (self.bundle / "lessons/workspace/msai_memup_local_memory_runtime_usage.md").write_text(
            """---
title: msai-memup local memory runtime usage
description: Store writes queue intents; drain them with a worker before recall can find them.
tags: [memup, local-memory, queue, recall]
---
# Runtime
""",
            encoding="utf-8",
        )
        (self.bundle / "lessons/_shared/site_config_unique_key.md").write_text(
            """---
title: Site config upsert needs a unique key
description: owner module section key must be UNIQUE before on duplicate key update is safe.
tags: [settings, upsert, unique]
---
# Settings
""",
            encoding="utf-8",
        )
        (self.bundle / "index_workspace.md").write_text(
            """| File | Description |
|-|-|
| `lessons/workspace/msai_memup_local_memory_runtime_usage.md` | Local memory store queues writes; worker drain makes recall visible. |
| `lessons/_shared/site_config_unique_key.md` | Setting upsert requires owner/module/section/key UNIQUE. |
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_multilingual_anchors_rank_expected_memory(self) -> None:
        result = ALR_RECALL.reduce_candidates(
            self.bundle,
            "本地記憶寫入後查不到",
            [
                "本地記憶|local memory|memory runtime",
                "寫入|store|persist",
                "查詢|recall|lookup",
                "佇列|queue|worker",
            ],
            5,
            None,
        )
        self.assertEqual(
            result["results"][0]["path"],
            "lessons/workspace/msai_memup_local_memory_runtime_usage.md",
        )
        self.assertEqual(result["results"][0]["coverage"], "4/4")

    def test_filename_and_index_coverage_rank_unique_key(self) -> None:
        result = ALR_RECALL.reduce_candidates(
            self.bundle,
            "Can setting writes rely on upsert for owner/module/section/key?",
            ["setting|config", "upsert|on duplicate key", "owner module section key", "unique key"],
            1,
            "_shared",
        )
        self.assertEqual(result["results"][0]["path"], "lessons/_shared/site_config_unique_key.md")
        self.assertEqual(len(result["results"]), 1)

    def test_rejects_generic_anchor(self) -> None:
        with self.assertRaises(ALR_RECALL.RecallUsageError):
            ALR_RECALL.reduce_candidates(
                self.bundle,
                "service error",
                ["service|system", "error|issue"],
                5,
                None,
            )

    def test_requires_bounded_anchor_count_and_limit(self) -> None:
        with self.assertRaises(ALR_RECALL.RecallUsageError):
            ALR_RECALL.reduce_candidates(self.bundle, "query", ["memory"], 5, None)
        with self.assertRaises(ALR_RECALL.RecallUsageError):
            ALR_RECALL.reduce_candidates(
                self.bundle, "query", ["memory runtime", "queue worker"], 11, None
            )

    def test_query_relation_breaks_anchor_coverage_tie(self) -> None:
        (self.bundle / "lessons/workspace/backoff_countdown.md").write_text(
            "---\ntitle: Backoff countdown\ndescription: Show resetAt and stale countdown.\n---\n",
            encoding="utf-8",
        )
        (self.bundle / "lessons/workspace/backoff_ignores_reset_at.md").write_text(
            "---\ntitle: Backoff ignores resetAt\ndescription: Fixed sleep ignores provider reset epoch and goes stale.\n---\n",
            encoding="utf-8",
        )
        (self.bundle / "index_workspace.md").write_text(
            (self.bundle / "index_workspace.md").read_text()
            + "| `lessons/workspace/backoff_countdown.md` | Backoff resetAt stale countdown. |\n"
            + "| `lessons/workspace/backoff_ignores_reset_at.md` | Backoff ignores provider resetAt and goes stale. |\n",
            encoding="utf-8",
        )
        result = ALR_RECALL.reduce_candidates(
            self.bundle,
            "Rate-limit backoff ignores the provider reset timestamp and gets stuck stale",
            ["rate limit|backoff", "provider reset|resetAt", "stale countdown|stale"],
            5,
            None,
        )
        self.assertEqual(
            result["results"][0]["path"], "lessons/workspace/backoff_ignores_reset_at.md"
        )

    def test_raw_and_concept_lanes_rescue_family_fact_from_bad_anchor_top_hit(self) -> None:
        (self.bundle / "lessons/g1").mkdir()
        (self.bundle / "lessons/q1").mkdir()
        (self.bundle / "lessons/g1/navigation_tables.md").write_text(
            """---
title: G1 navigation tables
description: G1 has distinct navigation tables; choose by category and controller.
---
# Navigation
The column navigation route is `/navigations?category=mobile` and reads `video_navigations`.
It is not the common app navigation configuration page.
""",
            encoding="utf-8",
        )
        (self.bundle / "lessons/q1/bottom_nav_permission.md").write_text(
            """---
title: Q1 bottom nav modern permission mapping
description: Q1 legacy bottom navigation has modern route and permission gaps.
---
# Bottom navigation
The Q1 bottom navigation table and shared settings page need permission fixes.
""",
            encoding="utf-8",
        )
        result = ALR_RECALL.reduce_candidates(
            self.bundle,
            "G1 legacy 欄目導航被錯接到底部共用設定頁；真正的 table、category 與 modern route 是什麼？",
            [
                "G1 legacy|legacy|欄目導航",
                "permission|table|category",
                "底部|bottom navigation|shared settings",
                "modern route|mapping",
            ],
            5,
            None,
        )
        paths = [item["path"] for item in result["results"]]
        self.assertIn("lessons/g1/navigation_tables.md", paths)
        rescued = next(
            item
            for item in result["results"]
            if item["path"] == "lessons/g1/navigation_tables.md"
        )
        self.assertIn("video_navigations", rescued["snippet"])
        self.assertIn("raw_lexical", rescued["retrieval_lanes"])
        candidates = ALR_RECALL.load_candidates(self.bundle, None)
        document_frequency = ALR_RECALL.prepare_lexical_documents(candidates)
        query_terms = ALR_RECALL.discriminative_query_terms(
            "G1 navigation",
            document_frequency,
            len(candidates),
        )
        self.assertIn("g1", query_terms)


if __name__ == "__main__":
    unittest.main()
