# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-09-02 - [Avoid micro-optimizations without measurable impact]
**Learning:** Hoisting a static configuration object outside a React component to prevent reallocation on every render is a common React best practice, but it is a micro-optimization with virtually zero measurable impact on performance unless the object is massive or explicitly breaks memoization downstream.
**Action:** Do not classify standard React structural cleanups (like hoisting static dictionaries) as performance optimizations. Wait to identify optimizations that have a provable, measurable impact on application load times, memory utilization, or request counts.
