## 2024-05-22 - [Database Tracking Issue]
**Learning:** The repository tracks the binary SQLite database file (`backend/upsc_saga.db`) and its WAL/SHM files. This causes issues with automated tests modifying the file and potentially corrupting the tracked version or creating large diffs.
**Action:** When working on backend tests, always use an in-memory database (`:memory:`) or a temporary file, and be extremely careful not to stage changes to the tracked database files. Ideally, these files should be removed from git tracking in a separate cleanup task.
