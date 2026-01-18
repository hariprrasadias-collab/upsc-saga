## 2026-01-18 - Sequential Analytics Queries
**Learning:** The `/api/pyq/analytics` endpoint executes 4 sequential SQL queries to aggregate data by subject, year, topic, and difficulty. While SQLite is fast, this pattern scales poorly and repeats the same calculations for every user request.
**Action:** Use `Flask-Caching` with `query_string=True` to cache these read-heavy, low-volatility endpoints. This reduced response time by ~50% and eliminated DB load for repeated requests.
