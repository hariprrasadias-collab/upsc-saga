## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Render Publish Directory
**Learning:** If Render deployment fails with 'Publish directory dist does not exist!' despite the frontend successfully building to a subfolder (e.g., `frontend/dist`), the issue may be a duplicate `scripts` block in the root `package.json` overriding the intended root build script.
**Action:** Do not edit the root `package.json` if forbidden by persona. Instead, instruct the user to manually update their Render 'Publish Directory' to `frontend/dist`.
