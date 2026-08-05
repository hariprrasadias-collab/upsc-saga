import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import './MnemonicGenerator.css';

interface MnemonicGeneratorProps {
    onMnemonicGenerated?: (mnemonic: string) => void;
}

interface MnemonicHistoryItem {
    id: number;
    mnemonic_text: string;
    original_text: string;
    mnemonic_type: string;
    visualization_prompt?: string;
    created_at: string;
}

const MnemonicGenerator: React.FC<MnemonicGeneratorProps> = ({ onMnemonicGenerated }) => {
    const [activeTab, setActiveTab] = useState<'create' | 'history'>('create');
    const [text, setText] = useState('');
    const [mnemonicType, setMnemonicType] = useState('facts');
    const [mnemonic, setMnemonic] = useState('');
    const [visualizationPrompt, setVisualizationPrompt] = useState('');
    const [generating, setGenerating] = useState(false);
    const [history, setHistory] = useState<MnemonicHistoryItem[]>([]);
    const [loadingHistory, setLoadingHistory] = useState(false);
    const [selectedMnemonic, setSelectedMnemonic] = useState<string | null>(null);

    const [deletingId, setDeletingId] = useState<number | null>(null);

    useEffect(() => {
        if (activeTab === 'history') {
            fetchHistory();
        }
    }, [activeTab]);

    const fetchHistory = async () => {
        setLoadingHistory(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/revision/mnemonic/history`);
            const data = await response.json();
            if (data.success) {
                setHistory(data.history);
            }
        } catch (error) {
            console.error('Error fetching history:', error);
        } finally {
            setLoadingHistory(false);
        }
    };

    const handleGenerate = async () => {
        if (!text.trim()) {
            // Replaced alert with a more subtle UI feedback if possible, but for now keeping simple validation
            return;
        }

        setGenerating(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/revision/mnemonic`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    type: mnemonicType
                })
            });

            const data = await response.json();
            if (data.success) {
                setMnemonic(data.mnemonic);
                setVisualizationPrompt(data.visualization_prompt || '');
                if (onMnemonicGenerated) {
                    onMnemonicGenerated(data.mnemonic);
                }
                // Refresh history if we switch tabs
                fetchHistory();
            } else {
                console.error('Failed to generate mnemonic');
            }
        } catch (error) {
            console.error('Error generating mnemonic:', error);
        } finally {
            setGenerating(false);
        }
    };

    const handleCopy = (textToCopy: string, e?: React.MouseEvent) => {
        if (e) e.stopPropagation();
        navigator.clipboard.writeText(textToCopy);
        // Could add a toast notification here
    };

    const handleClear = () => {
        setText('');
        setMnemonic('');
        setVisualizationPrompt('');
    };

    const confirmDelete = (id: number, e: React.MouseEvent) => {
        e.stopPropagation();
        setDeletingId(id);
    };

    const cancelDelete = (e: React.MouseEvent) => {
        e.stopPropagation();
        setDeletingId(null);
    };

    const handleDelete = async (id: number, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            const response = await fetch(`${API_BASE_URL}/api/revision/mnemonic/history/${id}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            if (data.success) {
                setHistory(prev => prev.filter(item => item.id !== id));
                setDeletingId(null);
            }
        } catch (error) {
            console.error('Error deleting mnemonic:', error);
        }
    };

    const renderMnemonicContent = (content: string, mode: 'preview' | 'full' = 'preview') => {
        const parts = content.split('---');
        let mnemonicPhrase = '';
        let explanation = content;

        if (parts.length > 1) {
            mnemonicPhrase = parts[0].replace(/\*\*MNEMONIC:\*\*/i, '').trim();
            explanation = parts.slice(1).join('---').trim();
        } else {
            const match = content.match(/\*\*MNEMONIC:\*\*\s*(.*?)\n/i);
            if (match) {
                mnemonicPhrase = match[1].trim();
                explanation = content.replace(match[0], '').trim();
            }
        }

        if (mode === 'preview') {
            return (
                <div
                    className="mnemonic-preview-card"
                    onClick={() => setSelectedMnemonic(content)}
                    title="Click to expand"
                >
                    {mnemonicPhrase ? (
                        <div className="mnemonic-hero preview">
                            <div className="hero-label">MEMORY HOOK</div>
                            <h1 className="hero-text">{mnemonicPhrase.replace(/\*\*/g, '')}</h1>
                            {visualizationPrompt && (
                                <div className="visualization-prompt">
                                    <span className="vis-icon">👁️</span>
                                    <i>{visualizationPrompt}</i>
                                </div>
                            )}
                            <div className="click-hint">Click to view full details ↗</div>
                        </div>
                    ) : (
                        <div className="mnemonic-preview-text">
                            {content.substring(0, 100)}...
                        </div>
                    )}
                </div>
            );
        }

        return (
            <div className="mnemonic-full-content">
                {mnemonicPhrase && (
                    <div className="mnemonic-hero full">
                        <div className="hero-label">MEMORY HOOK</div>
                        <h1 className="hero-text">{mnemonicPhrase.replace(/\*\*/g, '')}</h1>
                        {visualizationPrompt && (
                            <div className="visualization-prompt" style={{ marginTop: '1rem', color: 'var(--color-accent-orange)', fontSize: '1.2rem' }}>
                                <span className="vis-icon">👁️  Visualize this: </span>
                                <i>{visualizationPrompt}</i>
                            </div>
                        )}
                    </div>
                )}

                <div className="mnemonic-explanation">
                    <ReactMarkdown>{explanation}</ReactMarkdown>
                </div>
            </div>
        );
    };

    return (
        <div className="mnemonic-generator">
            {/* Modal Overlay */}
            {selectedMnemonic && (
                <div className="mnemonic-modal-overlay" onClick={() => setSelectedMnemonic(null)}>
                    <div className="mnemonic-modal-content" onClick={e => e.stopPropagation()}>
                        <button className="modal-close-btn" onClick={() => setSelectedMnemonic(null)} aria-label="Close">×</button>
                        <div className="modal-scroll-area">
                            {renderMnemonicContent(selectedMnemonic, 'full')}
                        </div>
                        <div className="modal-actions">
                            <button className="copy-btn" onClick={(e) => handleCopy(selectedMnemonic, e)}>
                                📋 Copy Full Mnemonic
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="mnemonic-header">
                <div>
                    <h2>🧠 Neural Mnemonic Engine</h2>
                    <p className="mnemonic-subtitle">Forge unbreakable memory links using ancient wisdom</p>
                </div>
                <div className="mnemonic-tabs">
                    <button
                        className={`tab-btn ${activeTab === 'create' ? 'active' : ''}`}
                        onClick={() => setActiveTab('create')}
                    >
                        Create
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                        onClick={() => setActiveTab('history')}
                    >
                        Memory Shards
                    </button>
                </div>
            </div>

            {activeTab === 'create' ? (
                <>
                    <div className="mnemonic-form">
                        <div>
                            <div className="label-row">
                                <label className="input-label">Input Data</label>
                                {text && (
                                    <button className="clear-btn" onClick={handleClear}>
                                        Clear
                                    </button>
                                )}
                            </div>
                            <textarea
                                className="mnemonic-textarea"
                                placeholder="Enter facts, dates, list of items, or concept to encode..."
                                rows={5}
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="input-label">Encoding Pattern</label>
                            <div className="type-selector">
                                <button
                                    className={`type-btn ${mnemonicType === 'facts' ? 'active' : ''}`}
                                    onClick={() => setMnemonicType('facts')}
                                >
                                    <span>📚</span>
                                    Facts
                                </button>
                                <button
                                    className={`type-btn ${mnemonicType === 'dates' ? 'active' : ''}`}
                                    onClick={() => setMnemonicType('dates')}
                                >
                                    <span>📅</span>
                                    Dates
                                </button>
                                <button
                                    className={`type-btn ${mnemonicType === 'list' ? 'active' : ''}`}
                                    onClick={() => setMnemonicType('list')}
                                >
                                    <span>📝</span>
                                    List
                                </button>
                                <button
                                    className={`type-btn ${mnemonicType === 'concept' ? 'active' : ''}`}
                                    onClick={() => setMnemonicType('concept')}
                                >
                                    <span>💡</span>
                                    Concept
                                </button>
                            </div>
                        </div>

                        <button
                            className="generate-mnemonic-btn"
                            onClick={handleGenerate}
                            disabled={generating || !text.trim()}
                        >
                            {generating ? '✨ Forging Memory Link...' : '⚡ Generate Mnemonic'}
                        </button>
                    </div>

                    <AnimatePresence>
                        {mnemonic && (
                            <motion.div
                                className="mnemonic-result"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20, transition: { duration: 0.2 } }}
                                transition={{ duration: 0.5, ease: "easeOut" }}
                            >
                                <div className="result-header">
                                    <h3>Revealed Truth</h3>
                                </div>
                                <div className="mnemonic-box">
                                    {renderMnemonicContent(mnemonic, 'preview')}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </>
            ) : (
                <div className="mnemonic-history">
                    {loadingHistory ? (
                        <div className="loading-state">Accessing Memory Archives...</div>
                    ) : history.length === 0 ? (
                        <div className="empty-state">No memory shards found. Create your first link.</div>
                    ) : (
                        <div className="history-list">
                            {history.map((item) => (
                                <div key={item.id} className="history-card" onClick={() => setSelectedMnemonic(item.mnemonic_text)}>
                                    <div className="history-header">
                                        <div className="history-meta">
                                            <span className={`history-type-badge ${item.mnemonic_type}`}>
                                                {item.mnemonic_type.toUpperCase()}
                                            </span>
                                            <span className="history-date">
                                                {new Date(item.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <div className="history-actions">
                                            <button
                                                className="icon-btn copy-icon-btn"
                                                onClick={(e) => handleCopy(item.mnemonic_text, e)}
                                                title="Copy Mnemonic"
                                            >
                                                📋
                                            </button>

                                            {deletingId === item.id ? (
                                                <div className="delete-confirm-group">
                                                    <button
                                                        className="confirm-delete-btn"
                                                        onClick={(e) => handleDelete(item.id, e)}
                                                    >
                                                        Confirm
                                                    </button>
                                                    <button
                                                        className="cancel-delete-btn"
                                                        onClick={cancelDelete}
                                                    >
                                                        ✕
                                                    </button>
                                                </div>
                                            ) : (
                                                <button
                                                    className="icon-btn delete-icon-btn"
                                                    onClick={(e) => confirmDelete(item.id, e)}
                                                    title="Delete Mnemonic"
                                                >
                                                    🗑️
                                                </button>
                                            )}
                                        </div>
                                    </div>

                                    <div className="history-content">
                                        {item.mnemonic_type === 'visual' ? (
                                            <div className="history-section vis-section" style={{ marginBottom: '1rem', background: '#1a1f33', padding: '10px', borderRadius: '8px', borderLeft: '4px solid #f39c12' }}>
                                                <span className="section-label" style={{ color: '#f39c12' }}>📸 Visual Generation Prompt (Midjourney)</span>
                                                <p className="section-text" style={{ fontFamily: 'monospace', color: '#a8b2d1', fontSize: '0.9rem', marginTop: '5px' }}>
                                                    {item.mnemonic_text}
                                                </p>
                                            </div>
                                        ) : (
                                            <div className="history-section mnemonic-section" style={{ marginBottom: '1rem' }}>
                                                <span className="section-label" style={{ color: 'var(--color-primary-light)' }}>🧠 Memory Hook</span>
                                                <h3 className="section-text" style={{ fontSize: '1.2rem', color: 'var(--color-text)' }}>
                                                    {item.mnemonic_text.replace(/\*\*/g, '')}
                                                </h3>
                                            </div>
                                        )}
                                        {item.visualization_prompt && (
                                            <div className="history-section vis-section" style={{ marginBottom: '1rem' }}>
                                                <span className="section-label">👁️ Visualization Suggestion</span>
                                                <p className="section-text" style={{ color: 'var(--color-accent-orange)', fontStyle: 'italic' }}>
                                                    {item.visualization_prompt}
                                                </p>
                                            </div>
                                        )}
                                        <div className="history-section input-section">
                                            <span className="section-label">Source Context</span>
                                            <p className="section-text" style={{ opacity: 0.8, fontSize: '0.9rem' }}>
                                                {item.original_text}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default MnemonicGenerator;
