## 2024-06-01 - Optimizing Bulk Inserts in Python
**Learning:** Using individual `INSERT` queries within a loop for bulk data creation (e.g., test questions) creates a significant N+1 query bottleneck.
**Action:** Always prepare an array of tuples and use `executemany` for bulk database insertions to minimize database roundtrips.
