# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-04-15 - [Eliminated N+1 query bottleneck in `/bosses` endpoint]
**Learning:** The `/bosses` endpoint iteratively ran `SELECT COUNT(*)` for every distinct year and subject, causing severe N+1 overhead as the number of distinct years/subjects grew. Grouping database aggregations (`SELECT ..., COUNT(*) ... GROUP BY ...`) entirely side-steps this issue by doing the heavy lifting in SQL.
**Action:** Whenever iteratively computing counts over distinct values, use SQL's `GROUP BY` to bulk-fetch the counts beforehand, and refactor underlying helper functions to optionally accept precomputed values.
