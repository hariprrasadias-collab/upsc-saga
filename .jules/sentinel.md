# Sentinel's Journal

## 2025-02-18 - IP Detection Behind Proxies
**Vulnerability:** Blindly trusting the first IP in `X-Forwarded-For` header allows attackers to spoof their IP by appending their own header.
**Learning:** Manual parsing of `X-Forwarded-For` is error-prone. Render and other cloud providers append the real IP to the end of the list, but standard practice varies.
**Prevention:** Use `werkzeug.middleware.proxy_fix.ProxyFix` middleware to correctly handle proxy headers and trust `request.remote_addr` in the application code. This delegates trust configuration to the middleware layer.
