import React from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface Props {
    content: string;
}

const QuoteBankRenderer: React.FC<Props> = ({ content }) => {
    return (
        <div className="quote-bank-container" style={{ borderLeft: '4px solid #a855f7', paddingLeft: '20px', margin: '10px 0', background: 'rgba(168, 85, 247, 0.05)', padding: '15px' }}>
            <h3 style={{ color: '#a855f7', marginTop: 0 }}>💬 Quote Bank</h3>
            <MarkdownRenderer content={content} />
        </div>
    );
};

export default QuoteBankRenderer;
