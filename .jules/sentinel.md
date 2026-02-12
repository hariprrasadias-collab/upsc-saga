## 2024-03-22 - [Path Traversal in Autonomy Evolution]
**Vulnerability:** The `trigger_evolution` endpoint in `autonomy_routes.py` was vulnerable to path traversal because it relied on `os.path.join(os.getcwd(), target_file)` without checking if `target_file` was an absolute path or resided within the project root.
**Learning:** `os.path.join` ignores the base path if the second argument is an absolute path (e.g., `/etc/passwd`). Checking for `..` is insufficient. `startswith` is also risky if trailing slashes are omitted (e.g. `/app` vs `/apple`).
**Prevention:** Always resolve paths to absolute paths using `os.path.abspath` and verify containment using `os.path.commonpath([root, target]) == root`. This handles directory boundaries correctly.
