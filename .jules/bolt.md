## 2026-05-27 - Analytics N+1 queries optimization
**Learning:** The /api/analytics/subject-wise endpoint performed N*3 database queries in a loop. By grouping these into three batched GROUP BY IN clause queries in get_all_subjects_performance we resolve the N+1 bottleneck.
**Action:** Always batch related multi-subject or multi-item queries using GROUP BY instead of looping inside an endpoint.
