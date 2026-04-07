# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-23 - Replaced XP history and year-trends N+1 loops with single GROUP BY queries
**Learning:** In `backend/app/routes/seer.py`, fetching historical XP or trends with an iterative approach inside a loop created arbitrary N+1 database queries.
**Action:** When extracting grouped or time-series data, fetch the data with a single `GROUP BY` query and load the results into a Python dictionary (`collections.defaultdict` or standard map) to achieve O(1) in-memory lookups instead of repeated database calls. Ensure defensive exception handling (`try: val = row['key'] except (TypeError, IndexError): val = row[i]`) when mapping rows, as SQLite cursors may dynamically return `sqlite3.Row` dictionaries or standard tuples.
