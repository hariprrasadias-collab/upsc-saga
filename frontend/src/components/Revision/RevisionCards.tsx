import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
            const response = await fetch(`${API_BASE_URL}/api/revision/cards`);
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
        console.log('Generate button clicked!', { title: newCard.title, content: newCard.content });

        if (!newCard.title.trim()) {
            alert('⚠️ Please enter a topic in the TITLE field (the first input box above)');
            return;
        }

        setGenerating(true);
        try {
            console.log('Sending request to backend...');
            const response = await fetch(`${API_BASE_URL}/api/revision/one-liner`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: newCard.title,
                    content: newCard.content
                })
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                console.log('Card created successfully!', data.card);
                setCards([data.card, ...cards]);
                setNewCard({ title: '', content: '' });
                alert('✅ Revision card created successfully!');
            } else {
                console.error('Failed to create card:', data);
                alert('Failed to generate revision card');
            }
        } catch (error) {
            console.error('Error generating card:', error);
            alert('Error generating revision card: ' + (error as Error).message);
        } finally {
            setGenerating(false);
        }
    };

    const handleDeleteCard = async (cardId: number) => {
        console.log('Delete button clicked for card:', cardId);

        // Use window.confirm explicitly and log the result
        const confirmDelete = window.confirm('🗑️ Delete this revision card?\n\nThis action cannot be undone.');
        console.log('Confirm dialog result:', confirmDelete);

        if (!confirmDelete) {
            console.log('Delete cancelled by user');
            return;
        }

        console.log('Proceeding with delete...');
        try {
            const response = await fetch(`${API_BASE_URL}/api/revision/cards/${cardId}`, {
                method: 'DELETE'
            });

            console.log('Delete response status:', response.status);
            if (response.ok) {
                console.log('Card deleted successfully');
                setCards(cards.filter(card => card.id !== cardId));
                alert('✅ Card deleted successfully');
            } else {
                console.error('Delete failed');
                alert('Failed to delete card');
            }
        } catch (error) {
            console.error('Error deleting card:', error);
            alert('Error deleting card');
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
                        placeholder="📝 TITLE: Enter topic name (e.g., 'Preamble of Indian Constitution')"
                        value={newCard.title}
                        onChange={(e) => setNewCard({ ...newCard, title: e.target.value })}
                        onKeyPress={(e) => e.key === 'Enter' && !generating && handleGenerateCard()}
                    />
                    <textarea
                        className="content-textarea"
                        placeholder="💡 CONTENT (Optional): Add details to generate better summary..."
                        rows={4}
                        value={newCard.content}
                        onChange={(e) => setNewCard({ ...newCard, content: e.target.value })}
                    />
                    <button
                        className="generate-btn"
                        onClick={handleGenerateCard}
                        disabled={generating}
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
                                    <div className="card-header-actions">
                                        <span className="card-date">
                                            {new Date(card.created_at).toLocaleDateString()}
                                        </span>
                                        <button
                                            className="delete-card-btn"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteCard(card.id);
                                            }}
                                            title="Delete card"
                                        >
                                            ×
                                        </button>
                                    </div>
                                </div>
                                <div className="card-content markdown-body">
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{card.one_liner}</ReactMarkdown>
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
