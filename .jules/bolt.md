## 2024-05-18 - Batch Database Insertion in loops
**Learning:** Python loops executing individual SQL `INSERT` statements using `conn.execute()` can cause severe I/O bottlenecks and context switching overhead in SQLite, resulting in an N+1 performance anti-pattern.
**Action:** When inserting multiple rows derived from collections (like an array of questions or answers), map the data to a list of tuples and use `conn.executemany()` to batch the inserts into a single operation.
