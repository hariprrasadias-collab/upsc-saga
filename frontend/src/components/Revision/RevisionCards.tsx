import React, { useState, useEffect } from 'react';
import './RevisionCards.css';

interface RevisionCard {
    id: number;
    topic_id: string;
    title: string;
    one_liner: string;
    created_at: string;
}

const RevisionCards: React.FC = () => {
    const [cards, setCards] = useState<RevisionCard[]>([]);
    const [loading, setLoading] = useState(false);
    const [newCard, setNewCard] = useState({ title: '', content: '' });
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchCards();
    }, []);

    const fetchCards = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/revision/cards');
            const data = await response.json();
            if (data.success) {
                setCards(data.cards);
            }
        } catch (error) {
            console.error('Error fetching cards:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateCard = async () => {
        if (!newCard.title.trim()) {
            alert('Please enter a topic title');
            return;
        }

        setGenerating(true);
        try {
            const response = await fetch('http://localhost:5000/api/revision/one-liner', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: newCard.title,
                    content: newCard.content
                })
            });

            const data = await response.json();
            if (data.success) {
                setCards([data.card, ...cards]);
                setNewCard({ title: '', content: '' });
            } else {
                alert('Failed to generate revision card');
            }
        } catch (error) {
            console.error('Error generating card:', error);
            alert('Error generating revision card');
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="revision-cards-container">
            <div className="revision-header">
                <h1>⚡ Quick Revision Cards</h1>
                <p className="revision-subtitle">High-yield smart summaries for last-minute revision</p>
            </div>

            {/* Create New Card */}
            <div className="card-generator">
                <h2>Generate New Card</h2>
                <div className="generator-form">
                    <input
                        type="text"
                        className="topic-input"
                        placeholder="Topic Title (e.g., 'Preamble of Indian Constitution')"
                        value={newCard.title}
                        onChange={(e) => setNewCard({ ...newCard, title: e.target.value })}
                    />
                    <textarea
                        className="content-textarea"
                        placeholder="Topic content (optional - helps generate better summary)"
                        rows={4}
                        value={newCard.content}
                        onChange={(e) => setNewCard({ ...newCard, content: e.target.value })}
                    />
                    <button
                        className="generate-btn"
                        onClick={handleGenerateCard}
                        disabled={generating}
                        style={{ opacity: generating ? 0.7 : 1, cursor: generating ? 'wait' : 'pointer' }}
                    >
                        {generating ? '✨ Forging Knowledge...' : '🚀 Generate Smart Summary'}
                    </button>
                </div>
            </div>

            {/* Cards List */}
            <div className="cards-section">
                <h2>Your Revision Cards ({cards.length})</h2>

                {loading ? (
                    <div className="loading-state">Loading cards...</div>
                ) : cards.length === 0 ? (
                    <div className="empty-state">
                        <p>📝 No revision cards yet</p>
                        <p className="empty-subtitle">Create your first card above!</p>
                    </div>
                ) : (
                    <div className="cards-grid">
                        {cards.map((card) => (
                            <div key={card.id} className="revision-card">
                                <div className="card-header">
                                    <h3>{card.title}</h3>
                                    <span className="card-date">
                                        {new Date(card.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                                <div className="card-content">
                                    <p className="one-liner">{card.one_liner}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default RevisionCards;
