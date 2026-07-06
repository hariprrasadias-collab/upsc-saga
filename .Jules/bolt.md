# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized ProgressHeatmap O(N^2) data mapping]
**Learning:** In `frontend/src/components/DashboardMain/ProgressHeatmap.tsx`, grouping heatmap data into weeks used an `Array.find()` operation inside a loop iterating over 90 days. This caused an $O(N \cdot M)$ complexity scaling when resolving each date's intensity data.
**Action:** When mapping array data against a fixed sequence of iterations (like days in a calendar), first construct a lookup `Map` ($O(1)$) instead of repeatedly searching the array ($O(N)$), converting the overall complexity from quadratic-like to linear.
