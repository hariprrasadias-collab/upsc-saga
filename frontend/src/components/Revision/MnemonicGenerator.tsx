import React, { useState, useEffect } from 'react';
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

    return (
        <div className="mnemonic-generator">
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
                                <button className="copy-btn" onClick={() => handleCopy(mnemonic)}>
                                    📋 Copy
                                </button>
                            </div>
                            <div className="mnemonic-box">
                                <p>{mnemonic}</p>
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
                                        <span className="history-type">{item.mnemonic_type}</span>
                                        <span className="history-date">
                                            {new Date(item.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div className="history-original">
                                        <strong>Input:</strong> {item.original_text.substring(0, 100)}
                                        {item.original_text.length > 100 ? '...' : ''}
                                    </div>
                                    <div className="history-mnemonic">
                                        <strong>Mnemonic:</strong>
                                        <p>{item.mnemonic_text}</p>
                                    </div>
                                    <button
                                        className="copy-btn-small"
                                        onClick={() => handleCopy(item.mnemonic_text)}
                                    >
                                        📋 Copy
                                    </button>
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
