import React from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface Props {
    content: string;
}

const CheatSheetRenderer: React.FC<Props> = ({ content }) => {
    return (
        <div className="cheat-sheet-container" style={{ border: '1px solid #4ade80', padding: '15px', borderRadius: '8px', background: 'rgba(74, 222, 128, 0.05)' }}>
            <h3 style={{ color: '#4ade80', marginTop: 0, borderBottom: '1px solid rgba(74, 222, 128, 0.3)', paddingBottom: '10px' }}>📝 Quick Reference</h3>
            <MarkdownRenderer content={content} />
        </div>
    );
};

export default CheatSheetRenderer;
