
## 2025-06-08 - SQLite Batch Inserts Optimization
**Learning:** In Flask/SQLite applications, looping over items to run individual `conn.execute('INSERT ...')` statements causes an N+1 query performance bottleneck during bulk creations.
**Action:** Always prefer compiling parameters into a list of tuples and using `conn.executemany()` to batch inserts. This transforms O(N) queries into O(1) batched query.
