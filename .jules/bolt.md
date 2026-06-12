## 2023-10-25 - [Setup]
**Learning:** Initializing journal for Bolt.
**Action:** Always measure before and after.
## 2025-06-12 - [Arena Boss N+1 Query]
**Learning:** `get_available_bosses` repeatedly queried counts for each year/subject inside a loop when generating boss options, causing an N+1 problem on the frontend render.
**Action:** Lift the count query out of loops by joining it as `SELECT X, COUNT(*) as count FROM pyq_questions GROUP BY X` before generating boss options.
