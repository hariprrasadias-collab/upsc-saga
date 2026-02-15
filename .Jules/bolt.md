# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2024-05-23 - N+1 Query in Time Series Data
**Learning:** Loops that generate time-series data often contain N+1 query patterns where the query itself is loop-invariant (doesn't use the loop variable).
**Action:** Check if the query inside the loop depends on the loop variable. If not, hoist it outside.
