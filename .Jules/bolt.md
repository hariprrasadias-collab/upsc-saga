# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Memoize inline array reductions in render loops]
**Learning:** Running expensive array operations like `.filter()` and `.reduce()` inside inline helper functions called during rendering (e.g., `getProgress(paper)` called in a loop) causes severe performance degradation as they re-evaluate on every render.
**Action:** Use `useMemo` to precalculate and cache the results of expensive computations into a lookup map (O(1) access) when the underlying data dependencies (like `analytics`) change, rather than re-computing them inline.
