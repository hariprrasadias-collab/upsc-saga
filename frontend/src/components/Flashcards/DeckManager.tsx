// DeckManager - Manage decks and cards
import React, { useState, useEffect } from 'react';
import './Flashcards.css';

interface Deck {
    id: number;
    name: string;
    description: string;
    subject: string;
    color: string;
    card_count: number;
}

interface DeckManagerProps {
    onStartReview: (deckId?: number) => void;
}

const DeckManager: React.FC<DeckManagerProps> = ({ onStartReview }) => {
    const [decks, setDecks] = useState<Deck[]>([]);
    const [loading, setLoading] = useState(true);
    const [showNewDeck, setShowNewDeck] = useState(false);
    const [newDeckName, setNewDeckName] = useState('');
    const [newDeckSubject, setNewDeckSubject] = useState('GS1');

    useEffect(() => {
        fetchDecks();
    }, []);

    const fetchDecks = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/flashcards/decks');
            const data = await res.json();
            setDecks(data);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch decks:', err);
            setLoading(false);
        }
    };

    const handleCreateDeck = async () => {
        if (!newDeckName.trim()) return;

        try {
            await fetch('http://localhost:5000/api/flashcards/decks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: newDeckName,
                    subject: newDeckSubject
                })
            });

            setNewDeckName('');
            setShowNewDeck(false);
            fetchDecks();
        } catch (err) {
            console.error('Failed to create deck:', err);
        }
    };

    if (loading) return <div className="loading">Loading decks...</div>;

    return (
        <div className="deck-manager">
            <div className="deck-manager-header">
                <h2>Your Decks</h2>
                <button onClick={() => onStartReview()} className="review-all-btn">
                    🎯 Review All Due Cards
                </button>
                <button onClick={() => setShowNewDeck(true)} className="new-deck-btn">
                    + New Deck
                </button>
            </div>

            {showNewDeck && (
                <div className="new-deck-form">
                    <input
                        type="text"
                        value={newDeckName}
                        onChange={(e) => setNewDeckName(e.target.value)}
                        placeholder="Deck name..."
                        className="deck-name-input"
                    />
                    <select value={newDeckSubject} onChange={(e) => setNewDeckSubject(e.target.value)}>
                        <option value="GS1">GS1</option>
                        <option value="GS2">GS2</option>
                        <option value="GS3">GS3</option>
                        <option value="GS4">GS4</option>
                        <option value="Optional">Optional</option>
                        <option value="Prelims">Prelims</option>
                    </select>
                    <button onClick={handleCreateDeck} className="create-btn">Create</button>
                    <button onClick={() => setShowNewDeck(false)} className="cancel-btn">Cancel</button>
                </div>
            )}

            <div className="decks-grid">
                {decks.map((deck) => (
                    <div key={deck.id} className="deck-card" style={{ borderColor: deck.color }}>
                        <div className="deck-header">
                            <h3>{deck.name}</h3>
                            <span className="subject-badge" style={{ backgroundColor: deck.color }}>
                                {deck.subject}
                            </span>
                        </div>
                        <p className="deck-description">{deck.description || 'No description'}</p>
                        <div className="deck-stats">
                            <span>{deck.card_count} cards</span>
                        </div>
                        <button
                            onClick={() => onStartReview(deck.id)}
                            className="review-deck-btn"
                        >
                            Review
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DeckManager;
