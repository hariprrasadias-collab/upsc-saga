# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized arena boss stats generation to eliminate N+1 queries]
**Learning:** The `get_available_bosses` endpoint generated statistics for all bosses (Years and Subjects) by iterating over unique attributes and making a `SELECT COUNT(*)` query for *every* individual boss. This caused (N)$ extra database queries.
**Action:** Replaced iterative distinct attribute counting with batched `SELECT ..., COUNT(*) ... GROUP BY ...` operations to transform (N)$ queries into an (1)$ constant time lookup. Added a `precomputed_count` parameter to the stats generating function to bypass individual database fetches when counts are known.
