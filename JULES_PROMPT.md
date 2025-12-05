# Task: Deep Optimization & Data Integrity (No New Features)

**Objective**: The user does NOT want new features. The goal is to ensure **existing features** (Sidebar, Golden Path, etc.) function to their **fullest potential** using **real data**.
**Critical Constraint**: NO MOCK DATA. NO HALLUCINATIONS. If data is missing, handle it gracefully or prompt for it, but do not fake it.

## 1. Fix Golden Path "Zero Yield" Issue (`backend/app/services/golden_path_service.py`)

**Problem**: The "Yield" (Marks) for topics in the Golden Path is currently 0 for all nodes.
**Cause**: The service joins `syllabus_topics` with `pyq_questions` on `topic` name. Exact string matching is failing (e.g., "Indus Valley" vs "Indus Valley Civilization").

**Required Fixes**:
1.  **Fuzzy Matching / Normalization**:
    *   Implement a robust matching algorithm (e.g., Levenshtein distance or simple keyword containment) to link PYQs to Syllabus Topics.
    *   *Better Approach*: Create a migration to add a `topic_id` foreign key to `pyq_questions` and backfill it, ensuring a hard link.
2.  **Fallback Logic**:
    *   If no PYQs are found for a specific sub-topic, roll up to the `Subject` level average to provide *some* estimate rather than 0.
3.  **Debug Endpoint**:
    *   Add a flag to `/api/golden-path/graph` to return "unmatched_topics" so we can see which PYQ topics aren't linking to the syllabus.

## 2. Enhance Sidebar Data Integrity (`backend/app/routes/dashboard.py`)

**Objective**: The Sidebar stats must reflect the *actual* state of the database.

1.  **Syllabus Progress**:
    *   Ensure the count reflects `syllabus_topics` where `status = 'Completed'`.
    *   *Optimization*: Cache this count calculation if it becomes slow (it shouldn't for < 1000 topics).
2.  **Active Quests**:
    *   Ensure it ONLY counts tasks where `is_quest = 1` AND `isCompleted = 0`.
    *   Verify that quests are actually being generated/stored in the DB.
3.  **Mock Tests**:
    *   Ensure `active_mocks` counts tests that the user has *started* but not *submitted* (`test_attempts` with status 'in_progress'), NOT just available tests.

## 3. "De-Mocking" Other Components

Review the following for any hardcoded/random data and replace with DB queries:
*   **Ravens (News)**: Ensure it's fetching from the NewsAPI/RSS feeds and not returning placeholder articles.
*   **Mimir (Chat)**: Ensure context injection (RAG) is actually querying the `vector_store` (ChromaDB/FAISS) and not just answering from base model knowledge.
*   **Anki Dojo**: Verify `fetch_due_cards` is communicating with the local Anki Connect instance correctly.

## 4. Frontend Optimization (`Sidebar.tsx`)

*   **Visuals**: Keep the UI changes (Badges, Progress Bar) but ensure they are driven 100% by the `sidebarStats` from `GlobalContext`.
*   **Zero State**: If a stat is 0, do not show a badge (cleaner UI).
*   **Performance**: Implement `React.memo` as planned to prevent sidebar re-renders during dashboard interactions.

## Summary of Success Criteria
1.  **Golden Path Graph**: Nodes should show non-zero Yield and Effort values based on actual PYQ and Flashcard counts.
2.  **Sidebar**: Badges should match the numbers seen in the respective "Quests" or "Mock Tests" pages.
3.  **No Hallucinations**: Every number displayed must be traceable to a database row.
