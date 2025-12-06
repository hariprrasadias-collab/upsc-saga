import React from 'react';
import './Renderers.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface ELI5Props {
    content: string;
}

const ELI5Renderer: React.FC<ELI5Props> = ({ content }) => {
    return (
        <div className="eli5-container glass-card">
            <div className="eli5-header">
                <span className="eli5-icon">🧸</span>
                <h2>Explain Like I'm 5</h2>
            </div>
            <div className="eli5-content">
                <MarkdownRenderer content={content} />
            </div>
            <div className="eli5-footer">
                <span className="tag">#Simple</span>
                <span className="tag">#Fun</span>
                <span className="tag">#Basics</span>
            </div>
        </div>
    );
};

export default ELI5Renderer;
