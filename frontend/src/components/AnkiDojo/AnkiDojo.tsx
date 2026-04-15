import { API_BASE_URL } from '../../config';

// /frontend/src/components/AnkiDojo/AnkiDojo.tsx
import React, { useState, useEffect } from 'react';
import './AnkiDojo.css';
import { audioManager } from '../../util/AudioManager';
import { ebisuScheduler } from './ebisuAlgorithm';
import DOMPurify from 'dompurify';

interface AnkiCard {
    id: number;
    question: string;
    answer: string;
    deckName: string;
}

type StudyMode = 'normal' | 'smart';

const AnkiDojo: React.FC = () => {
    const [queue, setQueue] = useState<number[]>([]);
    const [currentCard, setCurrentCard] = useState<AnkiCard | null>(null);
    const [isFlipped, setIsFlipped] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [studyMode, setStudyMode] = useState<StudyMode>('smart'); // Default to Smart Learn
    const [sessionCards, setSessionCards] = useState<number[]>([]);
    const [totalStudied, setTotalStudied] = useState(0);
    const [correctCount, setCorrectCount] = useState(0);
    const [streak, setStreak] = useState(0);
    const [refetchTrigger, setRefetchTrigger] = useState(0); // NEW: Trigger for refetch

    // Load Ebisu state from localStorage on mount
    useEffect(() => {
        const savedState = localStorage.getItem('ebisuState');
        if (savedState) {
            ebisuScheduler.importState(savedState);
        }
    }, []);

    // Save Ebisu state to localStorage whenever it changes
    const saveEbisuState = () => {
        const state = ebisuScheduler.exportState();
        localStorage.setItem('ebisuState', state);
    };

    // 1. Load the Queue (List of Due IDs) - NOW ALSO TRIGGERS ON refetchTrigger
    useEffect(() => {
        const fetchQueue = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/anki/queue`);
                if (!res.ok) throw new Error("Anki Connection Failed");
                const raw = await res.json();
                const ids = raw.success === false ? [] : (raw.data || raw);

                if (!Array.isArray(ids)) throw new Error("Invalid Anki Queue");

                // In Smart Learn mode, sort by Ebisu priority
                if (studyMode === 'smart') {
                    const sortedIds = ebisuScheduler.sortCardsByPriority(ids);
                    setQueue(sortedIds);
                    setSessionCards(sortedIds);
                } else {
                    setQueue(ids);
                    setSessionCards(ids);
                }

                setLoading(false);
            } catch {
                setError("Could not connect to Anki. Make sure the Anki App is running with AnkiConnect installed.");
                setLoading(false);
            }
        };
        fetchQueue();
    }, [studyMode, refetchTrigger]); // FIXED: Added refetchTrigger dependency

    // 2. Load Specific Card Content when queue updates
    useEffect(() => {
        const fetchNextCard = async () => {
            if (queue.length > 0 && !currentCard) {
                setLoading(true);
                const nextId = queue[0];
                try {
                    const res = await fetch(`${API_BASE_URL}/api/anki/card`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ card_id: nextId })
                    });
                    const raw = await res.json();
                    const cardData = raw.data || raw;
                    setCurrentCard(cardData);
                    setIsFlipped(false); // Reset flip
                } catch {
                    // Error loading card
                } finally {
                    setLoading(false);
                }
            }
        };
        fetchNextCard();
    }, [queue, currentCard]);

    // 3. Handle User Answer with Ebisu algorithm
    const handleAnswer = async (ease: number) => {
        if (!currentCard) return;

        const isCorrect = ease >= 3; // Good or Easy
        setTotalStudied(prev => prev + 1);

        if (isCorrect) {
            setCorrectCount(prev => prev + 1);
            setStreak(prev => prev + 1);
            audioManager.play('success');
        } else {
            setStreak(0);
            audioManager.play('click');
        }

        // Update Ebisu algorithm
        if (studyMode === 'smart') {
            ebisuScheduler.updateAfterReview(currentCard.id, ease);
            saveEbisuState();

            // Get stats for debugging/display
            const stats = ebisuScheduler.getCardStats(currentCard.id);
            console.log(`Card ${currentCard.id} updated:`, {
                halfLife: `${stats.halfLife.toFixed(1)} hours`,
                nextReview: `${stats.nextReviewHours.toFixed(1)} hours`,
                recallProb: `${(stats.recallProbability * 100).toFixed(1)}%`,
                successRate: `${(stats.successRate * 100).toFixed(1)}%`
            });
        }

        try {
            await fetch(`${API_BASE_URL}/api/anki/answer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ card_id: currentCard.id, ease })
            });

            // Remove current card from queue and clear currentCard to trigger next fetch
            setQueue(prev => prev.slice(1));
            setCurrentCard(null);
        } catch {
            // Error submitting answer
        }
    };

    const handleCardClick = () => {
        if (!isFlipped) {
            setIsFlipped(true);
            audioManager.play('click');
        }
    };

    // Handle mode switch with confirmation if mid-session
    const handleModeSwitch = (newMode: StudyMode) => {
        if (totalStudied > 0) {
            if (!confirm('Switching modes will reset your current session. Continue?')) {
                return;
            }
        }
        setStudyMode(newMode);
        setTotalStudied(0);
        setCorrectCount(0);
        setCurrentCard(null);
        setQueue([]);
        setLoading(true);
    };

    // FIXED: Start new session handler
    const handleStartNewSession = () => {
        setTotalStudied(0);
        setCorrectCount(0);
        setCurrentCard(null);
        setQueue([]);
        setLoading(true);
        setRefetchTrigger(prev => prev + 1); // Trigger refetch
    };

    const progressPercent = sessionCards.length > 0 ? ((totalStudied / sessionCards.length) * 100) : 0;
    const accuracyPercent = totalStudied > 0 ? ((correctCount / totalStudied) * 100) : 0;

    if (error) return (
        <div className="anki-container">
            <div className="error-message">
                <div className="error-icon">⚠️</div>
                <h2>Connection Error</h2>
                <p>{error}</p>
            </div>
        </div>
    );

    if (loading && !currentCard) return (
        <div className="anki-container">
            <div className="loading-message">
                <div className="spinner"></div>
                <p>Loading cards...</p>
            </div>
        </div>
    );

    if (queue.length === 0 && !currentCard) {
        return (
            <div className="anki-container">
                <div className="completion-screen">
                    <div className="completion-icon">🎉</div>
                    <h1>Study Session Complete!</h1>
                    <div className="stats-summary">
                        <div className="stat-item">
                            <div className="stat-value">{totalStudied}</div>
                            <div className="stat-label">Cards Studied</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-value">{Math.round(accuracyPercent)}%</div>
                            <div className="stat-label">Accuracy</div>
                        </div>
                    </div>
                    {studyMode === 'smart' && (
                        <div className="smart-learn-summary">
                            <h3>🧠 Smart Learn Insights</h3>
                            <p>Your recall probabilities have been updated. The algorithm will show cards at optimal intervals next time.</p>
                        </div>
                    )}
                    <button className="retry-btn" onClick={handleStartNewSession}>
                        Start New Session
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="anki-container">
            {/* Mode Selector */}
            <div className="mode-selector">
                <button
                    className={`mode-btn ${studyMode === 'normal' ? 'active' : ''}`}
                    onClick={() => handleModeSwitch('normal')}
                >
                    📚 Normal Practice
                </button>
                <button
                    className={`mode-btn ${studyMode === 'smart' ? 'active' : ''}`}
                    onClick={() => handleModeSwitch('smart')}
                >
                    🧠 Smart Learn
                </button>
            </div>

            {/* Mode Description */}
            <div className="mode-description">
                {studyMode === 'smart' ? (
                    <p>🎯 <strong>Smart Learn</strong> uses the Ebisu algorithm to optimize review intervals based on your performance.</p>
                ) : (
                    <p>📖 <strong>Normal Practice</strong> shows all cards in sequence without adaptive scheduling.</p>
                )}
            </div>

            {/* Progress Bar */}
            <div className="progress-container">
                <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
                </div>
                <div className="progress-text">
                    {totalStudied} / {sessionCards.length} studied • {Math.round(accuracyPercent)}% accuracy
                </div>
            </div>

            {/* Flashcard */}
            {currentCard && (
                <div className="card-wrapper">
                    {streak >= 3 && (
                        <div className={`streak-badge ki-charge-${Math.min(streak, 10)}`}>
                            🔥 {streak}x Streak!
                        </div>
                    )}
                    <div
                        className={`flip-card ${isFlipped ? 'flipped' : ''} ${streak >= 3 ? `ki-charge-${Math.min(streak, 10)}` : ''}`}
                        onClick={handleCardClick}
                    >
                        <div className="flip-card-inner">
                            {/* Front */}
                            <div className="flip-card-front">
                                <div className="card-label">Question</div>
                                {/* Sanitize flashcard content to prevent XSS */}
                                <div
                                    className="card-content"
                                    dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(currentCard.question) }}
                                />
                                {!isFlipped && <div className="tap-hint">👆 Tap to reveal answer</div>}
                            </div>

                            {/* Back */}
                            <div className="flip-card-back">
                                <div className="card-label">Answer</div>
                                {/* Sanitize flashcard content to prevent XSS */}
                                <div
                                    className="card-content"
                                    dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(currentCard.answer) }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Answer Buttons - Only show when flipped */}
                    {isFlipped && (
                        <div className="answer-buttons">
                            <button className="ans-btn wrong" onClick={() => handleAnswer(1)}>
                                <span className="emoji">❌</span>
                                <span>Wrong</span>
                            </button>
                            <button className="ans-btn hard" onClick={() => handleAnswer(2)}>
                                <span className="emoji">😓</span>
                                <span>Hard</span>
                            </button>
                            <button className="ans-btn good" onClick={() => handleAnswer(3)}>
                                <span className="emoji">👍</span>
                                <span>Good</span>
                            </button>
                            <button className="ans-btn easy" onClick={() => handleAnswer(4)}>
                                <span className="emoji">✨</span>
                                <span>Easy</span>
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default AnkiDojo;