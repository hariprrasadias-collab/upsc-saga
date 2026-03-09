# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-09 - [SQLite Aggregation over Python Loop in Flashcard Context]
**Learning:** In the `get_brain_context` logic of `FlashcardService`, pulling all flashcard reviews and iterating through them with `datetime.fromisoformat` and Python conditionals was causing an unnecessary O(N) memory and processing overhead. Running `fetchall()` and processing thousands of records via Python was slower than offloading data aggregation and condition checks directly to the SQLite query engine. Using SQL aggregate functions like `COALESCE(SUM(CASE WHEN ...))` paired with a Common Table Expression (`WITH`) is 3-4x faster for larger datasets.
**Action:** In SQLite-backed backend services, push data aggregation and `COUNT`/`SUM` logic directly into the database query rather than iterating over result sets in Python memory. This approach conforms to the overarching memory guideline: "For performance, push data aggregation (e.g., UNION, COUNT(DISTINCT)) directly to SQLite queries instead of fetching datasets into Python memory."
