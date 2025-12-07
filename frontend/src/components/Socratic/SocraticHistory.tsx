import React, { useState, useEffect, useMemo } from 'react';
import './SocraticHistory.css';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

interface Dialogue {
    id: number;
    topic: string;
    dialogue: string;
    insight: string; // This is now a JSON string containing the verdict
    created_at: string;
}

interface Verdict {
    winner: string;
    key_concepts: string[];
    synthesis: string;
    best_quote: string;
}

const SocraticHistory: React.FC = () => {
    const [history, setHistory] = useState<Dialogue[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDialogue, setSelectedDialogue] = useState<Dialogue | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchHistory();
    }, []);

    // Optimized filtering with useMemo
    const filteredHistory = useMemo(() => {
        if (searchTerm.trim() === '') return history;
        const lowerTerm = searchTerm.toLowerCase();
        return history.filter(item =>
            item.topic.toLowerCase().includes(lowerTerm) ||
            item.dialogue.toLowerCase().includes(lowerTerm)
        );
    }, [searchTerm, history]);

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

    const handleCopy = () => {
        if (selectedDialogue) {
            navigator.clipboard.writeText(selectedDialogue.dialogue);
            alert("Dialogue copied to clipboard!");
        }
    };

    const handleDownload = () => {
        if (!selectedDialogue) return;

        const element = document.createElement("a");
        const file = new Blob([selectedDialogue.dialogue], {type: 'text/plain'});
        element.href = URL.createObjectURL(file);
        element.download = `Socratic_Debate_${selectedDialogue.topic.replace(/\s+/g, '_')}.md`;
        document.body.appendChild(element); // Required for this to work in FireFox
        element.click();
        document.body.removeChild(element);
    };

    // Helper to parse the insight/verdict
    const getVerdict = (jsonStr: string): Verdict | null => {
        try {
            return JSON.parse(jsonStr);
        } catch {
            return null;
        }
    };

    const selectedVerdict = selectedDialogue ? getVerdict(selectedDialogue.insight) : null;

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
                                <div className="action-buttons">
                                    <button className="copy-btn" onClick={handleDownload} title="Download Transcript">
                                        📥 Download
                                    </button>
                                    <button className="copy-btn" onClick={handleCopy} title="Copy to Clipboard">
                                        📋 Copy
                                    </button>
                                </div>
                            </div>

                            {/* Verdict Card */}
                            {selectedVerdict && (
                                <div className="verdict-card">
                                    <div className="verdict-header">
                                        <h3>⚖️ Athena's Judgment</h3>
                                        <span className="winner-badge">🏆 Winner: {selectedVerdict.winner}</span>
                                    </div>
                                    <p className="verdict-synthesis">{selectedVerdict.synthesis}</p>
                                    <div className="verdict-tags">
                                        {selectedVerdict.key_concepts?.map((tag, idx) => (
                                            <span key={idx} className="concept-tag">{tag}</span>
                                        ))}
                                    </div>
                                    {selectedVerdict.best_quote && (
                                        <div className="best-quote">
                                            " {selectedVerdict.best_quote} "
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Legacy Insight Fallback */}
                            {!selectedVerdict && selectedDialogue.insight && (
                                <div className="insight-box">
                                    <strong>💡 Key Insight:</strong> {selectedDialogue.insight}
                                </div>
                            )}

                            <div className="dialogue-content custom-scrollbar">
                                <MarkdownRenderer content={selectedDialogue.dialogue} />
                            </div>
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
