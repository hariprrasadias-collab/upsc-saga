# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-31 - Executemany parameters must mirror original source strictly
**Learning:** When refactoring iterative INSERTs into `executemany` batches, do not blindly assume the table schema constraints dictate the number of parameters required. Existing code might only insert a subset of the table columns. Trying to pad the parameter list to match the full schema (e.g. adding 3 extra hallucinated columns) breaks functionality and violates the "preserve existing functionality exactly" boundary.
**Action:** Always read the exact `VALUES` clause of the original iterative query, and ensure the batched `params` list maps to those exact columns, nothing more.
