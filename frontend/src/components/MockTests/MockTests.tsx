// Mock Tests - Main Container
import React, { useState, useEffect } from 'react';
import './MockTests.css';

interface Test {
    id: number;
    title: string;
    description: string;
    total_questions: number;
    duration_minutes: number;
    difficulty: string;
}

interface Question {
    id: number;
    question_number: number;
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    subject?: string;
}

interface Answer {
    question_id: number;
    selected_answer: string | null;
    is_marked: boolean;
}

interface MockTestsProps {
    onTaskCompleted?: () => void;
}

const MockTests: React.FC<MockTestsProps> = ({ onTaskCompleted }) => {
    const [tests, setTests] = useState<Test[]>([]);
    const [currentTest, setCurrentTest] = useState<Test | null>(null);
    const [questions, setQuestions] = useState<Question[]>([]);
    const [attemptId, setAttemptId] = useState<number | null>(null);
    const [answers, setAnswers] = useState<Record<number, Answer>>({});
    const [currentQ, setCurrentQ] = useState(0);
    const [timeLeft, setTimeLeft] = useState(0);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [results, setResults] = useState<any>(null);
    const [view, setView] = useState<'list' | 'test' | 'results'>('list');

    // Fetch available tests
    useEffect(() => {
        if (view === 'list') {
            fetch('http://localhost:5000/api/mock-tests')
                .then(r => r.json())
                .then(data => setTests(data))
                .catch(err => console.error(err));
        }
    }, [view]);

    // Timer
    useEffect(() => {
        if (view === 'test' && timeLeft > 0) {
            const timer = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) {
                        handleSubmit();
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
            return () => clearInterval(timer);
        }
    }, [view, timeLeft]);

    const startTest = async (test: Test) => {
        try {
            const res = await fetch(`http://localhost:5000/api/mock-tests/${test.id}/start`, {
                method: 'POST'
            });
            const data = await res.json();

            setCurrentTest(test);
            setQuestions(data.questions);
            setAttemptId(data.attempt_id);
            setTimeLeft(test.duration_minutes * 60);
            setCurrentQ(0);
            setAnswers({});
            setView('test');
        } catch (err) {
            console.error(err);
            alert('Failed to start test');
        }
    };

    const saveAnswer = async (questionId: number, answer: string | null, marked: boolean = false) => {
        const newAnswers = {
            ...answers,
            [questionId]: { question_id: questionId, selected_answer: answer, is_marked: marked }
        };
        setAnswers(newAnswers);

        if (attemptId) {
            try {
                await fetch(`http://localhost:5000/api/mock-tests/attempt/${attemptId}/answer`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        question_id: questionId,
                        selected_answer: answer,
                        is_marked: marked
                    })
                });
            } catch (err) {
                console.error('Failed to save answer:', err);
            }
        }
    };

    const handleSubmit = async () => {
        if (!attemptId || isSubmitting) return;

        if (!window.confirm('Submit test? You cannot change answers after submission.')) {
            return;
        }

        setIsSubmitting(true);

        try {
            const res = await fetch(`http://localhost:5000/api/mock-tests/attempt/${attemptId}/submit`, {
                method: 'POST'
            });
            const data = await res.json();

            // Fetch detailed results
            const resultRes = await fetch(`http://localhost:5000/api/mock-tests/attempt/${attemptId}/results`);
            const resultData = await resultRes.json();

            setResults({ ...data, ...resultData });
            setView('results');

            // Call callback to refresh dashboard XP
            if (onTaskCompleted) {
                onTaskCompleted();
            }
        } catch (err) {
            console.error(err);
            alert('Failed to submit test');
        } finally {
            setIsSubmitting(false);
        }
    };

    const formatTime = (seconds: number) => {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return hrs > 0
            ? `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
            : `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const getOMRClass = (qId: number) => {
        const ans = answers[qId];
        if (!ans) return 'not-visited';
        if (ans.is_marked) return 'marked';
        if (ans.selected_answer) return 'answered';
        return 'visited';
    };

    if (view === 'list') {
        return (
            <div className="mock-tests-container">
                <h1>📋 Mock Tests</h1>
                <div className="tests-grid">
                    {tests.map(test => (
                        <div key={test.id} className="test-card">
                            <h3>{test.title}</h3>
                            <p>{test.description}</p>
                            <div className="test-meta">
                                <span>📝 {test.total_questions} Questions</span>
                                <span>⏱️ {test.duration_minutes} mins</span>
                                <span className={`difficulty ${test.difficulty.toLowerCase()}`}>
                                    {test.difficulty}
                                </span>
                            </div>
                            <button onClick={() => startTest(test)} className="start-btn">
                                Start Test
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (view === 'test' && currentTest && questions.length > 0) {
        const q = questions[currentQ];
        const currentAnswer = answers[q.id];

        return (
            <div className="test-interface">
                {/* Header */}
                <div className="test-header">
                    <div className="test-info">
                        <span>{currentTest.title}</span>
                        <span>Question {currentQ + 1}/{questions.length}</span>
                    </div>
                    <div className="timer" style={{ color: timeLeft < 300 ? '#e74c3c' : '#fff' }}>
                        ⏱️ {formatTime(timeLeft)}
                    </div>
                    <button onClick={handleSubmit} className="submit-test-btn" disabled={isSubmitting}>
                        {isSubmitting ? 'Submitting...' : 'Submit Test'}
                    </button>
                </div>

                {/* Question */}
                <div className="question-area">
                    <div className="question-header">
                        <h3>Question {q.question_number}</h3>
                        {q.subject && <span className="subject-tag">{q.subject}</span>}
                    </div>
                    <p className="question-text">{q.question_text}</p>

                    {/* Options */}
                    <div className="options">
                        {['A', 'B', 'C', 'D'].map(opt => (
                            <label key={opt} className={`option ${currentAnswer?.selected_answer === opt ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    name="answer"
                                    checked={currentAnswer?.selected_answer === opt}
                                    onChange={() => saveAnswer(q.id, opt)}
                                />
                                <span className="option-label">{opt}.</span>
                                <span className="option-text">{q[`option_${opt.toLowerCase()}` as keyof Question]}</span>
                            </label>
                        ))}
                    </div>

                    {/* Actions */}
                    <div className="question-actions">
                        <button
                            onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
                            disabled={currentQ === 0}
                            className="nav-btn"
                        >
                            ← Previous
                        </button>

                        <button
                            onClick={() => saveAnswer(q.id, currentAnswer?.selected_answer || null, !currentAnswer?.is_marked)}
                            className={`mark-btn ${currentAnswer?.is_marked ? 'marked' : ''}`}
                        >
                            {currentAnswer?.is_marked ? '⚠ Marked' : 'Mark for Review'}
                        </button>

                        <button
                            onClick={() => saveAnswer(q.id, null)}
                            className="clear-btn"
                        >
                            Clear Answer
                        </button>

                        <button
                            onClick={() => setCurrentQ(Math.min(questions.length - 1, currentQ + 1))}
                            disabled={currentQ === questions.length - 1}
                            className="nav-btn"
                        >
                            Next →
                        </button>
                    </div>
                </div>

                {/* OMR Sheet */}
                <div className="omr-sheet">
                    <h4>OMR Sheet</h4>
                    <div className="omr-grid">
                        {questions.map((question, idx) => (
                            <button
                                key={question.id}
                                onClick={() => setCurrentQ(idx)}
                                className={`omr-cell ${getOMRClass(question.id)} ${idx === currentQ ? 'current' : ''}`}
                            >
                                {question.question_number}
                            </button>
                        ))}
                    </div>
                    <div className="omr-legend">
                        <span><span className="legend-box answered"></span> Answered</span>
                        <span><span className="legend-box marked"></span> Marked</span>
                        <span><span className="legend-box visited"></span> Not Answered</span>
                        <span><span className="legend-box not-visited"></span> Not Visited</span>
                    </div>
                </div>
            </div>
        );
    }

    if (view === 'results' && results) {
        return (
            <div className="results-container">
                <h1>📊 Test Results</h1>

                {/* Score Card */}
                <div className="score-card">
                    <div className="score-circle">
                        <div className="score">{results.score.toFixed(2)}</div>
                        <div className="max-score">/ {results.max_score}</div>
                    </div>
                    <div className="percentage">{results.percentage.toFixed(1)}%</div>
                </div>

                {/* Breakdown */}
                <div className="breakdown-grid">
                    <div className="stat-box correct">
                        <div className="number">{results.correct}</div>
                        <div className="label">Correct</div>
                    </div>
                    <div className="stat-box incorrect">
                        <div className="number">{results.incorrect}</div>
                        <div className="label">Incorrect</div>
                    </div>
                    <div className="stat-box unattempted">
                        <div className="number">{results.unattempted}</div>
                        <div className="label">Unattempted</div>
                    </div>
                    <div className="stat-box accuracy">
                        <div className="number">{results.accuracy.toFixed(1)}%</div>
                        <div className="label">Accuracy</div>
                    </div>
                </div>

                {/* Subject-wise */}
                {results.subject_stats && (
                    <div className="subject-stats">
                        <h3>Subject-wise Performance</h3>
                        {results.subject_stats.map((s: any) => (
                            <div key={s.subject} className="subject-row">
                                <span>{s.subject}</span>
                                <span>{s.correct}/{s.total}</span>
                                <div className="progress-bar">
                                    <div className="progress-fill" style={{ width: `${(s.correct / s.total) * 100}%` }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Actions */}
                <div className="results-actions">
                    <button onClick={() => setView('list')} className="back-btn">
                        Back to Tests
                    </button>
                </div>
            </div>
        );
    }

    return <div className="loading">Loading...</div>;
};

export default MockTests;
