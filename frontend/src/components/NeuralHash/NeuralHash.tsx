import React, { useState, useEffect } from 'react';
import './NeuralHash.css';
import { FaBrain, FaHistory, FaBolt, FaLayerGroup, FaExclamationTriangle, FaDatabase, FaPlus } from 'react-icons/fa';
import { brainService } from '../../services/BrainService';
import MarkdownRenderer from '../Shared/MarkdownRenderer';

interface DecodedData {
    core_themes: string[];
    high_yield_keywords: string[];
    examiner_pattern: string;
    potential_questions: { type: string; question: string }[];
    complexity_score: number;
    relevance_score: number;
    cross_linkages?: string[];
    prelims_traps?: string[];
    data_points?: string[];
}

interface HistoryItem {
    id: number;
    input_text_preview: string;
    context_type: string;
    decoded_data: DecodedData;
    created_at: string;
}

const NeuralHash: React.FC = () => {
    const [inputText, setInputText] = useState('');
    const [contextType, setContextType] = useState('general');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<DecodedData | null>(null);
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [showHistory, setShowHistory] = useState(false);
    const [loadingText, setLoadingText] = useState('> INITIALIZING NEURAL PATHWAYS...');
    const [toast, setToast] = useState<{ msg: string, type: 'success' | 'error' } | null>(null);

    useEffect(() => {
        fetchHistory();
    }, []);

    // Dynamic Loading Effect
    useEffect(() => {
        if (!loading) return;

        const texts = [
            '> ACCESSING NEURAL PATHWAYS...',
            '> ANALYZING EXAMINER PSYCHE...',
            '> DECODING HIDDEN PATTERNS...',
            '> EXTRACTING HIGH-YIELD ARTIFACTS...',
            '> SYNTHESIZING INTELLIGENCE...'
        ];

        let i = 0;
        const interval = setInterval(() => {
            setLoadingText(texts[i % texts.length]);
            i++;
        }, 800);

        return () => clearInterval(interval);
    }, [loading]);

    // Keyboard Shortcut
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.key === 'Enter') {
                handleDecode();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [inputText, contextType]); // Dependencies for handleDecode

    // Toast Timer
    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => setToast(null), 3000);
            return () => clearTimeout(timer);
        }
    }, [toast]);

    const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
        setToast({ msg, type });
    };

    const fetchHistory = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/neural_hash/history');
            const data = await response.json();
            if (data.success) {
                setHistory(data.history);
            }
        } catch (error) {
            console.error("Failed to fetch history", error);
        }
    };

    const loadHistoryItem = (item: HistoryItem) => {
        setResult(item.decoded_data);
        setInputText(item.input_text_preview);
        setContextType(item.context_type);
        setShowHistory(false);
    };

    const handleDecode = async () => {
        if (!inputText.trim()) return;

        setLoading(true);
        try {
            const payload = { text: inputText, type: contextType };
            const result = await brainService.executeAction('DECODE_NEURAL_HASH', payload);

            if (result.success) {
                setResult(result.data);
                // Optionally save to history backend if needed, or rely on Brain logs
                // For now, we'll just show the result
                showToast('Patterns Decoded Successfully');
            } else {
                showToast('Decoding failed: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Decode error:', error);
            showToast('Failed to connect to the Neural Hash.', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateFlashcard = async (keyword: string) => {
        try {
            const response = await fetch('http://localhost:5000/api/flashcards', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    deck_id: 1, // Default deck for now
                    front: keyword,
                    back: `Define/Explain: ${keyword} in the context of ${contextType}`,
                    tags: ['neural-hash', contextType]
                })
            });
            if (response.ok) {
                showToast(`Flashcard created: ${keyword}`);
            }
        } catch (error) {
            console.error('Flashcard error:', error);
            showToast('Failed to create flashcard', 'error');
        }
    };

    const handleCreateTask = async (question: string) => {
        try {
            const response = await fetch('http://localhost:5000/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: `Answer: ${question.substring(0, 50)}...`,
                    xp_reward: 50,
                    due_date: new Date().toISOString().split('T')[0]
                })
            });
            if (response.ok) {
                showToast('Task added to WarMap');
            }
        } catch (error) {
            console.error('Task error:', error);
            showToast('Failed to add task', 'error');
        }
    };

    const handleCopy = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        showToast(`${label} Copied to Clipboard`);
    };

    return (
        <div className="neural-hash-container">
            {toast && (
                <div className={`cyber-toast ${toast.type}`}>
                    {toast.type === 'success' ? <FaBolt /> : <FaExclamationTriangle />}
                    {toast.msg}
                </div>
            )}

            <div className="decoder-header">
                <h1>The Neural Hash</h1>
                <div className="subtitle">PATTERN RECOGNITION & DECODING ENGINE</div>
                <button
                    className="history-toggle-btn neon-border-blue"
                    onClick={() => setShowHistory(!showHistory)}
                    style={{
                        position: 'absolute',
                        right: 0,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'transparent',
                        color: 'var(--color-accent-blue)',
                        padding: '0.5rem 1rem',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}
                >
                    <FaHistory /> History
                </button>
            </div>

            {showHistory ? (
                <div className="history-panel glass-panel">
                    <h2 className="neon-text-blue" style={{ marginBottom: '1rem' }}>Decryption Logs</h2>
                    {history.map(item => (
                        <div key={item.id} className="history-item" onClick={() => loadHistoryItem(item)}>
                            <div className="history-preview">
                                <strong>[{item.context_type.toUpperCase()}]</strong> {item.input_text_preview}
                            </div>
                            <div className="history-meta">
                                {new Date(item.created_at).toLocaleDateString()}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <>
                    <div className="input-section glass-panel">
                        <div className="context-selector">
                            {['general', 'pyq', 'editorial', 'syllabus', 'answer'].map(type => (
                                <button
                                    key={type}
                                    className={`context-btn ${contextType === type ? 'active' : ''}`}
                                    onClick={() => setContextType(type)}
                                >
                                    {type.toUpperCase()}
                                </button>
                            ))}
                        </div>

                        <textarea
                            className="hash-input"
                            placeholder="PASTE TEXT DATA HERE FOR DECODING... (CTRL+ENTER TO DECODE)"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                        />

                        <button
                            className="decode-btn neon-border-blue"
                            onClick={handleDecode}
                            disabled={loading || !inputText}
                        >
                            {loading ? 'DECODING PATTERNS...' : 'INITIATE DECODE SEQUENCE'}
                        </button>
                    </div>

                    {loading && (
                        <div className="loading-matrix neon-text-blue">
                            {loadingText}
                        </div>
                    )}

                    {result && (
                        <div className="results-container">
                            <div className="left-panel">
                                <div className="result-card glass-panel">
                                    <h3 className="neon-text-blue"><FaBrain /> Core Themes (The Soul)</h3>
                                    <div className="themes-list">
                                        {result.core_themes.map((theme, i) => (
                                            <span key={i} className="theme-tag">{theme}</span>
                                        ))}
                                    </div>
                                </div>

                                <div className="result-card glass-panel" style={{ marginTop: '2rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                        <h3 className="neon-text-blue" style={{ margin: 0 }}><FaBrain /> Examiner's Pattern</h3>
                                        <button
                                            onClick={() => handleCopy(result.examiner_pattern, "Pattern")}
                                            style={{
                                                background: 'rgba(255,255,255,0.1)',
                                                border: 'none',
                                                color: 'var(--color-text-primary)',
                                                cursor: 'pointer',
                                                padding: '0.2rem 0.6rem',
                                                borderRadius: '4px',
                                                fontSize: '0.7rem'
                                            }}
                                        >
                                            COPY
                                        </button>
                                    </div>
                                    <MarkdownRenderer content={result.examiner_pattern} className="pattern-text" />
                                </div>

                                {result.cross_linkages && (
                                    <div className="result-card glass-panel" style={{ marginTop: '2rem' }}>
                                        <h3 className="neon-text-blue"><FaLayerGroup /> Cross Linkages</h3>
                                        <ul className="cross-links-list" style={{ listStyle: 'none', padding: 0 }}>
                                            {result.cross_linkages.map((link, i) => (
                                                <li key={i}>{link}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                <div className="result-card glass-panel" style={{ marginTop: '2rem' }}>
                                    <h3 className="neon-text-blue">Potential Derivatives</h3>
                                    {result.potential_questions.map((q, i) => (
                                        <div key={i} className="question-item">
                                            <span className="q-type">{q.type}</span>
                                            <div className="q-text">{q.question}</div>
                                            <button
                                                className="add-task-btn"
                                                title="Add to WarMap"
                                                onClick={() => handleCreateTask(q.question)}
                                            >
                                                <FaPlus />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="right-panel">
                                <div className="result-card glass-panel">
                                    <h3 className="neon-text-blue">Metrics</h3>
                                    <div className="score-display">
                                        <div className={`score-circle ${result.relevance_score > 7 ? 'high' : 'low'}`}>
                                            {result.relevance_score}
                                        </div>
                                        <div className="score-label">Relevance Score</div>
                                    </div>
                                    <div className="score-display">
                                        <div className="score-circle med" style={{ width: '80px', height: '80px', fontSize: '2rem', borderColor: '#888', color: '#888' }}>
                                            {result.complexity_score}
                                        </div>
                                        <div className="score-label">Complexity</div>
                                    </div>
                                </div>

                                <div className="result-card glass-panel" style={{ marginTop: '2rem' }}>
                                    <h3 className="neon-text-blue"><FaBolt /> High Yield Keywords</h3>
                                    <div className="keywords-list">
                                        {result.high_yield_keywords.map((kw, i) => (
                                            <span
                                                key={i}
                                                className="keyword-tag"
                                                onClick={() => handleCreateFlashcard(kw)}
                                                title="Click to create Flashcard"
                                            >
                                                {kw}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {result.prelims_traps && (
                                    <div className="result-card glass-panel" style={{ marginTop: '2rem', borderColor: 'var(--color-error)' }}>
                                        <h3 style={{ color: 'var(--color-error)' }}><FaExclamationTriangle /> Prelims Traps</h3>
                                        <ul className="traps-list" style={{ listStyle: 'none', padding: 0 }}>
                                            {result.prelims_traps.map((trap, i) => (
                                                <li key={i}>{trap}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {result.data_points && (
                                    <div className="result-card glass-panel" style={{ marginTop: '2rem' }}>
                                        <h3 className="neon-text-blue"><FaDatabase /> Data Points</h3>
                                        <ul style={{ listStyle: 'none', padding: 0, color: '#aaa' }}>
                                            {result.data_points.map((dp, i) => (
                                                <li key={i} style={{ marginBottom: '0.5rem' }}>{dp}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default NeuralHash;
