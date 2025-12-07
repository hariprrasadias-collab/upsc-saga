import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface Props {
    content: string;
}

const QuoteBankRenderer: React.FC<Props> = ({ content }) => {
    // Parse Markdown List Items into Array
    // This simple regex looks for lines starting with * or - followed by text
    const quotes = content
        .split('\n')
        .filter(line => line.trim().match(/^[-*]\s+/))
        .map(line => line.replace(/^[-*]\s+/, '').trim());

    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

    const handleCopy = (text: string, index: number) => {
        navigator.clipboard.writeText(text);
        setCopiedIndex(index);
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    if (quotes.length === 0) {
        // Fallback for non-list content
        return (
            <div className="quote-bank-container" style={{ borderLeft: '4px solid #a855f7', padding: '15px', background: 'rgba(168, 85, 247, 0.05)' }}>
                <h3 style={{ color: '#a855f7', marginTop: 0 }}>💬 Quote Bank</h3>
                <div style={{ whiteSpace: 'pre-wrap' }}>{content}</div>
            </div>
        );
    }

    return (
        <div className="quote-bank-grid">
            <h3 style={{ color: '#a855f7', marginBottom: '15px' }}>💬 Quote Bank</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '15px' }}>
                {quotes.map((quote, idx) => (
                    <motion.div
                        key={idx}
                        className="quote-card glass-panel"
                        whileHover={{ scale: 1.03, backgroundColor: 'rgba(168, 85, 247, 0.15)' }}
                        style={{
                            padding: '15px',
                            border: '1px solid rgba(168, 85, 247, 0.3)',
                            borderRadius: '10px',
                            cursor: 'pointer',
                            position: 'relative',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between'
                        }}
                        onClick={() => handleCopy(quote, idx)}
                    >
                        <p style={{ fontStyle: 'italic', marginBottom: '10px', fontSize: '0.95rem' }}>"{quote}"</p>
                        <div style={{ alignSelf: 'flex-end', fontSize: '0.8rem', color: copiedIndex === idx ? '#4ade80' : '#a855f7' }}>
                            {copiedIndex === idx ? '✓ Copied' : '📋 Copy'}
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default QuoteBankRenderer;
