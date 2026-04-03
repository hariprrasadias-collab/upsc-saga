## 2024-03-24 - N+1 Queries in Boss Generation
**Learning:** The `/bosses` endpoint in `backend/app/routes/arena.py` was making iterative `SELECT COUNT(*)` lookups for every year and subject category sequentially through `get_boss_stats`.
**Action:** Used a single `GROUP BY` database query to fetch all category counts at once, and passed the results downstream via `precomputed_count` kwargs to prevent the N+1 query loop.
