## 2024-04-03 - [Fix N+1 queries in arena bosses route]
**Learning:** Generating the list of arena bosses iteratively queried the database for each boss to count questions, causing an N+1 performance bottleneck.
**Action:** Replace iterative SELECT COUNT statements with single bulk queries using GROUP BY. For reusable stat generation functions, pass pre-computed values (e.g., `pre_count`, `pre_row`) to bypass redundant database lookups.
