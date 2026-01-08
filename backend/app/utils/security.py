import bleach

def sanitize_html(content):
    """
    Sanitizes HTML content using bleach.
    Allows standard rich text tags and attributes common in Anki cards and articles.
    """
    if not content:
        return ""

    allowed_tags = {
        'b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li',
        'code', 'pre', 'span', 'div', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'table', 'thead', 'tbody', 'tr', 'td', 'th', 'img', 'style'
    }

    allowed_attrs = {
        '*': ['class', 'style'],
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height']
    }

    # Bleach 6.x supports protocols argument.
    allowed_protocols = ['http', 'https', 'mailto', 'data']

    try:
        return bleach.clean(
            str(content),
            tags=list(allowed_tags),
            attributes=allowed_attrs,
            protocols=allowed_protocols,
            strip=True
        )
    except Exception as e:
        print(f"Sanitization error: {e}")
        return ""
