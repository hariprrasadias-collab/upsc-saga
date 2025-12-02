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

    useEffect(() => {
        fetchSubjects();
    }, []);

    const fetchSubjects = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/foresight/subjects');
            const data = await response.json();
            setSubjects(data.subjects || []);
        } catch (error) {
            console.error('Failed to fetch subjects:', error);
        }
    };

    const triggerPrediction = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/foresight/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subject: selectedSubject,
                    timeframe_days: timeframeDays
                })
            });

            const data = await response.json();
            setPredictions(data.predictions || []);
        } catch (error) {
            console.error('Prediction failed:', error);
        } finally {
            setLoading(false);
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
            </div>

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

            {loading && (
                <div className="loading-oracle">
                    <div className="crystal-ball"></div>
                    <p>Analyzing PYQs and Current Affairs...</p>
                </div>
            )}

            <div className="predictions-grid">
                {predictions.map((pred) => (
                    <div
                        key={pred.id}
                        className={`prediction-card ${expandedCard === pred.id ? 'expanded' : ''}`}
                        onClick={() => setExpandedCard(expandedCard === pred.id ? null : pred.id)}
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
                        </div>

                        <div className="question-text">
                            {pred.question}
                        </div>

                        {expandedCard === pred.id && (
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
                            <button className="action-btn">📌 Pin</button>
                            <button className="action-btn">📝 Create Flashcards</button>
                            <button className="action-btn">🧪 Mock Test</button>
                        </div>
                    </div>
                ))}
            </div>

            {predictions.length === 0 && !loading && (
                <div className="empty-state">
                    <div className="crystal-ball-static"></div>
                    <h3>The Crystal Ball Awaits</h3>
                    <p>Configure your parameters and trigger a prediction to see what the future holds.</p>
                </div>
            )}
        </div>
    );
};

export default Foresight;
