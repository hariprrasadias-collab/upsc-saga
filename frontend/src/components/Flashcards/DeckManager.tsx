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

    const [showAddCard, setShowAddCard] = useState<number | null>(null);
    const [viewDeckId, setViewDeckId] = useState<number | null>(null);
    const [cardFront, setCardFront] = useState('');
    const [cardBack, setCardBack] = useState('');
    const [showCsvImport, setShowCsvImport] = useState<number | null>(null);
    const [csvFile, setCsvFile] = useState<File | null>(null);
    const [importing, setImporting] = useState(false);

    const handleAddCard = async () => {
        if (!cardFront.trim() || !cardBack.trim() || !showAddCard) return;

        try {
            await fetch('http://localhost:5000/api/flashcards', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    deck_id: showAddCard,
                    front: cardFront,
                    back: cardBack
                })
            });

            setCardFront('');
            setCardBack('');
            setShowAddCard(null);
            fetchDecks(); // Update counts
        } catch (err) {
            console.error('Failed to add card:', err);
        }
    };

    const handleCsvImport = async () => {
        if (!csvFile || !showCsvImport) return;

        setImporting(true);
        const text = await csvFile.text();
        const lines = text.split('\n').filter(l => l.trim());

        let successCount = 0;
        for (const line of lines) {
            const [front, back] = line.split(',').map(s => s.trim());
            if (front && back) {
                try {
                    await fetch('http://localhost:5000/api/flashcards', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            deck_id: showCsvImport,
                            front,
                            back
                        })
                    });
                    successCount++;
                } catch (err) {
                    console.error('Failed to import card:', err);
                }
            }
        }

        alert(`Imported ${successCount} cards successfully!`);
        setCsvFile(null);
        setShowCsvImport(null);
        setImporting(false);
        fetchDecks();
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

            {showAddCard && (
                <div className="modal-overlay">
                    <div className="modal-content add-card-modal">
                        <h3>Add New Card</h3>
                        <div className="form-group">
                            <label>Front</label>
                            <textarea
                                value={cardFront}
                                onChange={e => setCardFront(e.target.value)}
                                placeholder="Question or Term"
                                rows={3}
                            />
                        </div>
                        <div className="form-group">
                            <label>Back</label>
                            <textarea
                                value={cardBack}
                                onChange={e => setCardBack(e.target.value)}
                                placeholder="Answer or Definition"
                                rows={5}
                            />
                        </div>
                        <div className="modal-actions">
                            <button onClick={() => setShowAddCard(null)} className="cancel-btn">Cancel</button>
                            <button onClick={handleAddCard} className="save-btn">Add Card</button>
                        </div>
                    </div>
                </div>
            )}

            {showCsvImport && (
                <div className="modal-overlay">
                    <div className="modal-content csv-import-modal">
                        <h3>Import Cards from CSV</h3>
                        <p className="csv-help">Upload a CSV file with format: <code>front,back</code></p>
                        <input
                            type="file"
                            accept=".csv"
                            onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                            className="file-input"
                        />
                        {csvFile && <p className="file-name">Selected: {csvFile.name}</p>}
                        <div className="modal-actions">
                            <button onClick={() => setShowCsvImport(null)} className="cancel-btn">Cancel</button>
                            <button
                                onClick={handleCsvImport}
                                className="save-btn"
                                disabled={!csvFile || importing}
                            >
                                {importing ? 'Importing...' : 'Import'}
                            </button>
                        </div>
                    </div>
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
                            <button
                                className="delete-deck-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (window.confirm('Delete this deck and all its cards?')) {
                                        fetch(`http://localhost:5000/api/flashcards/decks/${deck.id}`, { method: 'DELETE' })
                                            .then(() => fetchDecks());
                                    }
                                }}
                            >
                                🗑️
                            </button>
                        </div>
                        <p className="deck-description">{deck.description || 'No description'}</p>
                        <div className="deck-stats">
                            <span>{deck.card_count} cards</span>
                        </div>
                        <div className="deck-actions">
                            <button
                                onClick={() => onStartReview(deck.id)}
                                className="review-deck-btn"
                            >
                                Review
                            </button>
                            <button
                                onClick={() => setShowAddCard(deck.id)}
                                className="add-card-btn"
                            >
                                + Add Card
                            </button>
                            <button
                                onClick={() => setShowCsvImport(deck.id)}
                                className="import-csv-btn"
                            >
                                📥 Import CSV
                            </button>
                            <button
                                onClick={() => setViewDeckId(deck.id)}
                                className="view-cards-btn"
                            >
                                👁️ View
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {viewDeckId && (
                <DeckCardList
                    deckId={viewDeckId}
                    onClose={() => setViewDeckId(null)}
                    onUpdate={() => fetchDecks()}
                />
            )}
        </div>
    );
};

interface DeckCardListProps {
    deckId: number;
    onClose: () => void;
    onUpdate: () => void;
}

const DeckCardList: React.FC<DeckCardListProps> = ({ deckId, onClose, onUpdate }) => {
    const [cards, setCards] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch(`http://localhost:5000/api/flashcards/decks/${deckId}`)
            .then(res => res.json())
            .then(data => {
                setCards(data.cards);
                setLoading(false);
            })
            .catch(err => console.error(err));
    }, [deckId]);

    const handleDeleteCard = async (cardId: number) => {
        if (!window.confirm('Delete this card?')) return;
        try {
            await fetch(`http://localhost:5000/api/flashcards/${cardId}`, { method: 'DELETE' });
            setCards(prev => prev.filter(c => c.id !== cardId));
            onUpdate();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content card-list-modal" style={{ maxWidth: '800px', width: '90%' }}>
                <div className="modal-header">
                    <h3>Deck Cards</h3>
                    <button onClick={onClose} className="close-btn">×</button>
                </div>
                <div className="cards-list-container" style={{ maxHeight: '60vh', overflowY: 'auto', marginTop: '1rem' }}>
                    {loading ? <div>Loading cards...</div> : cards.length === 0 ? <div>No cards in this deck.</div> : (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #444' }}>
                                    <th style={{ padding: '10px', textAlign: 'left' }}>Front</th>
                                    <th style={{ padding: '10px', textAlign: 'left' }}>Back</th>
                                    <th style={{ padding: '10px' }}>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cards.map(card => (
                                    <tr key={card.id} style={{ borderBottom: '1px solid #333' }}>
                                        <td style={{ padding: '10px' }}>{card.front}</td>
                                        <td style={{ padding: '10px' }}>{card.back}</td>
                                        <td style={{ padding: '10px', textAlign: 'center' }}>
                                            <button
                                                onClick={() => handleDeleteCard(card.id)}
                                                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                                            >
                                                🗑️
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DeckManager;
