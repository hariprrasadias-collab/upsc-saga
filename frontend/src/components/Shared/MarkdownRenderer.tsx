import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MarkdownRenderer.css';

interface MarkdownRendererProps {
    content: string;
    className?: string;
}

// ⚡ Bolt Optimization: Extract plugin array to maintain stable reference across renders
const remarkPlugins = [remarkGfm];

// ⚡ Bolt Optimization: Memoize the MarkdownRenderer component.
// Markdown parsing is expensive. Memoizing prevents unnecessary re-parsing and re-rendering
// when parent components update but the markdown content string remains exactly the same.
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
