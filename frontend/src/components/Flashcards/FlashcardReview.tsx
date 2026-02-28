import { API_BASE_URL } from '../../config';

// FlashcardReview - Interactive review interface with flip animation
import React, { useState, useEffect } from 'react';
import './Flashcards.css';
import { useAnalytics } from '../../contexts/AnalyticsContext';
import MarkdownRenderer from '../Shared/MarkdownRenderer';
import MapWorkCard from './MapWorkCard';

interface Card {
    id: number;
    front: string;
    back: string;
    maturity?: string;
    urgency?: number;
    card_type?: string;
    source?: string;
}

interface FlashcardReviewProps {
    deckId: number | null;
    onFinish: () => void;
}

const FlashcardReview: React.FC<FlashcardReviewProps> = ({ deckId, onFinish }) => {
    const [cards, setCards] = useState<Card[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isFlipped, setIsFlipped] = useState(false);
    const [loading, setLoading] = useState(true);
    const [sessionStart, setSessionStart] = useState(Date.now());
    const [cardsReviewed, setCardsReviewed] = useState(0);
    const { refreshAnalytics } = useAnalytics();

    useEffect(() => {
        fetchDueCards();
    }, [deckId]);

    const fetchDueCards = async () => {
        try {
            const url = deckId
                ? `${API_BASE_URL}/api/flashcards/due?deck_id=${deckId}&limit=20`
                : `${API_BASE_URL}/api/flashcards/due?limit=20`;

            const res = await fetch(url);
            const data = await res.json();
            setCards(data);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch cards:', err);
            setLoading(false);
        }
    };

    const handleRating = async (rating: number) => {
        if (currentIndex >= cards.length) return;

        const card = cards[currentIndex];
        const timeSpent = Math.floor((Date.now() - sessionStart) / 1000);

        try {
            await fetch(`${API_BASE_URL}/api/flashcards/${card.id}/review`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rating, time_taken: timeSpent })
            });

            moveToNext();
        } catch (err) {
            console.error('Failed to record review:', err);
        }
    };

    const moveToNext = () => {
        setCardsReviewed(prev => prev + 1);
        setIsFlipped(false);
        setSessionStart(Date.now());

        if (currentIndex + 1 < cards.length) {
            setCurrentIndex(prev => prev + 1);
        } else {
            finishSession();
        }
    };

    const finishSession = async () => {
        // Award XP
        if (cardsReviewed > 0) {
            await fetch(`${API_BASE_URL}/api/flashcards/award-xp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cards_reviewed: cardsReviewed + 1 })
            });
            refreshAnalytics(true);
        }
        onFinish();
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === ' ' && !isFlipped) {
            setIsFlipped(true);
        } else if (isFlipped) {
            const ratingMap: Record<string, number> = { '1': 1, '2': 2, '3': 3, '4': 4 };
            if (ratingMap[e.key]) {
                handleRating(ratingMap[e.key]);
            }
        }
    };

    if (loading) return <div className="loading">Loading cards...</div>;
    if (cards.length === 0) return <div className="no-cards">No cards due for review! 🎉</div>;
    if (currentIndex >= cards.length) {
        finishSession();
        return <div className="session-complete">Session complete! 🎉</div>;
    }

    const currentCard = cards[currentIndex];

    // Check if this is a Map Work card
    if (currentCard.card_type === 'map_work') {
        let mapData = [];
        try {
            mapData = JSON.parse(currentCard.back);
        } catch (e) {
            console.error("Failed to parse map data", e);
        }

        if (mapData.length > 0) {
            return (
                 <div className="flashcard-review" style={{ height: '600px' }}> {/* Increased height for map */}
                    <div className="review-progress">
                        <div className="progress-text">
                            Card {currentIndex + 1} / {cards.length}
                        </div>
                        <div className="progress-bar-container">
                            <div
                                className="progress-bar-fill"
                                style={{ width: `${((currentIndex + 1) / cards.length) * 100}%` }}
                            />
                        </div>
                    </div>

                    <MapWorkCard
                        data={mapData}
                        onComplete={() => handleRating(3)} // Auto-rate as Good on completion for now
                    />

                    <div className="session-stats">
                         <span>Reviewed: {cardsReviewed}</span>
                         <button onClick={finishSession} className="end-session-btn">End Session</button>
                    </div>
                </div>
            );
        }
    }

    return (
        <div className="flashcard-review" tabIndex={0} onKeyDown={handleKeyPress}>
            {/* Progress */}
            <div className="review-progress">
                <div className="progress-text">
                    Card {currentIndex + 1} / {cards.length}
                </div>
                <div className="progress-bar-container">
                    <div
                        className="progress-bar-fill"
                        style={{ width: `${((currentIndex + 1) / cards.length) * 100}%` }}
                    />
                </div>
            </div>

            {/* Card */}
            <div className={`flashcard ${isFlipped ? 'flipped' : ''}`} onClick={() => setIsFlipped(!isFlipped)}>
                <div className="flashcard-inner">
                    <div className="flashcard-front">
                        <div className="card-content"><MarkdownRenderer content={currentCard.front} /></div>
                        <div className="flip-hint">Click or press Space to flip</div>
                    </div>
                    <div className="flashcard-back">
                        <div className="card-content"><MarkdownRenderer content={currentCard.back} /></div>
                    </div>
                </div>
            </div>

            {/* Ratings (only show when flipped) */}
            {isFlipped && (
                <div className="rating-buttons">
                    <button onClick={() => handleRating(1)} className="rating-btn again">
                        <span className="key">1</span>
                        <span className="label">Again</span>
                    </button>
                    <button onClick={() => handleRating(2)} className="rating-btn hard">
                        <span className="key">2</span>
                        <span className="label">Hard</span>
                    </button>
                    <button onClick={() => handleRating(3)} className="rating-btn good">
                        <span className="key">3</span>
                        <span className="label">Good</span>
                    </button>
                    <button onClick={() => handleRating(4)} className="rating-btn easy">
                        <span className="key">4</span>
                        <span className="label">Easy</span>
                    </button>
                </div>
            )}

            {/* Session Stats */}
            <div className="session-stats">
                <span>Reviewed: {cardsReviewed}</span>
                <button onClick={finishSession} className="end-session-btn">End Session</button>
            </div>
        </div>
    );
};

export default FlashcardReview;
