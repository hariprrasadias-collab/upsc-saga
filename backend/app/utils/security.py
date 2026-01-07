import re
from html.parser import HTMLParser

class WhiteListSanitizer(HTMLParser):
    """
    A whitelist-based HTML sanitizer to prevent XSS.
    Parses HTML and reconstructs it including only allowed tags and attributes.
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

        # Whitelist of allowed tags (rich text but no scripting)
        self.allowed_tags = {
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
            'div', 'span', 'p', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img',
            'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'pre', 'sup', 'sub',
            'small', 'big', 'font', 'center', 'u', 's', 'strike', 'del', 'ins', 'dl', 'dt', 'dd',
            'audio', 'video', 'source', 'caption', 'mark', 'cite'
        }

        # Whitelist of allowed attributes
        self.allowed_attrs = {
            'href', 'src', 'title', 'alt', 'class', 'id', 'style', 'width', 'height',
            'align', 'valign', 'target', 'rel', 'controls', 'poster', 'colspan', 'rowspan',
            'cellpadding', 'cellspacing', 'border'
        }

        self.ignore_content = False # Flag to ignore content inside bad tags

    def handle_starttag(self, tag, attrs):
        if tag in self.allowed_tags:
            self.ignore_content = False
            safe_attrs = []
            for k, v in attrs:
                if k in self.allowed_attrs:
                    # Security Check: Prevent javascript:/vbscript: URIs
                    if k in ('href', 'src'):
                        clean_v = v.lower().strip()
                        # Allow data:image but block others
                        is_data_image = clean_v.startswith('data:image/')
                        if (clean_v.startswith('javascript:') or
                            clean_v.startswith('vbscript:') or
                            (clean_v.startswith('data:') and not is_data_image)):
                            continue

                    # Escape quotes in attribute values
                    safe_v = v.replace('"', '&quot;')
                    safe_attrs.append(f'{k}="{safe_v}"')

            attr_str = ' ' + ' '.join(safe_attrs) if safe_attrs else ''
            self.fed.append(f"<{tag}{attr_str}>")
        else:
            # If tag is script or style, we want to ignore its content
            if tag in ('script', 'style', 'noscript', 'iframe', 'textarea', 'title'):
                self.ignore_content = True

    def handle_endtag(self, tag):
        if tag in self.allowed_tags:
            self.fed.append(f"</{tag}>")

        # Turn off ignore_content if we just closed a bad tag
        if tag in ('script', 'style', 'noscript', 'iframe', 'textarea', 'title'):
            self.ignore_content = False

    def handle_startendtag(self, tag, attrs):
        """Handle self-closing tags like <br/>"""
        if tag in self.allowed_tags:
            safe_attrs = []
            for k, v in attrs:
                if k in self.allowed_attrs:
                    if k in ('href', 'src'):
                        clean_v = v.lower().strip()
                        is_data_image = clean_v.startswith('data:image/')
                        if (clean_v.startswith('javascript:') or
                            clean_v.startswith('vbscript:') or
                            (clean_v.startswith('data:') and not is_data_image)):
                            continue
                    safe_v = v.replace('"', '&quot;')
                    safe_attrs.append(f'{k}="{safe_v}"')

            attr_str = ' ' + ' '.join(safe_attrs) if safe_attrs else ''
            self.fed.append(f"<{tag}{attr_str} />")

    def handle_data(self, d):
        if not self.ignore_content:
            self.fed.append(d)

    def handle_entityref(self, name):
        if not self.ignore_content:
            self.fed.append(f'&{name};')

    def handle_charref(self, name):
        if not self.ignore_content:
            self.fed.append(f'&#{name};')

    def get_data(self):
        return "".join(self.fed)

def sanitize_html(html_content):
    """
    Sanitizes HTML content by removing unsafe tags and attributes.
    Returns the sanitized HTML string.
    """
    if not html_content:
        return ""

    # Simple type check
    if not isinstance(html_content, str):
        return str(html_content)

    s = WhiteListSanitizer()
    try:
        s.feed(html_content)
        return s.get_data()
    except Exception as e:
        print(f"Sanitization error: {e}")
        # Fail safe: escape everything if parsing fails
        import html
        return html.escape(html_content)
