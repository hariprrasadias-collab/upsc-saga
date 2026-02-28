import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import './RevisionCenter.css';
import { audioManager } from '../../util/AudioManager';

interface RevisionItem {
    id: number;
    item_type: string;
    item_id: number;
    next_review: string;
    interval: number;
    content?: any; // To store fetched content details
}

const RevisionCenter: React.FC = () => {
    const [dueItems, setDueItems] = useState<RevisionItem[]>([]);
    const [currentItem, setCurrentItem] = useState<RevisionItem | null>(null);
    const [loading, setLoading] = useState(true);
    const [showAnswer, setShowAnswer] = useState(false);

    useEffect(() => {
        fetchDueItems();
    }, []);

    const fetchDueItems = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/scheduler/due`);
            if (res.ok) {
                const data = await res.json();
                setDueItems(data);
                if (data.length > 0) {
                    setCurrentItem(data[0]);
                }
            }
        } catch (err) {
            console.error("Failed to fetch due items:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleRating = async (rating: number) => {
        if (!currentItem) return;

        try {
            const res = await fetch(`${API_BASE_URL}/api/scheduler/review`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    item_type: currentItem.item_type,
                    item_id: currentItem.item_id,
                    rating: rating
                })
            });

            if (res.ok) {
                audioManager.play(rating >= 3 ? 'success' : 'click');

                // Remove current item and move to next
                const remaining = dueItems.filter(i => i.id !== currentItem.id);
                setDueItems(remaining);
                setCurrentItem(remaining.length > 0 ? remaining[0] : null);
                setShowAnswer(false);
            }
        } catch (err) {
            console.error("Failed to submit review:", err);
        }
    };

    if (loading) return <div className="revision-loading">Loading your daily reviews...</div>;

    if (!currentItem) {
        return (
            <div className="revision-center empty">
                <div className="empty-content">
                    <h1>🎉 All Caught Up!</h1>
                    <p>You have no more items due for revision today.</p>
                    <button className="refresh-btn" onClick={fetchDueItems}>Check Again</button>
                </div>
            </div>
        );
    }

    return (
        <div className="revision-center">
            <div className="revision-header">
                <h1>🧠 Revision Center</h1>
                <span className="due-count">{dueItems.length} items due</span>
            </div>

            <div className="card-container">
                <div className="revision-card">
                    <div className="card-type">{currentItem.item_type.toUpperCase()}</div>

                    <div className="card-front">
                        <h3>Item ID: {currentItem.item_id}</h3>
                        <p>Content placeholder for {currentItem.item_type} #{currentItem.item_id}</p>
                        {/* In a real app, we would fetch and display the actual content here */}
                    </div>

                    {showAnswer && (
                        <div className="card-back">
                            <p>Answer/Details would appear here...</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="controls">
                {!showAnswer ? (
                    <button className="show-answer-btn" onClick={() => setShowAnswer(true)}>
                        Show Answer
                    </button>
                ) : (
                    <div className="rating-buttons">
                        <button className="rate-btn again" onClick={() => handleRating(1)}>
                            Again (1)
                            <span className="interval-preview">&lt; 10m</span>
                        </button>
                        <button className="rate-btn hard" onClick={() => handleRating(2)}>
                            Hard (2)
                            <span className="interval-preview">2d</span>
                        </button>
                        <button className="rate-btn good" onClick={() => handleRating(3)}>
                            Good (3)
                            <span className="interval-preview">4d</span>
                        </button>
                        <button className="rate-btn easy" onClick={() => handleRating(4)}>
                            Easy (4)
                            <span className="interval-preview">7d</span>
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RevisionCenter;
