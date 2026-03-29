## 2024-03-28 - [Critical IDOR Fix in PYQ Quiz Routes]
**Vulnerability:** Insecure Direct Object Reference (IDOR) where queries filtered sessions and quizzes based on a hardcoded `user_id = 1` rather than determining the specific current user. This would allow access to and modification of data belonging to other users.
**Learning:** Security depends on properly passing user identification from session contexts into database operations rather than hardcoding static mock identifiers during development.
**Prevention:** Consistently use session utility functions (like `get_current_user_id()`) combined with parameterized DB queries `?` to restrict scope to the current session user.
