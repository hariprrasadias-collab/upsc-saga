# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized Analytics Service unique dates extraction]
**Learning:** `calculate_study_hours` and `get_streak_days` previously made separate `SELECT` queries across 5 tables to fetch all activity timestamps into Python memory, converted them, and then added them to a set to determine unique active days. This memory-intensive pattern scaled poorly and was extremely slow. By using a single `SELECT COUNT(DISTINCT DATE(...))` with a `UNION ALL` (or a `UNION` for date extraction) block directly in SQLite, performance improved by ~2.3-3x.
**Action:** Always push data aggregation, like finding distinct dates or summing rows across multiple tables, down to SQLite using `UNION` or `UNION ALL` instead of pulling raw rows into Python sets and lists.
