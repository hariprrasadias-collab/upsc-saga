## 2024-05-22 - SQLite Subquery Performance Trap
**Learning:** SQLite's query optimizer can degrade catastrophically (28s vs 0.1s) when using `WHERE (col1, col2) IN (SELECT ...)` subqueries combined with partial or non-covering indexes.
**Action:** Always prefer Window Functions (`ROW_NUMBER()`) or CTEs over correlated subqueries for "latest record" lookups in SQLite to ensure stable execution plans.
