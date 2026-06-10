## 2024-06-10 - Mock Test Submission Bottleneck
**Learning:** Grading loops that process lists of questions can easily fall into N+1 query patterns by executing individual UPDATE statements for each answer.
**Action:** Use `executemany` with batched parameters to perform bulk updates, turning O(N) queries into O(1) batched operations.
