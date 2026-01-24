# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-05-23 - Analytics Logic Loop
**Learning:** Logic loops in Python that query the database inside the loop (N+1) can be silent performance killers, even if the individual query is fast. Hoisting queries outside the loop is a fundamental optimization.
**Action:** When seeing a loop constructing a time-series response, always check if the data being fetched inside the loop actually depends on the loop variable.
