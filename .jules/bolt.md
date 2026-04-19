## 2026-04-19 - Prevented N+1 Query in Analytics Service
**Learning:** The `identify_weak_areas` function in `backend/app/services/analytics_service.py` was making N+1 queries by fetching historical mock scores for multiple subjects inside a loop.
**Action:** Prevented N+1 query bottlenecks by fetching historical mock scores for multiple subjects using a single `IN (...)` query and grouping them in-memory with `collections.defaultdict`.
