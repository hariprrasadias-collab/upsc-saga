# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-11-20 - N+1 Query Fix Requires Caution with Local State
**Learning:** Fixing database bottlenecks often requires writing local test scripts that interact with the SQLite DB. Doing so modifies the binary `.db` file, which automated git tracking will stage. Submitting a patch with a polluted binary file violates code review principles and risks production database corruption.
**Action:** Always run `git checkout -- <db_file>` and ensure the `upsc_saga.db` file is excluded from commits whenever writing and executing benchmark or performance testing scripts.
