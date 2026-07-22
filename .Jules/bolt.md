# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized flashcard stats to eliminate O(N) memory & loop bottleneck]
**Learning:** The `get_flashcard_stats` function in `backend/app/routes/flashcards.py` fetched every single flashcard (potentially thousands) from the database into a Python list just to count how many cards belong to each "maturity" level using `get_card_maturity()`. This caused an O(N) memory bottleneck and loop processing time.
**Action:** Instead of hardcoding domain logic into SQL (which violates DRY and misses required variables like `alpha` and `beta`), use SQL `GROUP BY` to group unique data permutations (e.g., `GROUP BY halflife, alpha, beta, COUNT(id)`). This reduces the Python loop from O(N total cards) to O(K unique parameter combinations) while preserving the ability to safely call the domain logic function `get_card_maturity()` on each grouped batch.
