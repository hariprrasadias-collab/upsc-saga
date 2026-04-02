## 2025-02-23 - Fix N+1 query in Arena Bosses endpoint
**Learning:** Found an N+1 query pattern in `backend/app/routes/arena.py` where iterating over database records triggered individual `SELECT COUNT(*)` queries inside the loop for each year/subject.
**Action:** Resolved the bottleneck by combining `COUNT(*)` with `GROUP BY` in the initial extraction query and passing the precomputed counts down to helper functions. Ensure rows are accessed safely using `try-except` blocks to support both dictionary and tuple fallback.
