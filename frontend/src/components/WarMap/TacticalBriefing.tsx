import React, { useState, useEffect } from 'react';
import './TacticalBriefing.css';
import { API_BASE_URL } from '../../config';

interface Briefing {
    title: string;
    directive: string;
    primary_target: string;
    threat_level: string;
    tactical_breakdown: string[];
    quote: string;
}

const TacticalBriefing: React.FC<{ refreshTrigger: number, dayTasks: any[], csvTasks: any[] }> = ({ refreshTrigger, dayTasks, csvTasks }) => {
    const [briefing, setBriefing] = useState<Briefing | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBriefing = async () => {
            // Avoid fetching if tasks aren't loaded yet
            if (dayTasks.length === 0 && csvTasks.length === 0 && refreshTrigger === 0) return;

            setLoading(true);
            try {
                // Construct context from current tasks
                const tasksContext = [...csvTasks, ...dayTasks].map(t =>
                    'subject' in t ? `${t.subject}: ${t.activity} (${t.status})` : `${t.title} (${t.isCompleted ? 'Done' : 'Pending'})`
                ).join('\n');

                const response = await fetch(`${API_BASE_URL}/api/planner/tactical-brief`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        date: new Date().toISOString().split('T')[0],
                        context: tasksContext
                    })
                });
                const data = await response.json();
                const briefPayload = data.brief || (data.data && data.data.brief);
                if (data.success && briefPayload) {
                    setBriefing(briefPayload);
                }
            } catch (error) {
                console.error("Failed to load tactical briefing", error);
            } finally {
                setLoading(false);
            }
        };

        fetchBriefing();
    }, [refreshTrigger, dayTasks, csvTasks]);

    if (loading) {
        return (
            <div className="briefing-panel loading-scan">
                <div className="scanner"></div>
                <p>HYDRA UPLINK: DECRYPTING MORNING BRIEF...</p>
            </div>
        );
    }

    if (!briefing) {
        return (
            <div className="briefing-panel error-mode">
                <h3>CONNECTION LOST</h3>
                <p>Commander, the Oracle is unreachable. Proceed with standard operating procedures.</p>
            </div>
        );
    }

    const threatColor = briefing.threat_level === 'CRITICAL' ? '#ff3b30'
        : briefing.threat_level === 'ELEVATED' ? '#ffcc00'
            : '#34c759';

    return (
        <div className="briefing-panel">
            <header className="briefing-header">
                <h2 className="operation-title glitch" data-text={briefing.title}>{briefing.title}</h2>
                <div className="threat-badge" style={{ borderColor: threatColor, color: threatColor }}>
                    THREAT: {briefing.threat_level}
                </div>
            </header>

            <section className="directive-section">
                <h4>DIRECTIVE</h4>
                <p>{briefing.directive}</p>
            </section>

            <section className="target-section">
                <h4>PRIMARY TARGET</h4>
                <div className="target-box">{briefing.primary_target}</div>
            </section>

            <section className="breakdown-section">
                <h4>TACTICAL BREAKDOWN</h4>
                <ul>
                    {briefing.tactical_breakdown.map((item, idx) => (
                        <li key={idx}>
                            <span className="bullet-icon">➤</span> {item}
                        </li>
                    ))}
                </ul>
            </section>

            <footer className="quote-footer">
                <p>"{briefing.quote}"</p>
            </footer>
        </div>
    );
};

export default TacticalBriefing;
