import React, { useState } from 'react';
import './Flashcards.css';
import DeckManager from './DeckManager';
import FlashcardReview from './FlashcardReview';
import FlashcardStats from './FlashcardStats';

interface FlashcardsManagerProps {
    onTaskCompleted?: () => void;
}

const FlashcardsManager: React.FC<FlashcardsManagerProps> = ({ onTaskCompleted }) => {
    const [view, setView] = useState<'decks' | 'review' | 'stats'>('decks');
    const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null);

    const handleStartReview = (deckId?: number) => {
        setSelectedDeckId(deckId || null);
        setView('review');
    };

    const handleFinishReview = () => {
        setView('decks');
        if (onTaskCompleted) {
            onTaskCompleted();
        }
    };

    return (
        <div className="flashcards-manager">
            {/* Header with Navigation */}
            <div className="flashcards-header">
                <h1>🎴 Flashcards - Yggdrasil 2.0</h1>
                <div className="flashcards-nav">
                    <button
                        onClick={() => setView('decks')}
                        className={`nav-btn ${view === 'decks' ? 'active' : ''}`}
                    >
                        📚 Decks
                    </button>
                    <button
                        onClick={() => setView('review')}
                        className={`nav-btn ${view === 'review' ? 'active' : ''}`}
                    >
                        🎯 Review
                    </button>
                    <button
                        onClick={() => setView('stats')}
                        className={`nav-btn ${view === 'stats' ? 'active' : ''}`}
                    >
                        📊 Statistics
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flashcards-content">
                {view === 'decks' && (
                    <DeckManager onStartReview={handleStartReview} />
                )}
                {view === 'review' && (
                    <FlashcardReview
                        deckId={selectedDeckId}
                        onFinish={handleFinishReview}
                    />
                )}
                {view === 'stats' && (
                    <FlashcardStats />
                )}
            </div>
        </div>
    );
};

export default FlashcardsManager;
