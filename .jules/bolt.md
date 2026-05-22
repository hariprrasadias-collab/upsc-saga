## 2026-05-22 - Prevent N+1 queries using GROUP BY in Arena Bosses
**Learning:** In `backend/app/routes/arena.py`, `get_available_bosses` caused an N+1 query bottleneck by fetching distinct boss categories and then repeatedly calling `get_boss_stats`, which executed a `COUNT(*)` query for each category.
**Action:** Use a single `GROUP BY` query to fetch both categories and their counts simultaneously, and pass the precalculated count to the stats generator to avoid redundant database calls.
