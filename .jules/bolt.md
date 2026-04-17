## 2024-05-24 - Batching Database Operations to Prevent N+1 Queries
**Learning:** Found N+1 query loops in `submit_attempt` (updating answers) and `create_test` (inserting questions) within `mock_tests.py` which execute single database operations for every item sequentially, creating severe performance bottlenecks.
**Action:** Use `conn.executemany()` to perform batch `INSERT` and `UPDATE` operations, significantly reducing database roundtrips and drastically improving endpoint response times for large tests.
