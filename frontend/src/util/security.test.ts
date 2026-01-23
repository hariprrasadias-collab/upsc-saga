// @vitest-environment jsdom
import { describe, it, expect } from 'vitest';
import { sanitizeHtml } from './security';

describe('sanitizeHtml', () => {
    it('should pass through safe text', () => {
        const input = 'Hello World';
        expect(sanitizeHtml(input)).toBe('Hello World');
    });

    it('should preserve safe tags', () => {
        const input = '<p>Hello <b>World</b></p>';
        expect(sanitizeHtml(input)).toBe('<p>Hello <b>World</b></p>');
    });

    it('should remove script tags', () => {
        const input = '<div>Safe<script>alert(1)</script></div>';
        expect(sanitizeHtml(input)).toBe('<div>Safe</div>');
    });

    it('should remove onclick handlers', () => {
        const input = '<button onclick="alert(1)">Click Me</button>';
        expect(sanitizeHtml(input)).toBe('<button>Click Me</button>');
    });

    it('should remove javascript: hrefs', () => {
        const input = '<a href="javascript:alert(1)">Click Me</a>';
        expect(sanitizeHtml(input)).toBe('<a>Click Me</a>');
    });

    it('should preserve safe image srcs', () => {
        const input = '<img src="https://example.com/image.png">';
        expect(sanitizeHtml(input)).toBe('<img src="https://example.com/image.png">');
    });

    it('should preserve data:image srcs', () => {
        const input = '<img src="data:image/png;base64,abc">';
        expect(sanitizeHtml(input)).toBe('<img src="data:image/png;base64,abc">');
    });

    it('should remove data:text/html srcs (iframe bypass)', () => {
        // The iframe tag itself is in the unsafe list, so it will be removed entirely.
        const input = '<iframe src="data:text/html,<script>alert(1)</script>"></iframe>';
        expect(sanitizeHtml(input)).toBe('');

        // Test data: removal on non-image tags if logic exists, but currently we mostly care about href/src
        const input2 = '<a href="data:text/html,bad">Link</a>';
        expect(sanitizeHtml(input2)).toBe('<a>Link</a>');
    });

    it('should handle complex nesting', () => {
        const input = '<div><p>Test <b onclick="bad()">Bold</b></p><script>bad()</script></div>';
        expect(sanitizeHtml(input)).toBe('<div><p>Test <b>Bold</b></p></div>');
    });

    it('should remove iframes', () => {
        const input = '<div><iframe src="http://evil.com"></iframe></div>';
        expect(sanitizeHtml(input)).toBe('<div></div>');
    });
});
