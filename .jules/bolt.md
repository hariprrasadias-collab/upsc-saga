## 2024-05-18 - [Optimize N+1 queries in boss listings]
**Learning:** The `get_available_bosses` endpoint had an N+1 query problem, fetching the count for each year and subject individually using `SELECT COUNT(*)`.
**Action:** Used `GROUP BY` in the initial query to pre-calculate all counts at once (`SELECT year, COUNT(*) as count`), and passed them to `get_boss_stats` using an optional parameter to avoid redundant queries while reusing existing logic.
