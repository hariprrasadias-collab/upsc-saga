## 2024-10-28 - Hardcoded Secret Key Fallback
**Vulnerability:** A static fallback value ('dev_secret_key_upsc_saga_change_in_prod') was used for Flask's secret key if the environment variable was missing.
**Learning:** Hardcoded fallbacks undermine security by ensuring any unconfigured production environment shares the same secret key, allowing session forging and privilege escalation.
**Prevention:** Always use a randomly generated fallback (e.g., `os.urandom(24)`) for secrets if the environment variable is absent.
