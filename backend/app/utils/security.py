import html

def sanitize_html(text):
    """
    Sanitize text to prevent XSS attacks by escaping HTML characters.

    Args:
        text (str): The input text to sanitize.

    Returns:
        str: The sanitized text.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        return str(text)
    return html.escape(text)
