import React, { useState } from 'react';
import './NeuralHash.css';

interface DecodedData {
    core_themes: string[];
    high_yield_keywords: string[];
    examiner_pattern: string;
    potential_questions: { type: string; question: string }[];
    complexity_score: number;
    relevance_score: number;
}

const NeuralHash: React.FC = () => {
    const [inputText, setInputText] = useState('');
    const [contextType, setContextType] = useState('general');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<DecodedData | null>(null);

    const handleDecode = async () => {
        if (!inputText.trim()) return;

        setLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/neural_hash/decode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: inputText, type: contextType })
            });
            const data = await response.json();
            if (data.success) {
                setResult(data.data);
            } else {
                alert('Decoding failed: ' + data.error);
            }
        } catch (error) {
            console.error('Decode error:', error);
            alert('Failed to connect to the Neural Hash.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="neural-hash-container">
            <div className="decoder-header">
                <h1>The Neural Hash</h1>
                <div className="subtitle">PATTERN RECOGNITION & DECODING ENGINE</div>
            </div>

            <div className="input-section">
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
                    placeholder="PASTE TEXT DATA HERE FOR DECODING..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                />

                <button
                    className="decode-btn"
                    onClick={handleDecode}
                    disabled={loading || !inputText}
                >
                    {loading ? 'DECODING PATTERNS...' : 'INITIATE DECODE SEQUENCE'}
                </button>
            </div>

            {loading && (
                <div className="loading-matrix">
                    &gt; ACCESSING NEURAL PATHWAYS...<br />
                    &gt; ANALYZING EXAMINER PSYCHE...<br />
                    &gt; EXTRACTING HIGH-YIELD ARTIFACTS...
                </div>
            )}

            {result && (
                <div className="results-container">
                    <div className="left-panel">
                        <div className="result-card">
                            <h3>Core Themes (The Soul)</h3>
                            <div className="themes-list">
                                {result.core_themes.map((theme, i) => (
                                    <span key={i} className="theme-tag">{theme}</span>
                                ))}
                            </div>
                        </div>

                        <div className="result-card" style={{ marginTop: '2rem' }}>
                            <h3>Examiner's Pattern</h3>
                            <p className="pattern-text">{result.examiner_pattern}</p>
                        </div>

                        <div className="result-card" style={{ marginTop: '2rem' }}>
                            <h3>Potential Derivatives</h3>
                            {result.potential_questions.map((q, i) => (
                                <div key={i} className="question-item">
                                    <span className="q-type">{q.type}</span>
                                    <div className="q-text">{q.question}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="right-panel">
                        <div className="result-card">
                            <h3>Metrics</h3>
                            <div className="score-display">
                                <div className={`score-circle ${result.relevance_score > 7 ? 'high' : 'low'}`}>
                                    {result.relevance_score}
                                </div>
                                <div className="score-label">Relevance Score</div>
                            </div>
                            <div className="score-display">
                                <div className="score-circle med" style={{ width: '80px', height: '80px', fontSize: '2rem' }}>
                                    {result.complexity_score}
                                </div>
                                <div className="score-label">Complexity</div>
                            </div>
                        </div>

                        <div className="result-card" style={{ marginTop: '2rem' }}>
                            <h3>High Yield Keywords</h3>
                            <div className="keywords-list">
                                {result.high_yield_keywords.map((kw, i) => (
                                    <span key={i} className="keyword-tag">{kw}</span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default NeuralHash;
