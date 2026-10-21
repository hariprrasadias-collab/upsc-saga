import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MarkdownRenderer.css';

interface MarkdownRendererProps {
    content: string;
    className?: string;
}

// ⚡ Bolt: Hoisted static array reference outside component to prevent
// ReactMarkdown from re-rendering due to a new array instance on every render.
const remarkPlugins = [remarkGfm];

// ⚡ Bolt: Wrapped in React.memo to prevent unnecessary re-renders of the
// expensive ReactMarkdown component when parent state changes.
const MarkdownRenderer: React.FC<MarkdownRendererProps> = React.memo(({ content, className = '' }) => {
    return (
        <div className={`markdown-content ${className}`}>
            <ReactMarkdown remarkPlugins={remarkPlugins}>
                {content}
            </ReactMarkdown>
        </div>
    );
});

export default MarkdownRenderer;
