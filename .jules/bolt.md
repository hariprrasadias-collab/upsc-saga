## 2024-05-24 - Frontend List Performance vs Backend Indexes

**Learning:**
I originally suspected `backend/app/routes/dashboard.py` might be missing an index on `due_date`, causing slow loads. However, checking `backend/app/db_models/indexes.py` revealed that `idx_tasks_user_due` was already implemented. This highlights the importance of checking existing optimization infrastructure before assuming negligence.

**Action:**
Always check `db_models/indexes.py` (or schema definitions) early in the profiling phase to avoid redundant optimization planning. When backend is optimized, pivot immediately to frontend rendering patterns (like large un-memoized lists) which are often overlooked in feature-heavy components like `SyllabusTracker`.
