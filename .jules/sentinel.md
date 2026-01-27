## 2025-01-26 - Exposed Google OAuth Credentials
**Vulnerability:** Real Google OAuth credentials (`backend/credentials.json`) and session tokens (`backend/token.json`) were committed to the git repository.
**Learning:** Adding files to `.gitignore` does not remove them from the repository if they were previously tracked. The files remained in history and in the current HEAD despite the ignore rule.
**Prevention:** Always verify `git ls-files` after updating `.gitignore`. Use `git rm --cached` to stop tracking files that were accidentally committed.
