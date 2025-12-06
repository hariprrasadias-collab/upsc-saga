import React from 'react';
import './Renderers.css';

interface QuoteBankProps {
    content: string;
}

const QuoteBankRenderer: React.FC<QuoteBankProps> = ({ content }) => {
    // Expected format: "Quote" - Author (or similar)
    const quotes = content.split('\n').filter(l => l.trim().length > 0).map(line => {
        const parts = line.split('-');
        if (parts.length > 1) {
            return {
                text: parts[0].trim().replace(/^["']|["']$/g, ''), // Remove quotes if present
                author: parts.slice(1).join('-').trim()
            };
        }
        return { text: line.replace(/^["']|["']$/g, ''), author: 'Anonymous' };
    });

    return (
        <div className="quote-bank-container">
            {quotes.map((quote, idx) => (
                <div key={idx} className="quote-card glass-card">
                    <div className="quote-icon">❝</div>
                    <p className="quote-text">{quote.text}</p>
                    <div className="quote-author">— {quote.author}</div>
                </div>
            ))}
        </div>
    );
};

export default QuoteBankRenderer;
