## 2024-06-05 - Optimize flashcard review subquery
**Learning:** Correlated subqueries (`LEFT JOIN review_sessions rs ON rs.id = (SELECT id FROM review_sessions WHERE flashcard_id = f.id ORDER BY reviewed_at DESC LIMIT 1)`) can dramatically outperform nested `IN` + `MAX` + `GROUP BY` patterns for fetching latest child records in SQLite, especially when proper indexes exist.
**Action:** Default to correlated subqueries for fetching latest associations in SQLite instead of bulk grouping.
