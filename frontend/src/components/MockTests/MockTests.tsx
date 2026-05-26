import { API_BASE_URL } from '../../config';

// Mock Tests - Main Container
import React, { useState, useEffect } from 'react';
import './MockTests.css';
import { useAnalytics } from '../../contexts/AnalyticsContext';
import { brainService } from '../../services/BrainService';

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
    const { refreshAnalytics } = useAnalytics();
    const [isGenerating, setIsGenerating] = useState(false);

    // Add Test Modal State
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [newTest, setNewTest] = useState({
        title: '',
        subject: '',
        description: '',
        difficulty: 'Medium',
        questionsJson: ''
    });

    // Fetch available tests
    const fetchTests = () => {
        fetch(`${API_BASE_URL}/api/mock-tests`)
            .then(r => r.json())
            .then(raw => {
                const data = raw.success === false ? [] : (raw.data || raw);
                console.log('Fetched tests:', data);
                setTests(Array.isArray(data) ? data : []);
            })
            .catch(err => console.error(err));
    };

    useEffect(() => {
        if (view === 'list') {
            fetchTests();
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
        console.log('Starting test:', test);
        try {
            const res = await fetch(`${API_BASE_URL}/api/mock-tests/${test.id}/start`, {
                method: 'POST'
            });

            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const raw = await res.json();
            const data = raw.data || raw;
            console.log('Test data received:', data);

            if (!data.questions || data.questions.length === 0) {
                alert('This test has no questions available. Please try another test.');
                return;
            }

            setCurrentTest(test);
            setQuestions(data.questions);
            setAttemptId(data.attempt_id);
            setTimeLeft(test.duration_minutes * 60);
            setCurrentQ(0);
            setAnswers({});
            setView('test');
        } catch (err) {
            console.error('Error starting test:', err);
            alert(`Failed to start test: ${err instanceof Error ? err.message : 'Unknown error'}`);
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
                await fetch(`${API_BASE_URL}/api/mock-tests/attempt/${attemptId}/answer`, {
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
            const res = await fetch(`${API_BASE_URL}/api/mock-tests/attempt/${attemptId}/submit`, {
                method: 'POST'
            });
            const raw = await res.json();
            const data = raw.data || raw;

            // Fetch detailed results
            const resultRes = await fetch(`${API_BASE_URL}/api/mock-tests/attempt/${attemptId}/results`);
            const rawResult = await resultRes.json();
            const resultData = rawResult.data || rawResult;

            setResults({ ...data, ...resultData });
            setView('results');

            // Call callback to refresh dashboard XP
            if (onTaskCompleted) {
                onTaskCompleted();
            }
            refreshAnalytics(true);
        } catch (err) {
            console.error(err);
            alert('Failed to submit test');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleCreateTest = async () => {
        try {
            let questions = [];
            try {
                questions = JSON.parse(newTest.questionsJson);
            } catch (e) {
                alert('Invalid JSON format for questions');
                return;
            }

            if (!Array.isArray(questions) || questions.length === 0) {
                alert('Questions must be a non-empty array');
                return;
            }

            const res = await fetch(`${API_BASE_URL}/api/mock-tests`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: newTest.title,
                    subject: newTest.subject,
                    description: newTest.description,
                    difficulty: newTest.difficulty,
                    questions: questions
                })
            });

            if (res.ok) {
                alert('Test Created Successfully!');
                setIsAddModalOpen(false);
                setNewTest({ title: '', subject: '', description: '', difficulty: 'Medium', questionsJson: '' });
                fetchTests();
            } else {
                const err = await res.json();
                alert(`Failed to create test: ${err.error}`);
            }
        } catch (err) {
            console.error(err);
            alert('Error creating test');
        }
    };

    const handleGenerateSmartTest = async () => {
        setIsGenerating(true);
        try {
            const result = await brainService.executeAction('CREATE_MOCK_TEST', { topic: 'Weak Areas', count: 10 });
            if (result.success) {
                alert(result.message);
                fetchTests();
            } else {
                alert("Failed to generate test: " + result.message);
            }
        } catch (err) {
            console.error("Smart Test Generation Error:", err);
            alert("The Oracle is silent.");
        } finally {
            setIsGenerating(false);
        }
    };

    const deleteTest = async (testId: number, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!window.confirm('Are you sure you want to delete this test? This action cannot be undone.')) {
            return;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/api/mock-tests/${testId}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                setTests(tests.filter(t => t.id !== testId));
            } else {
                const err = await res.json();
                alert(`Failed to delete test: ${err.error}`);
            }
        } catch (err) {
            console.error('Error deleting test:', err);
            alert('Error deleting test');
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
                <div className="mock-header">
                    <h1>📋 Mock Tests</h1>
                    <button className="add-test-btn" onClick={() => setIsAddModalOpen(true)}>
                        <span>+</span> Create New Test
                    </button>
                    <button
                        className="add-test-btn smart-test-btn"
                        onClick={handleGenerateSmartTest}
                        disabled={isGenerating}
                        style={{ marginLeft: '10px', background: 'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)' }}
                    >
                        {isGenerating ? 'Forging Test...' : '🧠 Generate Smart Test'}
                    </button>
                </div>

                <div className="tests-grid">
                    {tests.map(test => (
                        <div key={test.id} className="test-card">
                            <h3>{test.title}</h3>
                            <p>{test.description}</p>
                            <div className="test-meta">
                                <span>📝 {test.total_questions} Qs</span>
                                <span>⏱️ {test.duration_minutes}m</span>
                                <span className={`difficulty ${test.difficulty?.toLowerCase() || 'medium'}`}>
                                    {test.difficulty || 'Medium'}
                                </span>
                            </div>
                            <div className="card-actions" style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
                                <button onClick={() => startTest(test)} className="start-btn" style={{ flex: 1 }}>
                                    Start Test
                                </button>
                                <button
                                    onClick={(e) => deleteTest(test.id, e)}
                                    className="delete-btn"
                                    style={{
                                        padding: '10px',
                                        background: '#ff4757',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '8px',
                                        cursor: 'pointer'
                                    }}
                                    title="Delete Test"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {isAddModalOpen && (
                    <div className="modal-overlay" onClick={(e) => {
                        if (e.target === e.currentTarget) setIsAddModalOpen(false);
                    }}>
                        <div className="modal-content">
                            <div className="modal-header">
                                <h2>Create New Mock Test</h2>
                                <button aria-label="Close" className="close-modal-btn" onClick={() => setIsAddModalOpen(false)}><span aria-hidden="true">×</span></button>
                            </div>
                            <div className="modal-body">
                                <div className="form-group">
                                    <label>Title</label>
                                    <input
                                        type="text"
                                        value={newTest.title}
                                        onChange={e => setNewTest({ ...newTest, title: e.target.value })}
                                        placeholder="e.g., Ancient History Full Test"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Subject</label>
                                    <input
                                        type="text"
                                        value={newTest.subject}
                                        onChange={e => setNewTest({ ...newTest, subject: e.target.value })}
                                        placeholder="e.g., History"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Description</label>
                                    <textarea
                                        value={newTest.description}
                                        onChange={e => setNewTest({ ...newTest, description: e.target.value })}
                                        placeholder="Brief description of the test..."
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Difficulty</label>
                                    <select
                                        value={newTest.difficulty}
                                        onChange={e => setNewTest({ ...newTest, difficulty: e.target.value })}
                                    >
                                        <option value="Easy">Easy</option>
                                        <option value="Medium">Medium</option>
                                        <option value="Hard">Hard</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Questions (JSON Format)</label>
                                    <textarea
                                        value={newTest.questionsJson}
                                        onChange={e => setNewTest({ ...newTest, questionsJson: e.target.value })}
                                        placeholder='[{"question_text": "...", "option_a": "...", "correct_answer": "A"}]'
                                        rows={8}
                                        style={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
                                    />
                                    <small style={{ color: '#888' }}>
                                        Paste a JSON array of question objects. Each object must have: question_text, option_a, option_b, option_c, option_d, correct_answer (A/B/C/D).
                                    </small>
                                </div>
                                <div className="modal-actions">
                                    <button className="cancel-btn" onClick={() => setIsAddModalOpen(false)}>Cancel</button>
                                    <button className="create-btn" onClick={handleCreateTest}>Create Test</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
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
                    <div className="timer" style={{ color: timeLeft < 300 ? '#e74c3c' : 'var(--color-accent-blue)' }}>
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
