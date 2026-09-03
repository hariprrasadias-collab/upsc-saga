# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-06-15 - [Optimize static objects in React components]
**Learning:** In React, large static objects defined inside the component module scope are reallocated on every render, adding unnecessary overhead.
**Action:** When identifying large, static configuration objects or dictionaries (e.g., navigation menus, stylistic matrixes) in React components, hoist them completely outside the component scope to prevent reallocation. This is cleaner and more performant than wrapping them in `useMemo`, which introduces its own hook overhead.
