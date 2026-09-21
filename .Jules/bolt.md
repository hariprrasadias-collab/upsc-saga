# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).


## 2024-05-23 - [Optimize React array computations with useMemo]
**Learning:** Recomputing derived state inline using `.filter().reduce()` in React components causes performance degradation when components render lists of items or repeatedly evaluate the same calculations. This codebase's React patterns often loop over full arrays rather than transforming them to O(1) lookups.
**Action:** When optimizing expensive inline array operations, always extract them into a single `useMemo` block that generates an O(1) dictionary lookup map (e.g., `Record<string, number>`) or precomputes all needed values once.
