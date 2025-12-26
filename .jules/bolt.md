# Bolt's Journal

## 2024-05-22 - SQLite FTS Performance Anti-Pattern
**Learning:** The `get_questions` endpoint in `pyq.py` performs a full-text search by fetching *all* FTS row IDs in Python and injecting them back into a SQL `IN` clause. This causes massive memory overhead and slow query construction for common terms.
**Action:** Future optimization should use a direct SQL JOIN between the main table and the FTS virtual table (e.g., `JOIN pyq_questions_fts ON pyq_questions.id = pyq_questions_fts.rowid`) to let the database engine handle the intersection efficiently.
