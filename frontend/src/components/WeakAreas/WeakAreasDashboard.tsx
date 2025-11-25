import React, { useState, useEffect } from 'react';
import './WeakAreasDashboard.css';
import { useToast } from '../Toast';

interface WeakArea {
    topic: string;
    subject: string;
    total_attempts: number;
    correct_attempts: number;
    accuracy_rate: number;
    trend: 'improving' | 'declining' | 'stable';
    priority_score: number;
}

interface PracticeSet {
    id: number;
    set_name: string;
    total_questions: number;
    completed: number;
    score: number;
    created_at: string;
}

const WeakAreasDashboard: React.FC = () => {
    const [weakAreas, setWeakAreas] = useState<WeakArea[]>([]);
    const [practiceSets, setPracticeSets] = useState<PracticeSet[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const { addToast } = useToast();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [areasRes, setsRes] = await Promise.all([
                fetch('http://localhost:5000/api/weak-areas/analysis'),
                fetch('http://localhost:5000/api/weak-areas/practice-sets')
            ]);

            if (areasRes.ok) {
                const data = await areasRes.json();
                setWeakAreas(data.weak_areas);
            }

            if (setsRes.ok) {
                const data = await setsRes.json();
                setPracticeSets(data.practice_sets);
            }
        } catch (error) {
            console.error('Error fetching weak areas:', error);
            addToast('Failed to load weak areas data', 'error');
        } finally {
            setLoading(false);
        }
    };

    const generatePracticeSet = async () => {
        setGenerating(true);
        try {
            const res = await fetch('http://localhost:5000/api/weak-areas/practice-set', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ num_questions: 10 })
            });

            if (res.ok) {
                await res.json(); // Consume response but don't use variable
                addToast('Practice set generated successfully!', 'success');
                fetchData(); // Refresh list
            } else {
                const err = await res.json();
                addToast(err.error || 'Failed to generate set', 'error');
            }
        } catch (error) {
            console.error('Error generating set:', error);
            addToast('Error generating practice set', 'error');
        } finally {
            setGenerating(false);
        }
    };

    if (loading) return <div className="loading-spinner"></div>;

    return (
        <div className="weak-areas-container animate-fade-in">
            <header className="wa-header">
                <div>
                    <h1>Weak Area Targeter</h1>
                    <p>AI-identified topics that need your attention</p>
                </div>
                <button
                    className={`generate-btn ${generating ? 'loading' : ''}`}
                    onClick={generatePracticeSet}
                    disabled={generating || weakAreas.length === 0}
                >
                    {generating ? 'Generating...' : '🎯 Generate Focused Practice'}
                </button>
            </header>

            <div className="wa-grid">
                <div className="wa-section weak-topics">
                    <h2>Priority Topics</h2>
                    {weakAreas.length === 0 ? (
                        <div className="empty-state">
                            <p>No weak areas identified yet. Keep taking mock tests!</p>
                        </div>
                    ) : (
                        <div className="topics-list stagger-children">
                            {weakAreas.map((area) => (
                                <div key={`${area.subject}-${area.topic}`} className="topic-card hover-lift">
                                    <div className="topic-header">
                                        <span className="topic-subject">{area.subject}</span>
                                        <span className={`topic-trend ${area.trend}`}>
                                            {area.trend === 'improving' ? '↗' : area.trend === 'declining' ? '↘' : '→'}
                                        </span>
                                    </div>
                                    <h3>{area.topic}</h3>
                                    <div className="topic-stats">
                                        <div className="stat">
                                            <label>Accuracy</label>
                                            <div className="progress-bar">
                                                <div
                                                    className="progress-fill"
                                                    style={{
                                                        width: `${area.accuracy_rate}%`,
                                                        background: area.accuracy_rate < 40 ? '#ef4444' : '#f59e0b'
                                                    }}
                                                ></div>
                                            </div>
                                            <span>{Math.round(area.accuracy_rate)}%</span>
                                        </div>
                                        <div className="stat-row">
                                            <span>Attempts: {area.total_attempts}</span>
                                            <span>Correct: {area.correct_attempts}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="wa-section practice-sets">
                    <h2>Your Practice Sets</h2>
                    {practiceSets.length === 0 ? (
                        <div className="empty-state">
                            <p>No practice sets generated yet.</p>
                        </div>
                    ) : (
                        <div className="sets-list stagger-children">
                            {practiceSets.map((set) => (
                                <div key={set.id} className="set-card hover-lift">
                                    <div className="set-info">
                                        <h3>{set.set_name}</h3>
                                        <span className="set-date">
                                            {new Date(set.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div className="set-status">
                                        {set.completed >= set.total_questions ? (
                                            <span className="status-completed">
                                                Score: {Math.round(set.score)}/{set.total_questions}
                                            </span>
                                        ) : (
                                            <button className="start-btn">
                                                Continue ({set.completed}/{set.total_questions})
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WeakAreasDashboard;
