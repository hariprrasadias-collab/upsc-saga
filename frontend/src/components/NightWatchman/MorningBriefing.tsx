import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './MorningBriefing.css';

interface Briefing {
    id: number;
    date: string;
    summary: string;
    quote: string;
    articles_analyzed: number;
    is_read: boolean;
}

const MorningBriefing: React.FC = () => {
    const [briefing, setBriefing] = useState<Briefing | null>(null);
    const [loading, setLoading] = useState(false);
    const [triggering, setTriggering] = useState(false);

    useEffect(() => {
        fetchLatestBriefing();
    }, []);

    const fetchLatestBriefing = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/watchman/briefing/latest');
            const data = await response.json();
            if (data.success) {
                setBriefing(data.briefing);
            } else {
                setBriefing(null);
            }
        } catch (error) {
            console.error('Failed to fetch briefing:', error);
        } finally {
            setLoading(false);
        }
    };

    const triggerWatchman = async () => {
        setTriggering(true);
        try {
            const response = await fetch('http://localhost:5000/api/watchman/trigger', {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                fetchLatestBriefing();
            }
        } catch (error) {
            console.error('Failed to trigger watchman:', error);
        } finally {
            setTriggering(false);
        }
    };

    const markAsRead = async () => {
        if (!briefing) return;
        try {
            await fetch(`http://localhost:5000/api/watchman/briefing/${briefing.id}/read`, {
                method: 'POST'
            });
            // Optimistically update
            setBriefing({ ...briefing, is_read: true });
        } catch (error) {
            console.error('Failed to mark as read:', error);
        }
    };

    return (
        <div className="morning-briefing-container">
            <div className="briefing-header">
                <h1>🦉 The Night Watchman</h1>
                <p className="subtitle">Autonomous Research & Intelligence Briefing</p>
            </div>

            {loading ? (
                <div className="loading-state">
                    <div className="owl-loader"></div>
                    <p>Retrieving Intelligence...</p>
                </div>
            ) : briefing ? (
                <div className={`briefing-content ${briefing.is_read ? 'read' : 'unread'}`}>
                    <div className="briefing-meta">
                        <span className="date-badge">📅 {briefing.date}</span>
                        <span className="source-badge">📡 {briefing.articles_analyzed} Sources Analyzed</span>
                    </div>

                    <div className="quote-section">
                        <blockquote>"{briefing.quote}"</blockquote>
                    </div>

                    <div className="markdown-content">
                        <ReactMarkdown>{briefing.summary}</ReactMarkdown>
                    </div>

                    <div className="briefing-actions">
                        {!briefing.is_read && (
                            <button className="action-btn primary" onClick={markAsRead}>
                                ✅ Mark as Read
                            </button>
                        )}
                        <button className="action-btn secondary" onClick={triggerWatchman} disabled={triggering}>
                            {triggering ? '🔄 Scouting...' : '🔄 Refresh Intelligence'}
                        </button>
                    </div>
                </div>
            ) : (
                <div className="empty-state">
                    <div className="owl-icon">🦉</div>
                    <h3>No Briefing Available</h3>
                    <p>The Night Watchman hasn't filed a report for today yet.</p>
                    <button className="trigger-btn" onClick={triggerWatchman} disabled={triggering}>
                        {triggering ? '🦅 Scouting Sector...' : '🦅 Dispatch Watchman'}
                    </button>
                </div>
            )}
        </div>
    );
};

export default MorningBriefing;
