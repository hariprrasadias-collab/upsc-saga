## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## $(date +%Y-%m-%d) - SQL Injection via f-strings in SQLite
**Vulnerability:** The analytics endpoint dynamically built queries using `f-strings` inserting uncontrolled user input or pre-processed logic segments into SQL command text.
**Learning:** Python `f-strings` in query execution (e.g., `conn.execute(f"SELECT ... {filters_sql}")`) inherently bypass parameterized boundaries and represent critical SQL injection risks, especially when `filters_sql` stems from user input parameters.
**Prevention:** Always use static strings combined with `sqlite3` parameters (e.g., `?` syntax) for dynamic values. When concatenating clause logic like `WHERE` or `GROUP BY` dynamically, assemble the string directly using standard concatenation and enforce the database adapter binding for all user data elements.
