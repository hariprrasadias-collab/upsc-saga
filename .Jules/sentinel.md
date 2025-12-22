## 2024-05-23 - SSRF Vulnerability in Article Fetcher
**Vulnerability:** The `fetch_article_content` function in `upsc_summarizer.py` was blindly accepting user-provided URLs and making server-side HTTP requests using `requests.get()`. This allowed potential Server-Side Request Forgery (SSRF) attacks where an attacker could probe internal network services (localhost, private IPs) or access metadata services (AWS, GCP) by submitting crafted URLs.

**Learning:** When fetching content from URLs provided by users (or even external feeds that could be poisoned), validation is critical. We cannot rely on the frontend or the source to guarantee safety. The `requests` library follows redirects by default, which can be used to bypass initial checks if not handled (though in this fix we prioritized initial URL validation as a first defense).

**Prevention:**
1. Validated the URL scheme (http/https).
2. Resolved the hostname to an IP address before making the request.
3. Explicitly blocked private IP ranges (10.x, 172.16.x, 192.168.x), loopback addresses (127.0.0.1), and link-local addresses.
4. Added `is_safe_url` helper function to encapsulate this logic.
