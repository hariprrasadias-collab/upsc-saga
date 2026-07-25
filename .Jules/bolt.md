# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-07-25 - SQL GROUP BY for complex data categorizations
**Learning:** When categorizing large sets of data based on complex domain-specific Python functions (like Ebisu calculations requiring `alpha`, `beta`, `halflife`), we can't easily reinvent the function logic in SQL. Instead, we can use a SQL `GROUP BY` clause on the required function parameters to minimize the dataset size (eliminating redundant rows with the same parameters) before iterating over the grouped results in Python and aggregating their counts.
**Action:** Replace `SELECT ...` + iteration with `SELECT ..., COUNT() ... GROUP BY ...` + iteration when aggregating data that relies on Python-level categorizations, ensuring O(N) memory bottlenecks are avoided without logic regressions.
