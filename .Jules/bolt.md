# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-02-28 - Optimize syllabus historical data fetching
**Learning:** The `syllabus_topics` table only stores the current status of topics without historical records, which results in the `syllabus` analytics metric showing a constant value across historical dates. Querying it inside a per-day loop leads to O(N) redundant queries.
**Action:** When working with tables lacking historical tracking (like `syllabus_topics`), execute aggregate/count queries once outside the date loop to prevent N+1-like redundant queries when building time-series trend data.
