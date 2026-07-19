## 2024-07-19 - N+1 Query Optimization with Fault Tolerance
**Learning:** Replacing loop-based iterative database queries with bulk `GROUP BY` operations across multiple tables (e.g., `mock_tests`, `answer_questions`, `syllabus_topics`) significantly reduces database roundtrips. However, missing tables (like `answer_questions` in test environments) can cause the entire batch operation to fail.
**Action:** Always wrap bulk database aggregations across different tables in isolated `try...except` blocks to prevent independent table failures from halting the entire endpoint.
