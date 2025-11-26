import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './MnemonicGenerator.css';

interface MnemonicGeneratorProps {
    onMnemonicGenerated?: (mnemonic: string) => void;
}

interface MnemonicHistoryItem {
    id: number;
    mnemonic_text: string;
    original_text: string;
    mnemonic_type: string;
    created_at: string;
}

const MnemonicGenerator: React.FC<MnemonicGeneratorProps> = ({ onMnemonicGenerated }) => {
    const [activeTab, setActiveTab] = useState<'create' | 'history'>('create');
    const [text, setText] = useState('');
    const [mnemonicType, setMnemonicType] = useState('facts');
    const [mnemonic, setMnemonic] = useState('');
    const [generating, setGenerating] = useState(false);
    const [history, setHistory] = useState<MnemonicHistoryItem[]>([]);
    const [loadingHistory, setLoadingHistory] = useState(false);
    const [selectedMnemonic, setSelectedMnemonic] = useState<string | null>(null);

    useEffect(() => {
        if (activeTab === 'history') {
            fetchHistory();
        }
    }, [activeTab]);

    const fetchHistory = async () => {
        setLoadingHistory(true);
        try {
            const response = await fetch('http://localhost:5000/api/revision/mnemonic/history');
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
            alert('Please enter some content');
            return;
        }

        setGenerating(true);
        try {
            const response = await fetch('http://localhost:5000/api/revision/mnemonic', {
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
                if (onMnemonicGenerated) {
                    onMnemonicGenerated(data.mnemonic);
                }
                // Refresh history if we switch tabs
                fetchHistory();
            } else {
                alert('Failed to generate mnemonic');
            }
        } catch (error) {
            console.error('Error generating mnemonic:', error);
            alert('Error generating mnemonic');
        } finally {
            setGenerating(false);
        }
    };

    const handleCopy = (textToCopy: string) => {
        navigator.clipboard.writeText(textToCopy);
        alert('Mnemonic copied to clipboard!');
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this mnemonic?')) return;

        try {
            const response = await fetch(`http://localhost:5000/api/revision/mnemonic/history/${id}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            if (data.success) {
                setHistory(prev => prev.filter(item => item.id !== id));
            } else {
                alert('Failed to delete mnemonic');
            }
        } catch (error) {
            console.error('Error deleting mnemonic:', error);
            alert('Error deleting mnemonic');
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
                        <button className="modal-close-btn" onClick={() => setSelectedMnemonic(null)}>×</button>
                        <div className="modal-scroll-area">
                            {renderMnemonicContent(selectedMnemonic, 'full')}
                        </div>
                        <div className="modal-actions">
                            <button className="copy-btn" onClick={() => handleCopy(selectedMnemonic)}>
                                📋 Copy Full Mnemonic
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="mnemonic-header">
                <div>
                    <h2>🧠 Mnemonic Generator</h2>
                    <p className="mnemonic-subtitle">Create memory aids for UPSC topics</p>
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
                        History
                    </button>
                </div>
            </div>

            {activeTab === 'create' ? (
                <>
                    <div className="mnemonic-form">
                        <label className="input-label">What do you want to remember?</label>
                        <textarea
                            className="mnemonic-textarea"
                            placeholder="Enter facts, dates, list of items, or concept..."
                            rows={5}
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                        />

                        <label className="input-label">Mnemonic Type</label>
                        <div className="type-selector">
                            <button
                                className={`type-btn ${mnemonicType === 'facts' ? 'active' : ''}`}
                                onClick={() => setMnemonicType('facts')}
                            >
                                📚 Facts
                            </button>
                            <button
                                className={`type-btn ${mnemonicType === 'dates' ? 'active' : ''}`}
                                onClick={() => setMnemonicType('dates')}
                            >
                                📅 Dates
                            </button>
                            <button
                                className={`type-btn ${mnemonicType === 'list' ? 'active' : ''}`}
                                onClick={() => setMnemonicType('list')}
                            >
                                📝 List
                            </button>
                            <button
                                className={`type-btn ${mnemonicType === 'concept' ? 'active' : ''}`}
                                onClick={() => setMnemonicType('concept')}
                            >
                                💡 Concept
                            </button>
                        </div>

                        <button
                            className="generate-mnemonic-btn"
                            onClick={handleGenerate}
                            disabled={generating || !text.trim()}
                        >
                            {generating ? '✨ Creating Memory Aid...' : '🎯 Generate Mnemonic'}
                        </button>
                    </div>

                    {mnemonic && (
                        <div className="mnemonic-result">
                            <div className="result-header">
                                <h3>Your Mnemonic:</h3>
                            </div>
                            <div className="mnemonic-box">
                                {renderMnemonicContent(mnemonic, 'preview')}
                            </div>
                        </div>
                    )}
                </>
            ) : (
                <div className="mnemonic-history">
                    {loadingHistory ? (
                        <div className="loading-state">Loading history...</div>
                    ) : history.length === 0 ? (
                        <div className="empty-state">No mnemonics generated yet. Create one!</div>
                    ) : (
                        <div className="history-list">
                            {history.map((item) => (
                                <div key={item.id} className="history-card">
                                    <div className="history-header">
                                        <div className="history-meta">
                                            <span className={`history-type-badge ${item.mnemonic_type}`}>
                                                {item.mnemonic_type.toUpperCase()}
                                            </span>
                                            <span className="history-date">
                                                {new Date(item.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                        <button
                                            className="delete-btn"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDelete(item.id);
                                            }}
                                            title="Delete Mnemonic"
                                        >
                                            🗑️
                                        </button>
                                    </div>

                                    <div className="history-content">
                                        <div className="history-section input-section">
                                            <span className="section-label">Input:</span>
                                            <p className="section-text">
                                                {item.original_text.length > 100
                                                    ? item.original_text.substring(0, 100) + '...'
                                                    : item.original_text}
                                            </p>
                                        </div>

                                        <div className="history-section result-section">
                                            <div className="section-header">
                                                <span className="section-label">Mnemonic:</span>
                                            </div>
                                            {renderMnemonicContent(item.mnemonic_text, 'preview')}
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
