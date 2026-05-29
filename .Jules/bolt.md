# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## $(date +%Y-%m-%d) - [Optimized flashcard subqueries with bare columns]
**Learning:** SQLite correlated subqueries using \`IN\` with \`MAX()\` (e.g., \`WHERE (id, date) IN (SELECT id, MAX(date) GROUP BY id)\`) behave catastrophically if the grouping table contains multiple identical max values (exact same timestamp), resulting in a Cartesian-like multiplication of returned rows. This balloons row counts (e.g. 1123 instead of 603) and significantly degrades query performance.
**Action:** Replace these correlated \`IN\` subqueries with SQLite's bare column grouped queries (e.g., \`SELECT id, val1, MAX(date) GROUP BY id\`). Because SQLite guarantees that unaggregated columns in a grouped query are drawn from the exact same row as the \`MAX()\` result, it enforces a strict 1-to-1 return, eliminating duplication and slashing query times by 60-70%. Always pair this with a covering composite index \`(foreign_key, date DESC)\`.

## $(date +%Y-%m-%d) - [Fixed CSS Syntax Error Causing Build Failures]
**Learning:** Nested CSS selectors or missing closing braces inside media queries/nested classes can be silently ignored or only trigger warnings in development mode. However, during production builds (`esbuild css minify` via Vite/Rollup), these syntax errors (like `Unexpected "}"`) become fatal and cause the entire build process to crash with `exit code 1` or `2`.
**Action:** Always ensure CSS rules are properly scoped and braces match, especially when using standard CSS rather than SCSS/SASS preprocessors. Remove orphaned braces or nested rules that break standard CSS syntax parsing.
