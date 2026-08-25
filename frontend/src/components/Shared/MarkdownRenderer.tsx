import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MarkdownRenderer.css';

interface MarkdownRendererProps {
    content: string;
    className?: string;
}

// ⚡ Bolt Performance Optimization:
// Wrapped in React.memo to prevent expensive re-parsing of markdown content on every parent render.
// Impact: Reduces CPU load and prevents main-thread blocking during rapid state changes in parent components (e.g., typing in sibling inputs).
const MarkdownRenderer: React.FC<MarkdownRendererProps> = React.memo(({ content, className = '' }) => {
    return (
        <div className={`markdown-content ${className}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content}
            </ReactMarkdown>
        </div>
    );
});
MarkdownRenderer.displayName = 'MarkdownRenderer';

export default MarkdownRenderer;
