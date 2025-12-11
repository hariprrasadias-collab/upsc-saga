import React, { useState, useEffect } from 'react';
import './Foresight.css';

interface Prediction {
    id: number;
    question: string;
    type: 'MCQ' | 'Essay';
    probability: number;
    reasoning: string;
    subject: string;
    topic: string;
    preparation_tip: string;
    generated_at: string;
}

const Foresight: React.FC = () => {
    const [predictions, setPredictions] = useState<Prediction[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedSubject, setSelectedSubject] = useState('All');
    const [timeframeDays, setTimeframeDays] = useState(90);
    const [subjects, setSubjects] = useState<string[]>([]);
    const [expandedCard, setExpandedCard] = useState<number | null>(null);

    const [activeTab, setActiveTab] = useState<'new' | 'saved'>('new');

    useEffect(() => {
        fetchSubjects();
        if (activeTab === 'saved') {
            fetchSavedPredictions();
        }
    }, [activeTab]);

    const fetchSubjects = async () => {
        try {
            const response = await fetch('/api/foresight/subjects');
            const data = await response.json();
            setSubjects(data.subjects || []);
        } catch (error) {
            console.error('Failed to fetch subjects:', error);
        }
    };

    const fetchSavedPredictions = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/foresight/saved');
            const data = await response.json();
            setPredictions(data.predictions || []);
        } catch (error) {
            console.error('Failed to fetch saved predictions:', error);
        } finally {
            setLoading(false);
        }
    };

    const triggerPrediction = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/foresight/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subject: selectedSubject,
                    timeframe_days: timeframeDays
                })
            });

            const data = await response.json();
            setPredictions(data.predictions || []);
            setActiveTab('new');
        } catch (error) {
            console.error('Prediction failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleFavorite = async (pred: Prediction) => {
        if (activeTab === 'saved') {
            // Unsave
            try {
                await fetch(`/api/foresight/unsave/${pred.id}`, { method: 'DELETE' });
                setPredictions(prev => prev.filter(p => p.id !== pred.id));
            } catch (error) {
                console.error('Failed to unsave:', error);
            }
        } else {
            // Save
            try {
                await fetch('/api/foresight/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(pred)
                });
                alert('Prediction saved to favorites!');
            } catch (error) {
                console.error('Failed to save:', error);
            }
        }
    };

    const getProbabilityColor = (prob: number): string => {
        if (prob >= 0.8) return '#00ff88';
        if (prob >= 0.6) return '#ffaa00';
        if (prob >= 0.4) return '#ff6b00';
        return '#ff3366';
    };

    const getProbabilityLabel = (prob: number): string => {
        if (prob >= 0.8) return 'Very High';
        if (prob >= 0.6) return 'High';
        if (prob >= 0.4) return 'Moderate';
        return 'Low';
    };

    return (
        <div className="foresight-container">
            <div className="foresight-header">
                <div className="title-section">
                    <h1>🔮 Project Foresight</h1>
                    <p className="subtitle">The Oracle: Predicting Tomorrow's Questions Today</p>
                </div>
                <div className="foresight-tabs">
                    <button
                        className={`tab-btn ${activeTab === 'new' ? 'active' : ''}`}
                        onClick={() => setActiveTab('new')}
                    >
                        🔮 New Predictions
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'saved' ? 'active' : ''}`}
                        onClick={() => setActiveTab('saved')}
                    >
                        ⭐ Saved Favorites
                    </button>
                </div>
            </div>

            {activeTab === 'new' && (
                <div className="prediction-controls">
                    <div className="control-group">
                        <label>Subject Focus</label>
                        <select
                            value={selectedSubject}
                            onChange={(e) => setSelectedSubject(e.target.value)}
                        >
                            {subjects.map(subject => (
                                <option key={subject} value={subject}>{subject}</option>
                            ))}
                        </select>
                    </div>

                    <div className="control-group">
                        <label>Timeframe (Days)</label>
                        <input
                            type="number"
                            value={isNaN(timeframeDays) ? '' : timeframeDays}
                            onChange={(e) => setTimeframeDays(parseInt(e.target.value))}
                            min="30"
                            max="365"
                        />
                    </div>

                    <button
                        className="predict-button"
                        onClick={triggerPrediction}
                        disabled={loading}
                    >
                        {loading ? '🔮 Consulting the Oracle...' : '🔮 Generate Predictions'}
                    </button>
                </div>
            )}

            {loading && (
                <div className="loading-oracle">
                    <div className="crystal-ball"></div>
                    <p>{activeTab === 'new' ? 'Analyzing PYQs and Current Affairs...' : 'Retrieving Ancient Prophecies...'}</p>
                </div>
            )}

            <div className="predictions-grid">
                {predictions.map((pred, index) => (
                    <div
                        key={pred.id || index}
                        className={`prediction-card ${expandedCard === (pred.id || index) ? 'expanded' : ''}`}
                        onClick={() => setExpandedCard(expandedCard === (pred.id || index) ? null : (pred.id || index))}
                    >
                        <div className="card-header">
                            <div
                                className="probability-badge"
                                style={{
                                    borderColor: getProbabilityColor(pred.probability),
                                    color: getProbabilityColor(pred.probability)
                                }}
                            >
                                <span className="prob-value">{(pred.probability * 100).toFixed(0)}%</span>
                                <span className="prob-label">{getProbabilityLabel(pred.probability)}</span>
                            </div>
                            <div className="meta-tags">
                                <span className="subject-tag">{pred.subject}</span>
                                <span className="type-tag">{pred.type}</span>
                            </div>
                            <button
                                className="favorite-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    toggleFavorite(pred);
                                }}
                                title={activeTab === 'saved' ? "Remove from Favorites" : "Save to Favorites"}
                            >
                                {activeTab === 'saved' ? '⭐' : '☆'}
                            </button>
                        </div>

                        <div className="question-text">
                            {pred.question}
                        </div>

                        {expandedCard === (pred.id || index) && (
                            <div className="expanded-details">
                                <div className="detail-section">
                                    <h4>📊 Reasoning</h4>
                                    <p>{pred.reasoning}</p>
                                </div>

                                <div className="detail-section">
                                    <h4>📚 Topic</h4>
                                    <p>{pred.topic}</p>
                                </div>

                                <div className="detail-section">
                                    <h4>💡 Preparation Strategy</h4>
                                    <p>{pred.preparation_tip}</p>
                                </div>
                            </div>
                        )}

                        <div className="card-footer">
                            <button className="action-btn">📝 Create Flashcards</button>
                            <button className="action-btn">🧪 Mock Test</button>
                        </div>
                    </div>
                ))}
            </div>

            {predictions.length === 0 && !loading && (
                <div className="empty-state">
                    <div className="crystal-ball-static"></div>
                    <h3>{activeTab === 'new' ? 'The Crystal Ball Awaits' : 'No Saved Prophecies'}</h3>
                    <p>{activeTab === 'new' ? 'Configure your parameters and trigger a prediction to see what the future holds.' : 'Star predictions to save them here for future reference.'}</p>
                </div>
            )}
        </div>
    );
};

export default Foresight;
