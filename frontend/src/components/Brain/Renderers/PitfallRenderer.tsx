import React from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface Props {
    content: string;
}

const PitfallRenderer: React.FC<Props> = ({ content }) => {
    return (
        <div className="pitfall-container" style={{ border: '1px solid #ef4444', padding: '15px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.05)' }}>
            <h3 style={{ color: '#ef4444', marginTop: 0 }}>⚠️ Common Pitfalls</h3>
            <MarkdownRenderer content={content} />
        </div>
    );
};

export default PitfallRenderer;
