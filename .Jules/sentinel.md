## 2024-06-14 - Fix Hardcoded Google Calendar Secrets
**Vulnerability:** Hardcoded Google Calendar secrets (`credentials.json` and `token.json`) were committed to the repository and accessed via the filesystem in `backend/app/routes/warmap.py`.
**Learning:** These files contain sensitive `client_secret` and `refresh_token` information that could allow unauthorized access to the configured Google Calendar integration if exposed.
**Prevention:** Ensure `.gitignore` properly ignores these files and modify the application code to load sensitive configurations from environment variables (`GOOGLE_CREDENTIALS_JSON` and `GOOGLE_TOKEN_JSON`) instead of the filesystem.
