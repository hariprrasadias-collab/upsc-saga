import React, { useState, useEffect, useMemo, useRef } from 'react';
import './SocraticHistory.css';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

interface Dialogue {
    id: number;
    topic: string;
    dialogue: string;
    insight: string;
    created_at: string;
}

interface Verdict {
    winner: string;
    key_concepts: string[];
    synthesis: string;
    best_quote: string;
    mental_models?: string[];
}

interface Turn {
    speakerId: string;
    text: string;
    type: string;
    technique?: string;
    timestamp: number;
}

const AGENTS: Record<string, { name: string, icon: string, voice: string }> = {
    'skeptic': { name: 'Socrates', icon: '🤔', voice: 'Google US English Male' },
    'idealist': { name: 'Plato', icon: '✨', voice: 'Google UK English Female' },
    'realist': { name: 'Aristotle', icon: '📜', voice: 'Google UK English Male' },
    'iconoclast': { name: 'Nietzsche', icon: '⚡', voice: 'Google Deutsch Male' }, // Fallback logic needed
    'sage': { name: 'Confucius', icon: '🎍', voice: 'Google UK English Male' },
    'strategist': { name: 'Machiavelli', icon: '♟️', voice: 'Google US English Male' }
};

const SocraticHistory: React.FC = () => {
    const [history, setHistory] = useState<Dialogue[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDialogue, setSelectedDialogue] = useState<Dialogue | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Playback State
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTurnIndex, setCurrentTurnIndex] = useState(-1);
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

    useEffect(() => {
        fetchHistory();
        return () => {
            stopPlayback();
        };
    }, []);

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
        if (!selectedDialogue) return;
        const text = typeof parsedDialogue === 'string'
            ? parsedDialogue
            : parsedDialogue.map(t => `${AGENTS[t.speakerId]?.name || 'Unknown'}: ${t.text}`).join('\n\n');

        navigator.clipboard.writeText(text);
        alert("Dialogue copied to clipboard!");
    };

    const handleDownload = () => {
        if (!selectedDialogue) return;

        const text = typeof parsedDialogue === 'string'
            ? parsedDialogue
            : parsedDialogue.map(t => `${AGENTS[t.speakerId]?.name || 'Unknown'}: ${t.text}`).join('\n\n');

        const element = document.createElement("a");
        const file = new Blob([text], {type: 'text/plain'});
        element.href = URL.createObjectURL(file);
        element.download = `Socratic_Debate_${selectedDialogue.topic.replace(/\s+/g, '_')}.md`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    // Helper to parse content
    const getVerdict = (jsonStr: string): Verdict | null => {
        try {
            return JSON.parse(jsonStr);
        } catch {
            return null;
        }
    };

    const parsedDialogue: Turn[] | string = useMemo(() => {
        if (!selectedDialogue) return "";
        try {
            // Check if it's JSON array
            const parsed = JSON.parse(selectedDialogue.dialogue);
            if (Array.isArray(parsed)) return parsed;
            return selectedDialogue.dialogue;
        } catch {
            return selectedDialogue.dialogue;
        }
    }, [selectedDialogue]);

    const selectedVerdict = selectedDialogue ? getVerdict(selectedDialogue.insight) : null;

    // --- TTS Logic ---

    const stopPlayback = () => {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
        setCurrentTurnIndex(-1);
    };

    const speakTurn = (index: number) => {
        if (typeof parsedDialogue === 'string') return;
        if (index >= parsedDialogue.length) {
            stopPlayback();
            return;
        }

        const turn = parsedDialogue[index];
        setCurrentTurnIndex(index);

        const text = turn.text;
        const speaker = AGENTS[turn.speakerId];

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;

        // Voice Selection
        const voices = window.speechSynthesis.getVoices();
        // Try to match specific voice, fallback to gender
        // Note: Voice names vary by OS/Browser. This is a best-effort heuristic.
        const voiceName = speaker?.voice || '';
        const selectedVoice = voices.find(v => v.name.includes(voiceName)) ||
                              voices.find(v => v.lang.startsWith('en'));

        if (selectedVoice) utterance.voice = selectedVoice;

        utterance.onend = () => {
            speakTurn(index + 1);
        };

        utteranceRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    };

    const togglePlay = () => {
        if (isPlaying) {
            stopPlayback();
        } else {
            if (typeof parsedDialogue !== 'string') {
                setIsPlaying(true);
                speakTurn(0);
            }
        }
    };

    const createFlashcard = async (front: string, back: string) => {
        if (!confirm("Create Flashcard from this insight?")) return;
        try {
            await fetch('http://localhost:5000/api/flashcards', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    deck_id: 1, // Default deck for now, logic could be improved
                    front: front,
                    back: back,
                    source: 'socratic_archive'
                })
            });
            alert("Flashcard Created!");
        } catch (e) {
            alert("Failed to create flashcard.");
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
                                    onClick={() => {
                                        stopPlayback();
                                        setSelectedDialogue(item);
                                    }}
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
                            <div className="view-header">
                                <h2>{selectedDialogue.topic}</h2>
                                <div className="action-buttons">
                                    {Array.isArray(parsedDialogue) && (
                                        <button
                                            className={`play-btn ${isPlaying ? 'playing' : ''}`}
                                            onClick={togglePlay}
                                            title={isPlaying ? "Stop Debate" : "Listen to Debate"}
                                        >
                                            {isPlaying ? "⏹️ Stop" : "▶️ Listen"}
                                        </button>
                                    )}
                                    <button className="copy-btn" onClick={handleDownload} title="Download">
                                        📥
                                    </button>
                                    <button className="copy-btn" onClick={handleCopy} title="Copy">
                                        📋
                                    </button>
                                </div>
                            </div>

                            {/* Verdict Card */}
                            {selectedVerdict && (
                                <div className="verdict-card">
                                    <div className="verdict-header">
                                        <h3>⚖️ Athena's Judgment</h3>
                                        <button
                                            className="card-add-btn"
                                            onClick={() => createFlashcard(`Socratic Verdict: ${selectedDialogue.topic}`, selectedVerdict.synthesis)}
                                            title="Save Verdict as Flashcard"
                                        >
                                            ⚡
                                        </button>
                                    </div>
                                    <div className="winner-row">
                                        <span className="winner-badge">🏆 Winner: {selectedVerdict.winner}</span>
                                    </div>

                                    <p className="verdict-synthesis">{selectedVerdict.synthesis}</p>

                                    <div className="verdict-tags">
                                        {selectedVerdict.key_concepts?.map((tag, idx) => (
                                            <span key={idx} className="concept-tag">{tag}</span>
                                        ))}
                                    </div>

                                    {selectedVerdict.mental_models && (
                                        <div className="mental-models">
                                            <strong>🧠 Mental Models:</strong> {selectedVerdict.mental_models.join(', ')}
                                        </div>
                                    )}

                                    {selectedVerdict.best_quote && (
                                        <div className="best-quote">
                                            " {selectedVerdict.best_quote} "
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="dialogue-content custom-scrollbar">
                                {Array.isArray(parsedDialogue) ? (
                                    <div className="script-view">
                                        {parsedDialogue.map((turn, idx) => (
                                            <div
                                                key={idx}
                                                className={`script-turn ${currentTurnIndex === idx ? 'speaking' : ''}`}
                                            >
                                                <div className="turn-avatar">
                                                    {AGENTS[turn.speakerId]?.icon || '👤'}
                                                </div>
                                                <div className="turn-body">
                                                    <div className="turn-meta">
                                                        <span className="turn-speaker">{AGENTS[turn.speakerId]?.name || 'Unknown'}</span>
                                                        {turn.technique && (
                                                            <span className="turn-technique">Using: {turn.technique}</span>
                                                        )}
                                                        <button
                                                            className="mini-card-btn"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                createFlashcard(`${AGENTS[turn.speakerId]?.name} on ${selectedDialogue.topic}`, turn.text);
                                                            }}
                                                            title="Save as Flashcard"
                                                        >
                                                            ⚡
                                                        </button>
                                                    </div>
                                                    <div className="turn-text">{turn.text}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <MarkdownRenderer content={parsedDialogue} />
                                )}
                            </div>
                        </>
                    ) : (
                        <div className="placeholder-text">
                            <div className="placeholder-icon">📜</div>
                            Select a dialogue to review the wisdom of the ancients.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SocraticHistory;
