import React, { useState, useEffect } from 'react';
import './SocraticHistory.css';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

interface Dialogue {
    id: number;
    topic: string;
    dialogue: string;
    insight: string;
    created_at: string;
}

const SocraticHistory: React.FC = () => {
    const [history, setHistory] = useState<Dialogue[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDialogue, setSelectedDialogue] = useState<Dialogue | null>(null);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/socratic/history');
            const data = await response.json();
            if (data.success) {
                setHistory(data.data);
            }
        } catch (error) {
            console.error("Failed to fetch Socratic history", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="socratic-history-container">
            <h1 className="neon-text">🏛️ Socratic Archives</h1>

            <div className="socratic-layout">
                <div className="history-list glass-panel">
                    <h3>Past Dialogues</h3>
                    {loading ? (
                        <div>Loading archives...</div>
                    ) : (
                        <ul>
                            {history.map(item => (
                                <li
                                    key={item.id}
                                    className={`history-item ${selectedDialogue?.id === item.id ? 'active' : ''}`}
                                    onClick={() => setSelectedDialogue(item)}
                                >
                                    <div className="item-topic">{item.topic}</div>
                                    <div className="item-date">{new Date(item.created_at).toLocaleDateString()}</div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                <div className="dialogue-view glass-panel">
                    {selectedDialogue ? (
                        <>
                            <h2>{selectedDialogue.topic}</h2>
                            <div className="dialogue-content">
                                <MarkdownRenderer content={selectedDialogue.dialogue} />
                            </div>
                            {selectedDialogue.insight && (
                                <div className="insight-box">
                                    <strong>💡 Key Insight:</strong> {selectedDialogue.insight}
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="placeholder-text">
                            Select a dialogue from the archives to review the wisdom of the ancients.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SocraticHistory;
