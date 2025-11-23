// FlashcardStats - Analytics dashboard for review performance
import React, { useState, useEffect } from 'react';
import './Flashcards.css';

interface Analytics {
    total_cards: number;
    new: number;
    learning: number;
    young: number;
    mature: number;
    mastered: number;
    daily_streak: number;
    total_reviews: number;
}

const FlashcardStats: React.FC = () => {
    const [analytics, setAnalytics] = useState<Analytics | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAnalytics();
    }, []);

    const fetchAnalytics = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/flashcards/analytics');
            const data = await res.json();
            setAnalytics(data);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch analytics:', err);
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">Loading statistics...</div>;
    if (!analytics) return <div>No data available</div>;

    return (
        <div className="flashcard-stats">
            <h2>📊 Review Statistics</h2>

            {/* Overview Cards */}
            <div className="stats-overview">
                <div className="stat-card">
                    <div className="stat-value">{analytics.total_cards}</div>
                    <div className="stat-label">Total Cards</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{analytics.total_reviews}</div>
                    <div className="stat-label">Total Reviews</div>
                </div>
                <div className="stat-card streak">
                    <div className="stat-value">🔥 {analytics.daily_streak}</div>
                    <div className="stat-label">Day Streak</div>
                </div>
            </div>

            {/* Card Maturity Distribution */}
            <div className="maturity-section">
                <h3>Card Maturity</h3>
                <div className="maturity-bars">
                    <div className="maturity-bar">
                        <span className="maturity-label">New</span>
                        <div className="bar-container">
                            <div
                                className="bar-fill new"
                                style={{ width: `${(analytics.new / analytics.total_cards) * 100}%` }}
                            />
                        </div>
                        <span className="maturity-count">{analytics.new}</span>
                    </div>
                    <div className="maturity-bar">
                        <span className="maturity-label">Learning</span>
                        <div className="bar-container">
                            <div
                                className="bar-fill learning"
                                style={{ width: `${(analytics.learning / analytics.total_cards) * 100}%` }}
                            />
                        </div>
                        <span className="maturity-count">{analytics.learning}</span>
                    </div>
                    <div className="maturity-bar">
                        <span className="maturity-label">Young</span>
                        <div className="bar-container">
                            <div
                                className="bar-fill young"
                                style={{ width: `${(analytics.young / analytics.total_cards) * 100}%` }}
                            />
                        </div>
                        <span className="maturity-count">{analytics.young}</span>
                    </div>
                    <div className="maturity-bar">
                        <span className="maturity-label">Mature</span>
                        <div className="bar-container">
                            <div
                                className="bar-fill mature"
                                style={{ width: `${(analytics.mature / analytics.total_cards) * 100}%` }}
                            />
                        </div>
                        <span className="maturity-count">{analytics.mature}</span>
                    </div>
                    <div className="maturity-bar">
                        <span className="maturity-label">Mastered</span>
                        <div className="bar-container">
                            <div
                                className="bar-fill mastered"
                                style={{ width: `${(analytics.mastered / analytics.total_cards) * 100}%` }}
                            />
                        </div>
                        <span className="maturity-count">{analytics.mastered}</span>
                    </div>
                </div>
            </div>

            {/* Tips */}
            <div className="stats-tips">
                <h3>💡 Tips</h3>
                <ul>
                    <li>Review cards daily to maintain your streak!</li>
                    <li>Use "Again" for cards you completely forgot</li>
                    <li>"Hard" when you struggled but got it</li>
                    <li>"Good" for correct recall</li>
                    <li>"Easy" for instant, perfect recall</li>
                </ul>
            </div>
        </div>
    );
};

export default FlashcardStats;
