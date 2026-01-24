/**
 * Security utilities for frontend sanitization.
 *
 * 🛡️ Sentinel Security Module
 * Protects against XSS attacks by sanitizing HTML content before rendering.
 */

/**
 * Sanitizes HTML string to remove unsafe tags and attributes.
 * Uses the browser's DOMParser to parse and scrub the content.
 *
 * @param html The raw HTML string to sanitize
 * @returns The sanitized HTML string safe for dangerouslySetInnerHTML
 */
export const sanitizeHtml = (html: string): string => {
    if (!html) return '';

    // Create a new DOMParser
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // List of tags to strip completely (including content)
    // script: XSS execution
    // iframe/object/embed: External content injection
    // style: CSS injection (can be used for data exfiltration)
    // meta/base: Page structure manipulation
    // form: Phishing risk
    const unsafeTags = ['script', 'iframe', 'object', 'embed', 'link', 'style', 'meta', 'base', 'form'];

    unsafeTags.forEach(tag => {
        const elements = doc.querySelectorAll(tag);
        elements.forEach(el => el.remove());
    });

    // Clean attributes on all remaining elements
    const allElements = doc.querySelectorAll('*');
    allElements.forEach(el => {
        // Get all attribute names
        const attrs = el.getAttributeNames();

        attrs.forEach(attr => {
            const attrName = attr.toLowerCase();
            const attrValue = el.getAttribute(attr);

            // 1. Remove event handlers (on*)
            // e.g., onerror, onclick, onmouseover
            if (attrName.startsWith('on')) {
                el.removeAttribute(attr);
                return;
            }

            // 2. Check for javascript: protocol in href and src
            if ((attrName === 'href' || attrName === 'src') && attrValue) {
                const val = attrValue.trim().toLowerCase();

                // Block javascript: URIs
                if (val.startsWith('javascript:')) {
                    el.removeAttribute(attr);
                    return;
                }

                // Block data: URIs except images
                if (val.startsWith('data:')) {
                    if (!val.startsWith('data:image/')) {
                        el.removeAttribute(attr);
                        return;
                    }
                }
            }
        });
    });

    return doc.body.innerHTML;
};
