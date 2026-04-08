# Phase 4: Maintain & Compress (On-demand)

When receiving a human command such as "optimize agent-context", "organize knowledge base", or `/maintain`, please execute global or local compression and organization on the `.agent-lessons/` directory according to the SOP below. Core principle: Distill rules, reduce noise.

---

## Step 1: Evaluate Scale and Formulate Strategy

Count the number of physical files under the `lessons/` directory (excluding template files), and determine the current maintenance strategy level:

| Scale Level | File Count | Recommended Index Structure | Core Operational Requirement |
| :--- | :--- | :--- | :--- |
| Level 1 | ≤ 10 | Single flat router table | Check title precision. |
| Level 2 | 11–30 | Single segmented router table (divided by domain using `##`) | Merge duplicate items, group Index by domain. |
| Level 3 | 31–60 | Master Index + Domain Sub-indexes | Split Index files, actively merge related rules. |
| Level 4 | > 60 | Master Index + Domain Sub-indexes | Forcibly distill generalized rules, large-scale clean up of obsolete files. |

---

## Step 2: Merge & Generalize

Scan all Lesson files to find groups with highly overlapping topics or domains (e.g., multiple articles involving the same database or API gotchas).

1. **Distill, Do Not Stitch:** Extract a more generalized and precise underlying constraint rule (Rule) from N overlapping records and write a new merged file. Simply concatenating old texts end-to-end is forbidden.
2. **Delete Old Files:** Completely delete the original files that were merged.
3. **Validation Standard:** The new rule must be summarizable in a single sentence, ensuring future Agents can directly read and follow it.

---

## Step 3: Title and Filename Sharpening

Titles and filenames must be an extreme compression of the conclusion. When an Agent scans the Index, it should not need to read the file content to determine its relevance.

- [Bad] `db_issue.md` (Summary: Database has an issue)
- [Good] `sqlite_wal_must_disable_in_readonly.md` (Summary: SQLite readonly mode must disable WAL)

---

## Step 4: Index Structure Evolution

Restructure the router table based on the level from Step 1:

- **Level 2 (Segmented):** Use Markdown headers (like `## Database`, `## Auth`) within a single `index.md` to logically group the table.
- **Level 3+ (Split):** Create multi-level routing. The master `index.md` only retains domain summaries and links pointing to Sub-indexes (e.g., `[Database Lessons](index_db.md)`). The Sub-index for each domain is responsible for listing specific Lesson file paths and summaries.

---

## Step 5: Verify & Prune Obsolete Data

You must proactively verify whether the status described in each Lesson is consistent with the project's current codebase. Directly delete (or update) any Lesson that meets any of the following conditions, and synchronously remove its record from the Index:

1. The package or API relied upon by the record is no longer used in this project.
2. The conclusion has been completely covered or overturned by an updated Lesson.
3. After verification, the described issue has been thoroughly fixed or refactored in the codebase and is no longer applicable (state is untrue or obsolete).
4. The last updated date (`Updated`) is more than 6 months ago, and it has not been referenced by any recent tasks.

---

## Execution Report

After the maintenance operation is completed, output a concise maintenance summary to the human:
1. How many articles were merged, how many were deleted.
2. Whether the Index structure underwent a level change.
3. The total scale status of the current knowledge base (total file count and corresponding Level).