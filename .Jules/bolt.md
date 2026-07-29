# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-22 - [Fixed N+1 queries in boss generation]
**Learning:** `get_available_bosses` in `backend/app/routes/arena.py` was fetching distinct years/subjects and then running a separate `COUNT(*)` query for each inside `get_boss_stats`.
**Action:** Replaced iterative loops over distinct items with a single bulk query using a `GROUP BY` clause, and passed the pre-calculated counts down to the helper function using an optional `precalc_count=None` parameter for backwards compatibility.

## 2024-05-22 - [Fixed strict TypeScript deployment error]
**Learning:** Deployment failures can be caused by strict TypeScript settings flagging unused variables.
**Action:** Direct implementation of the fix in the codebase (e.g. prefixing unused variables with an underscore to bypass `TS6133` error) is the best resolution path for these types of build errors during deployment.
