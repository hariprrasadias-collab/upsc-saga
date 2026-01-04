import html

def sanitize_html(content):
    """
    Sanitizes HTML content by escaping special characters.
    This prevents Stored XSS by converting <script> to &lt;script&gt;.

    WARNING: This will escape ALL HTML tags, rendering rich text as plain text code.
    This is a strict security measure until a proper HTML sanitizer (like 'bleach')
    is added to the dependencies to allow safe whitelisted tags.

    Args:
        content (str): The raw input string.

    Returns:
        str: The sanitized string safe for storage and display.
    """
    if not content:
        return ""
    return html.escape(str(content))
