## $(date +%Y-%m-%d) - [Bulk Updates via GROUP BY in Weak Area Analyzer]
**Learning:** Found an N+1 query loop in `analyze_all_performance` inside `backend/app/services/weak_area_analyzer.py` where iterating over individual topics fired multiple queries per topic.
**Action:** Replaced the loop with a single bulk query using `GROUP BY topic` and updated the `weak_areas` table efficiently using `cursor.executemany` UPSERT.
