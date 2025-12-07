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
    const [filteredHistory, setFilteredHistory] = useState<Dialogue[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDialogue, setSelectedDialogue] = useState<Dialogue | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchHistory();
    }, []);

    useEffect(() => {
        if (searchTerm.trim() === '') {
            setFilteredHistory(history);
        } else {
            const lowerTerm = searchTerm.toLowerCase();
            const filtered = history.filter(item =>
                item.topic.toLowerCase().includes(lowerTerm) ||
                item.dialogue.toLowerCase().includes(lowerTerm)
            );
            setFilteredHistory(filtered);
        }
    }, [searchTerm, history]);

    const fetchHistory = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/socratic/history');
            const data = await response.json();
            if (data.success) {
                setHistory(data.data);
                setFilteredHistory(data.data);
            }
        } catch (error) {
            console.error("Failed to fetch Socratic history", error);
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = () => {
        if (selectedDialogue) {
            navigator.clipboard.writeText(selectedDialogue.dialogue);
            // Optionally add a toast notification here
            alert("Dialogue copied to clipboard!");
        }
    };

    return (
        <div className="socratic-history-container">
            <div className="history-header">
                <h1 className="neon-text">🏛️ Socratic Archives</h1>
                <div className="search-bar">
                    <input
                        type="text"
                        placeholder="Search archives..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <span className="search-icon">🔍</span>
                </div>
            </div>

            <div className="socratic-layout">
                <div className="history-list glass-panel">
                    <h3>Past Dialogues ({filteredHistory.length})</h3>
                    {loading ? (
                        <div className="loading-spinner">Loading archives...</div>
                    ) : (
                        <ul>
                            {filteredHistory.map(item => (
                                <li
                                    key={item.id}
                                    className={`history-item ${selectedDialogue?.id === item.id ? 'active' : ''}`}
                                    onClick={() => setSelectedDialogue(item)}
                                >
                                    <div className="item-topic">{item.topic}</div>
                                    <div className="item-date">{new Date(item.created_at).toLocaleDateString()}</div>
                                    <div className="item-preview">
                                        {item.dialogue.substring(0, 50)}...
                                    </div>
                                </li>
                            ))}
                            {filteredHistory.length === 0 && !loading && (
                                <div className="no-results">No dialogues found.</div>
                            )}
                        </ul>
                    )}
                </div>

                <div className="dialogue-view glass-panel">
                    {selectedDialogue ? (
                        <>
                            <div className="view-header">
                                <h2>{selectedDialogue.topic}</h2>
                                <button className="copy-btn" onClick={handleCopy} title="Copy to Clipboard">
                                    📋 Copy
                                </button>
                            </div>
                            <div className="dialogue-content custom-scrollbar">
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
                            <div className="placeholder-icon">📜</div>
                            Select a dialogue from the archives to review the wisdom of the ancients.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SocraticHistory;
