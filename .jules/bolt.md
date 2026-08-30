## 2026-08-30 - N+1 Query in seer.py
**Learning:** The previous implementation queried the database for subject counts in a loop (one query per year), leading to unnecessary DB overhead.
**Action:** Use a single GROUP BY query instead of looping.
