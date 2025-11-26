// QuizResults.tsx - Display quiz results with review
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import './QuizResults.css';

interface ResultsData {
    score: number;
    total_questions: number;
    correct_count: number;
    incorrect_count: number;
    duration_seconds: number;
    results: any[];
}

const QuizResults: React.FC = () => {
    const { sessionId } = useParams<{ sessionId: string }>();
    const navigate = useNavigate();
    const location = useLocation();
    const [results, setResults] = useState<ResultsData | null>(location.state?.results || null);
    const [loading, setLoading] = useState(!results);
    const [showExplanations, setShowExplanations] = useState(true);

    useEffect(() => {
        if (!results) {
            const fetchResults = async () => {
                try {
                    const res = await fetch(`http://localhost:5000/api/pyq/quiz/${sessionId}`);
                    const data = await res.json();
                    setResults({
                        score: data.session.score,
                        total_questions: data.session.total_questions,
                        correct_count: data.session.correct_count,
                        incorrect_count: data.session.incorrect_count,
                        duration_seconds: data.session.duration_seconds,
                        results: data.questions
                    });
                    setLoading(false);
                } catch (err) {
                    console.error('Failed to load results', err);
                }
            };
            fetchResults();
        }
    }, [sessionId, results]);

    if (loading || !results) {
        return (
            <div className="results-loading-container">
                <div className="loading-spinner"></div>
                <p>Analyzing Performance...</p>
            </div>
        );
    }

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}m ${secs}s`;
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return '#4ade80'; // Green
        if (score >= 60) return '#facc15'; // Yellow
        return '#f87171'; // Red
    };

    const subjectWise = results.results.reduce((acc: any, q: any) => {
        if (!acc[q.subject]) {
            acc[q.subject] = { correct: 0, total: 0 };
        }
        acc[q.subject].total++;
        if (q.is_correct) acc[q.subject].correct++;
        return acc;
    }, {});

    // Circular Progress Component
    const CircularProgress = ({ score }: { score: number }) => {
        const radius = 60;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (score / 100) * circumference;
        const color = getScoreColor(score);

        return (
            <div className="circular-progress">
                <svg width="140" height="140" viewBox="0 0 140 140">
                    <circle
                        cx="70"
                        cy="70"
                        r={radius}
                        fill="none"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="10"
                    />
                    <circle
                        cx="70"
                        cy="70"
                        r={radius}
                        fill="none"
                        stroke={color}
                        strokeWidth="10"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        transform="rotate(-90 70 70)"
                        style={{ transition: 'stroke-dashoffset 1s ease-out' }}
                    />
                </svg>
                <div className="progress-value">
                    <span className="score-number" style={{ color }}>{score.toFixed(0)}%</span>
                    <span className="score-text">Score</span>
                </div>
            </div>
        );
    };

    return (
        <div className="results-container">
            <header className="results-header">
                <div className="header-content">
                    <h1>Performance Report</h1>
                    <p className="session-id">Session #{sessionId?.slice(0, 8)}</p>
                </div>
                <button className="back-btn" onClick={() => navigate('/pyq-archives')}>
                    ← Back to Archives
                </button>
            </header>

            <div className="results-dashboard">
                {/* Left Column: Score & Stats */}
                <div className="dashboard-left">
                    <div className="score-card">
                        <CircularProgress score={results.score} />
                        <div className="score-message">
                            {results.score >= 80 ? 'Excellent Work! 🌟' :
                                results.score >= 60 ? 'Good Effort! 👍' :
                                    'Keep Practicing! 💪'}
                        </div>
                    </div>

                    <div className="stats-grid">
                        <div className="stat-card correct">
                            <div className="stat-icon">✓</div>
                            <div className="stat-info">
                                <span className="stat-value">{results.correct_count}</span>
                                <span className="stat-label">Correct</span>
                            </div>
                        </div>
                        <div className="stat-card incorrect">
                            <div className="stat-icon">✗</div>
                            <div className="stat-info">
                                <span className="stat-value">{results.incorrect_count}</span>
                                <span className="stat-label">Incorrect</span>
                            </div>
                        </div>
                        <div className="stat-card time">
                            <div className="stat-icon">⏱</div>
                            <div className="stat-info">
                                <span className="stat-value">{formatTime(results.duration_seconds)}</span>
                                <span className="stat-label">Time Taken</span>
                            </div>
                        </div>
                        <div className="stat-card accuracy">
                            <div className="stat-icon">🎯</div>
                            <div className="stat-info">
                                <span className="stat-value">
                                    {Math.round((results.correct_count / results.total_questions) * 100)}%
                                </span>
                                <span className="stat-label">Accuracy</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column: Subject Analysis */}
                <div className="dashboard-right">
                    <div className="subject-analysis">
                        <h3>Subject Breakdown</h3>
                        <div className="subject-list">
                            {Object.entries(subjectWise).map(([subject, data]: [string, any]) => {
                                const percentage = (data.correct / data.total) * 100;
                                return (
                                    <div key={subject} className="subject-item">
                                        <div className="subject-info">
                                            <span className="subject-name">{subject}</span>
                                            <span className="subject-score">{data.correct}/{data.total}</span>
                                        </div>
                                        <div className="progress-bar-bg">
                                            <div
                                                className="progress-bar-fill"
                                                style={{
                                                    width: `${percentage}%`,
                                                    backgroundColor: getScoreColor(percentage)
                                                }}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </div>

            <div className="review-section">
                <div className="review-header-row">
                    <h2>Detailed Review</h2>
                    <button
                        className="toggle-explanations-btn"
                        onClick={() => setShowExplanations(!showExplanations)}
                    >
                        {showExplanations ? 'Hide Explanations' : 'Show Explanations'}
                    </button>
                </div>

                <div className="questions-list">
                    {results.results.map((q: any, idx: number) => {
                        const isCorrect = q.is_correct;
                        const wasAnswered = q.selected_answer !== null;

                        return (
                            <div key={idx} className={`question-card ${isCorrect ? 'correct-card' : 'incorrect-card'}`}>
                                <div className="q-header">
                                    <span className="q-number">Q{idx + 1}</span>
                                    <div className="q-tags">
                                        <span className="q-tag subject">{q.subject}</span>
                                        <span className="q-tag year">{q.year}</span>
                                    </div>
                                    <span className={`q-status ${isCorrect ? 'status-correct' : 'status-wrong'}`}>
                                        {!wasAnswered ? 'Skipped' : isCorrect ? 'Correct' : 'Incorrect'}
                                    </span>
                                </div>

                                <div className="q-text">{q.question_text}</div>

                                <div className="q-options">
                                    {['A', 'B', 'C', 'D'].map(opt => {
                                        const optionKey = `option_${opt.toLowerCase()}`;
                                        const optionText = q[optionKey];
                                        const isUserAnswer = q.selected_answer === opt;
                                        const isCorrectAnswer = q.correct_option === opt;

                                        let optionClass = 'q-option';
                                        if (isCorrectAnswer) optionClass += ' opt-correct';
                                        if (isUserAnswer && !isCorrect) optionClass += ' opt-wrong';
                                        if (isUserAnswer) optionClass += ' opt-selected';

                                        return (
                                            <div key={opt} className={optionClass}>
                                                <span className="opt-letter">{opt}</span>
                                                <span className="opt-text">{optionText}</span>
                                                {isCorrectAnswer && <span className="opt-badge badge-correct">Correct Answer</span>}
                                                {isUserAnswer && !isCorrect && <span className="opt-badge badge-wrong">Your Answer</span>}
                                            </div>
                                        );
                                    })}
                                </div>

                                {showExplanations && q.explanation && (
                                    <div className="q-explanation">
                                        <h4>💡 Explanation</h4>
                                        <p>{q.explanation}</p>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default QuizResults;
