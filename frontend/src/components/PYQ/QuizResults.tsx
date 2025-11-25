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
            // Fetch results if not passed via navigation state
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
        return <div className="results-loading">Loading Results...</div>;
    }

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}m ${secs}s`;
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return '#2ecc71';
        if (score >= 60) return '#f39c12';
        return '#e74c3c';
    };

    const subjectWise = results.results.reduce((acc: any, q: any) => {
        if (!acc[q.subject]) {
            acc[q.subject] = { correct: 0, total: 0 };
        }
        acc[q.subject].total++;
        if (q.is_correct) acc[q.subject].correct++;
        return acc;
    }, {});

    return (
        <div className="results-container">
            <div className="results-header">
                <h1>Quiz Results</h1>
                <button className="back-btn" onClick={() => navigate('/pyq-archives')}>
                    Back to Archives
                </button>
            </div>

            <div className="results-summary">
                <div className="score-card" style={{ borderColor: getScoreColor(results.score) }}>
                    <div className="score-value" style={{ color: getScoreColor(results.score) }}>
                        {results.score.toFixed(1)}%
                    </div>
                    <div className="score-label">Score</div>
                </div>

                <div className="stats-grid">
                    <div className="stat-item">
                        <div className="stat-value">{results.correct_count}</div>
                        <div className="stat-label">Correct</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-value">{results.incorrect_count}</div>
                        <div className="stat-label">Incorrect</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-value">{results.total_questions}</div>
                        <div className="stat-label">Total Questions</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-value">{formatTime(results.duration_seconds)}</div>
                        <div className="stat-label">Time Taken</div>
                    </div>
                </div>

                <div className="subject-performance">
                    <h3>Subject-wise Performance</h3>
                    <div className="subject-grid">
                        {Object.entries(subjectWise).map(([subject, data]: [string, any]) => (
                            <div key={subject} className="subject-card">
                                <div className="subject-name">{subject}</div>
                                <div className="subject-score">
                                    {data.correct} / {data.total}
                                </div>
                                <div className="subject-percent">
                                    {((data.correct / data.total) * 100).toFixed(0)}%
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="results-controls">
                <button onClick={() => setShowExplanations(!showExplanations)}>
                    {showExplanations ? 'Hide' : 'Show'} Explanations
                </button>
            </div>

            <div className="questions-review">
                <h2>Question Review</h2>
                {results.results.map((q: any, idx: number) => {
                    const isCorrect = q.is_correct;
                    const wasAnswered = q.selected_answer !== null;

                    return (
                        <div key={idx} className={`review-card ${isCorrect ? 'correct' : 'incorrect'}`}>
                            <div className="review-header">
                                <span className="review-number">Q{idx + 1}</span>
                                <div className="review-tags">
                                    <span className="tag">{q.subject}</span>
                                    {q.topic && <span className="tag">{q.topic}</span>}
                                    <span className="tag">{q.year}</span>
                                </div>
                                <span className={`review-status ${isCorrect ? 'correct' : 'incorrect'}`}>
                                    {!wasAnswered ? '⊗ Not Attempted' : isCorrect ? '✓ Correct' : '✗ Incorrect'}
                                </span>
                            </div>

                            <div className="review-question">{q.question_text}</div>

                            <div className="review-options">
                                {['A', 'B', 'C', 'D'].map(opt => {
                                    const optionKey = `option_${opt.toLowerCase()}`;
                                    const optionText = q[optionKey];
                                    const isUserAnswer = q.selected_answer === opt;
                                    const isCorrectAnswer = q.correct_option === opt;

                                    let optionClass = 'review-option';
                                    if (isCorrectAnswer) optionClass += ' correct-answer';
                                    if (isUserAnswer && !isCorrect) optionClass += ' wrong-answer';

                                    return (
                                        <div key={opt} className={optionClass}>
                                            <span className="option-label">{opt}</span>
                                            <span className="option-text">{optionText}</span>
                                            {isCorrectAnswer && <span className="label-badge correct">✓ Correct</span>}
                                            {isUserAnswer && !isCorrect && <span className="label-badge wrong">Your Answer</span>}
                                        </div>
                                    );
                                })}
                            </div>

                            {showExplanations && q.explanation && (
                                <div className="explanation-box">
                                    <h4>Explanation</h4>
                                    <p>{q.explanation}</p>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default QuizResults;
