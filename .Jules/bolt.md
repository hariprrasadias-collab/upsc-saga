# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-06-28 - Optimizing React Re-Renders with useMemo in KnowledgeGraph

**Learning:** Array manipulation methods like `.map()` and `new Set()` create new object references. If performed during every render cycle (e.g., in a component body like `KnowledgeGraph` without memoization), they cause unnecessary garbage collection overhead and can trigger wasteful re-renders in child components that rely on referential equality, even when the underlying data (`graphData`) hasn't changed.
**Action:** Always wrap expensive, purely functional derivations of state or props (especially those involving creating new Maps, Sets, or Arrays) with `useMemo` when they are inside the render path, ensuring the correct dependency array is provided.
