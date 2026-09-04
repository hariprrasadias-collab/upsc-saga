# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2023-10-27 - Exception Handling Anti-Patterns
**Learning:** Silently swallowing errors with `except Exception: pass` during refactoring is flagged as a bug by code review.
**Action:** Always explicitly log exceptions (`print(f"Error: {e}")`) when replacing bare except blocks.

## 2023-10-27 - Database Schema Verification
**Learning:** `syllabus_topics` doesn't have a `user_id` column, so filtering by it causes errors. Also, `pyq_attempted` and `flashcard_mastered` were returned as 0 by the original query because they weren't implemented yet; removing them breaks dictionary parity.
**Action:** Before optimizing queries, explicitly verify schemas (`PRAGMA table_info`). Ensure all keys from the original unoptimized dictionary are preserved in the optimized result.
