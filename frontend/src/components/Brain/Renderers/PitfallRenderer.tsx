import React from 'react';
import './Renderers.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface PitfallProps {
    content: string;
}

const PitfallRenderer: React.FC<PitfallProps> = ({ content }) => {
    // Try to parse bullet points as individual "mistakes" if possible
    // Otherwise just render the markdown in a warning box

    return (
        <div className="pitfall-container">
            <div className="pitfall-banner">
                <span className="warning-icon">⚠️</span>
                <h3>Common Pitfalls & Mistakes</h3>
            </div>
            <div className="pitfall-card glass-card">
                <MarkdownRenderer content={content} />
            </div>
        </div>
    );
};

export default PitfallRenderer;
