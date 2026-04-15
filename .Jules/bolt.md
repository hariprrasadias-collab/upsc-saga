# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-04-15 - Batch database inserts using executemany
**Learning:** When creating large datasets via an API endpoint (e.g., creating a mock test with multiple questions), iterative DB `INSERT` queries within a for-loop create a significant bottleneck (O(n) DB overhead).
**Action:** Consolidate multiple individual queries into a single parameterized batch operation using `conn.executemany(...)` by pre-formatting the data into a list of tuples, turning O(n) insertions into a much more performant single batch transaction.

## 2025-04-15 - Unused Variables breaking Production Builds
**Learning:** In strict TypeScript configurations (like Vite React templates), an unused variable (TS6133) will completely halt the build phase during `tsc -b`.
**Action:** When working on unused variable errors, especially in shared components, prefixing the variable with an underscore (e.g. `_isUpscale`) safely satisfies strict TypeScript checks without having to refactor consuming interfaces or run the risk of breaking runtime logic.
