## 2024-05-23 - Shadowed Auth Function IDOR
**Vulnerability:** A local `get_current_user_id()` function redefined inside `backend/app/routes/challenges.py` shadowed the proper authentication utility from `app.utils.session`, defaulting to `user_id = 1` and causing an IDOR vulnerability.
**Learning:** Hardcoding or locally redefining authentication utilities can bypass security checks designed into the proper session module.
**Prevention:** Always rely on centralized, secure authentication utilities and ensure they are not shadowed or overridden by local functions within individual route files.
