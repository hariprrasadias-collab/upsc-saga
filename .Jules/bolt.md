# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2026-02-20 - Analytics Loop Inefficiency
**Learning:** Analytics endpoints that iterate over date ranges often recalculate state-invariant metrics (like current syllabus completion) inside the loop, causing N+1 query performance issues.
**Action:** Lift state-invariant queries outside of loops to calculate once and reuse the value.
