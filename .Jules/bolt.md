# Bolt's Journal

## 2024-05-31 - N+1 Query in consult_the_seer and loops in get_year_trends
**Learning:** Found N+1 query issue in backend/app/routes/seer.py for consult_the_seer (looping over dates) and get_year_trends (nested loops querying per year).
**Action:** Always check loop conditions making SQL queries in routes. Consolidate into single aggregated queries instead of multiple iterative fetches.
