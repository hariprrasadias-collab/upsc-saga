## 2026-01-31 - Syllabus Payload Optimization
**Learning:** Fetching potentially large text columns (e.g., `notes`) in list views (N items) scales poorly. Even if empty initially, future data growth will degrade performance.
**Action:** Always project specific columns in SQL queries (`SELECT col1, col2` instead of `SELECT *`). For large text fields, return a boolean flag (e.g., `has_notes`) and implement an on-demand fetch endpoint for the full content.
