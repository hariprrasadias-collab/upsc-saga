// Answer Writing Practice - Main Component
import React, { useState, useEffect } from 'react';
import './AnswerWriting.css';
import { audioManager } from '../../util/AudioManager';
import { useAnalytics } from '../../contexts/AnalyticsContext';
import TemplateSelector from './TemplateSelector';

interface Prompt {
    id: number;
    question: string;
    word_limit: number;
    subject: string;
    topic: string;
    difficulty: string;
    keywords?: string;
}

interface Evaluation {
    overall_score: number;
    structure_score: number;
    content_score: number;
    relevance_score: number;
    keyword_coverage: number;
    strengths: string[];
    improvements: string[];
    missing_keywords: string[];
    word_count: number;
    word_limit: number;
    word_limit_met: boolean;
}

interface AnswerWritingProps {
    onTaskCompleted?: () => void;
}

const AnswerWriting: React.FC<AnswerWritingProps> = ({ onTaskCompleted }) => {
    const [currentPrompt, setCurrentPrompt] = useState<Prompt | null>(null);
    const [answerText, setAnswerText] = useState('');
    const [wordCount, setWordCount] = useState(0);
    const [timeElapsed, setTimeElapsed] = useState(0);
    const [isTimerRunning, setIsTimerRunning] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
    const [showEvaluation, setShowEvaluation] = useState(false);
    const [showHistory, setShowHistory] = useState(false);
    const [history, setHistory] = useState<any[]>([]);
    const [loadingHistory, setLoadingHistory] = useState(false);

    const { refreshAnalytics } = useAnalytics();

    // Fetch daily prompt on mount
    useEffect(() => {
        fetchDailyPrompt();
    }, []);

    // Timer
    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;
        if (isTimerRunning) {
            interval = setInterval(() => {
                setTimeElapsed(prev => prev + 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isTimerRunning]);

    // Word count calculator
    useEffect(() => {
        const words = answerText.trim().split(/\s+/).filter(w => w.length > 0);
        setWordCount(words.length);
    }, [answerText]);

    const fetchDailyPrompt = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/answer-writing/daily-prompt');
            if (res.ok) {
                const data = await res.json();
                setCurrentPrompt(data);
            }
        } catch (err) {
            console.error('Error fetching prompt:', err);
        }
    };

    const fetchHistory = async () => {
        setLoadingHistory(true);
        try {
            const res = await fetch('http://localhost:5000/api/answer-writing/my-answers');
            if (res.ok) {
                const data = await res.json();
                setHistory(data);
            }
        } catch (err) {
            console.error('Error fetching history:', err);
        } finally {
            setLoadingHistory(false);
        }
    };

    const toggleHistory = () => {
        if (!showHistory && history.length === 0) {
            fetchHistory();
        }
        setShowHistory(!showHistory);
        audioManager.play('click');
    };

    const startTimer = () => {
        if (!isTimerRunning) {
            setIsTimerRunning(true);
            audioManager.play('click');
        }
    };

    const pauseTimer = () => {
        setIsTimerRunning(false);
        audioManager.play('click');
    };

    const resetTimer = () => {
        setTimeElapsed(0);
        setIsTimerRunning(false);
        audioManager.play('click');
    };

    const handleSubmit = async () => {
        if (!currentPrompt || !answerText.trim()) {
            alert('Please write an answer before submitting');
            return;
        }

        setIsSubmitting(true);
        setIsTimerRunning(false);
        audioManager.play('click');

        try {
            const res = await fetch('http://localhost:5000/api/answer-writing/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt_id: currentPrompt.id,
                    answer_text: answerText,
                    time_taken: timeElapsed
                })
            });

            if (res.ok) {
                const data = await res.json();
                setEvaluation(data.evaluation);
                setShowEvaluation(true);
                audioManager.play('success');

                // Call callback to refresh dashboard XP
                if (onTaskCompleted) {
                    onTaskCompleted();
                }

                // Refresh analytics context
                refreshAnalytics(true);
            } else {
                alert('Failed to submit answer');
            }
        } catch (err) {
            console.error('Error submitting answer:', err);
            alert('Error submitting answer');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleTemplateSelect = (template: any) => {
        // Insert template example into the editor
        setAnswerText(template.example);
        audioManager.play('success');
    };

    const handleNewAttempt = () => {
        setAnswerText('');
        setWordCount(0);
        setTimeElapsed(0);
        setIsTimerRunning(false);
        setEvaluation(null);
        setShowEvaluation(false);
        fetchDailyPrompt();
        audioManager.play('click');
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const getWordCountColor = () => {
        if (!currentPrompt) return '#fff';
        const limit = currentPrompt.word_limit;
        if (wordCount > limit * 1.2) return '#e74c3c'; // Over limit (red)
        if (wordCount > limit) return '#f39c12'; // Slightly over (orange)
        if (wordCount >= limit * 0.9) return '#2ecc71'; // Near target (green)
        return '#3498db'; // Under target (blue)
    };

    if (!currentPrompt) {
        return <div className="answer-writing-container"><div className="loading">Loading prompt...</div></div>;
    }

    return (
        <div className="answer-writing-container">
            {showHistory ? (
                <div className="history-container">
                    <div className="history-header">
                        <h1>📜 Submission History</h1>
                        <button onClick={toggleHistory} className="back-btn">← Back to Practice</button>
                    </div>

                    {loadingHistory ? (
                        <div className="loading">Loading history...</div>
                    ) : history.length === 0 ? (
                        <div className="empty-state">
                            <h2>No submissions yet</h2>
                            <p>Practice answering questions to build your submission history!</p>
                            <button onClick={toggleHistory} className="start-practice-btn">
                                ✏️ Start Practicing
                            </button>
                        </div>
                    ) : (
                        <div className="history-list">
                            {history.map((item) => (
                                <div key={item.id} className="history-item">
                                    <div className="history-item-header">
                                        <span className="history-subject">{item.subject}</span>
                                        <span className="history-score">{item.overall_score?.toFixed(1) || 'N/A'}/10</span>
                                    </div>
                                    <p className="history-question">{item.question}</p>
                                    <div className="history-meta">
                                        <span>📝 {item.word_count} words</span>
                                        <span>⏱️ {Math.floor(item.time_taken / 60)}:{(item.time_taken % 60).toString().padStart(2, '0')}</span>
                                        <span>📅 {new Date(item.submitted_at).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ) : !showEvaluation ? (
                <>
                    {/* Header */}
                    <div className="aw-header">
                        <h1>✍️ Answer Writing Practice</h1>
                        <button onClick={toggleHistory} className="history-btn">
                            {showHistory ? '✏️ Back to Practice' : '📜 View History'}
                        </button>
                        <div className="aw-meta">
                            <span className="subject-badge">{currentPrompt.subject}</span>
                            <span className="difficulty-badge difficulty-{currentPrompt.difficulty.toLowerCase()}">
                                {currentPrompt.difficulty}
                            </span>
                            <span className="word-limit-badge">{currentPrompt.word_limit} words</span>
                        </div>
                    </div>

                    {/* Question */}
                    <div className="question-box">
                        <h2>Question:</h2>
                        <p className="question-text">{currentPrompt.question}</p>
                        {currentPrompt.topic && <div className="topic-tag">📌 {currentPrompt.topic}</div>}
                    </div>

                    {/* Timer and Word Count */}
                    <div className="stats-bar">
                        <div className="timer-section">
                            <span className="timer-label">Time:</span>
                            <span className="timer-display">{formatTime(timeElapsed)}</span>
                            <div className="timer-controls">
                                {!isTimerRunning ? (
                                    <button onClick={startTimer} className="timer-btn start-btn">▶ Start</button>
                                ) : (
                                    <button onClick={pauseTimer} className="timer-btn pause-btn">⏸ Pause</button>
                                )}
                                <button onClick={resetTimer} className="timer-btn reset-btn">⟲ Reset</button>
                            </div>
                        </div>

                        <div className="word-count-section">
                            <span className="word-count-label">Words:</span>
                            <span className="word-count-display" style={{ color: getWordCountColor() }}>
                                {wordCount} / {currentPrompt.word_limit}
                            </span>
                        </div>
                    </div>

                    {/* Template Selector */}
                    <TemplateSelector onSelectTemplate={handleTemplateSelect} />

                    {/* Answer Editor */}
                    <div className="answer-editor">
                        <textarea
                            value={answerText}
                            onChange={(e) => setAnswerText(e.target.value)}
                            onFocus={startTimer}
                            placeholder="Start writing your answer here... Timer will start automatically."
                            className="answer-textarea"
                            rows={15}
                        />
                    </div>

                    {/* Submit Button */}
                    <div className="submit-section">
                        <button
                            onClick={handleSubmit}
                            disabled={isSubmitting || wordCount === 0}
                            className="submit-btn"
                        >
                            {isSubmitting ? '⏳ Evaluating with AI...' : '📤 Submit for Evaluation'}
                        </button>
                    </div>
                </>
            ) : (
                <>
                    {/* Evaluation Results */}
                    <div className="evaluation-container">
                        <h1>📊 AI Evaluation Results</h1>

                        {/* Overall Score */}
                        <div className="overall-score-card">
                            <div className="score-circle">
                                <svg viewBox="0 0 100 100" className="score-svg">
                                    <circle cx="50" cy="50" r="45" fill="none" stroke="#e0e0e0" strokeWidth="8" />
                                    <circle
                                        cx="50"
                                        cy="50"
                                        r="45"
                                        fill="none"
                                        stroke="#2ecc71"
                                        strokeWidth="8"
                                        strokeDasharray={`${(evaluation!.overall_score / 10) * 283} 283`}
                                        transform="rotate(-90 50 50)"
                                    />
                                </svg>
                                <div className="score-text">
                                    <span className="score-value">{evaluation!.overall_score.toFixed(1)}</span>
                                    <span className="score-max">/10</span>
                                </div>
                            </div>
                            <h2>Overall Score</h2>
                        </div>

                        {/* Individual Scores */}
                        <div className="scores-grid">
                            <div className="score-item">
                                <span className="score-label">Structure</span>
                                <span className="score-bar">
                                    <span className="score-fill" style={{ width: `${(evaluation!.structure_score / 10) * 100}%` }}></span>
                                </span>
                                <span className="score-number">{evaluation!.structure_score.toFixed(1)}/10</span>
                            </div>

                            <div className="score-item">
                                <span className="score-label">Content</span>
                                <span className="score-bar">
                                    <span className="score-fill" style={{ width: `${(evaluation!.content_score / 10) * 100}%` }}></span>
                                </span>
                                <span className="score-number">{evaluation!.content_score.toFixed(1)}/10</span>
                            </div>

                            <div className="score-item">
                                <span className="score-label">Relevance</span>
                                <span className="score-bar">
                                    <span className="score-fill" style={{ width: `${(evaluation!.relevance_score / 10) * 100}%` }}></span>
                                </span>
                                <span className="score-number">{evaluation!.relevance_score.toFixed(1)}/10</span>
                            </div>

                            <div className="score-item">
                                <span className="score-label">Keyword Coverage</span>
                                <span className="score-bar">
                                    <span className="score-fill keyword-fill" style={{ width: `${evaluation!.keyword_coverage}%` }}></span>
                                </span>
                                <span className="score-number">{evaluation!.keyword_coverage.toFixed(0)}%</span>
                            </div>
                        </div>

                        {/* Strengths */}
                        <div className="feedback-section strengths">
                            <h3>✅ Strengths</h3>
                            <ul>
                                {evaluation!.strengths.map((strength, idx) => (
                                    <li key={idx}>{strength}</li>
                                ))}
                            </ul>
                        </div>

                        {/* Improvements */}
                        <div className="feedback-section improvements">
                            <h3>🔄 Areas to Improve</h3>
                            <ul>
                                {evaluation!.improvements.map((improvement, idx) => (
                                    <li key={idx}>{improvement}</li>
                                ))}
                            </ul>
                        </div>

                        {/* Missing Keywords */}
                        {evaluation!.missing_keywords.length > 0 && (
                            <div className="feedback-section missing-keywords">
                                <h3>🔍 Missing Keywords</h3>
                                <div className="keyword-tags">
                                    {evaluation!.missing_keywords.map((keyword, idx) => (
                                        <span key={idx} className="keyword-tag">{keyword}</span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* New Attempt Button */}
                        <div className="new-attempt-section">
                            <button onClick={handleNewAttempt} className="new-attempt-btn">
                                ✏️ Practice Another Question
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default AnswerWriting;
