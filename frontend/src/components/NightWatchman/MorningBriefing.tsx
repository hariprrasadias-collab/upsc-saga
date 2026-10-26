import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './MorningBriefing.css';

interface Briefing {
    id: number;
    date: string;
    summary: string;
    quote: string;
    articles_analyzed: number;
    mind_map?: string;
    static_linkage?: string;
    is_read: boolean;
    quiz_data?: string; // JSON string from DB
    quiz?: QuizQuestion[]; // Parsed object
}

interface QuizQuestion {
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
}

const MorningBriefing: React.FC = () => {
    const [briefing, setBriefing] = useState<Briefing | null>(null);
    const [loading, setLoading] = useState(false);
    const [triggering, setTriggering] = useState(false);
    const [history, setHistory] = useState<any[]>([]);
    const [showHistory, setShowHistory] = useState(false);
    const [speaking, setSpeaking] = useState(false);

    // Quiz State
    const [quizMode, setQuizMode] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [showResults, setShowResults] = useState(false);
    const [selectedOption, setSelectedOption] = useState<string | null>(null);
    const [quizFeedback, setQuizFeedback] = useState<string | null>(null);

    useEffect(() => {
        fetchLatestBriefing();
        fetchHistory();
    }, []);

    const fetchLatestBriefing = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/night-watchman/latest`);
            const data = await response.json();
            if (data.success && data.briefing) {
                // Parse quiz data if available
                let parsedQuiz = [];
                if (data.briefing.quiz_data) {
                    try {
                        parsedQuiz = JSON.parse(data.briefing.quiz_data);
                    } catch (e) {
                        console.error("Failed to parse quiz data", e);
                    }
                }
                setBriefing({ ...data.briefing, quiz: parsedQuiz });
            } else {
                setBriefing(null);
            }
        } catch (error) {
            console.error("Failed to fetch briefing:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchHistory = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/night-watchman/history`);
            const data = await response.json();
            if (data.success) {
                setHistory(data.history);
            }
        } catch (error) {
            console.error("Failed to fetch history:", error);
        }
    };

    const fetchBriefingById = async (id: number) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/night-watchman/briefing/${id}`);
            const data = await response.json();
            if (data.success && data.briefing) {
                let parsedQuiz = [];
                if (data.briefing.quiz_data) {
                    try {
                        parsedQuiz = JSON.parse(data.briefing.quiz_data);
                    } catch (e) {
                        console.error("Failed to parse quiz data", e);
                    }
                }
                setBriefing({ ...data.briefing, quiz: parsedQuiz });
                setShowHistory(false);
            }
        } catch (error) {
            console.error("Failed to fetch briefing:", error);
        } finally {
            setLoading(false);
        }
    };

    const triggerWatchman = async () => {
        setTriggering(true);
        try {
            const response = await fetch(`${API_BASE_URL}/night-watchman/trigger`, {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                fetchLatestBriefing();
                fetchHistory();
            } else {
                alert("Watchman failed to report: " + data.message);
            }
        } catch (error) {
            console.error("Trigger failed:", error);
            alert("Failed to contact Night Watchman.");
        } finally {
            setTriggering(false);
        }
    };

    const markAsRead = async () => {
        if (!briefing) return;
        try {
            await fetch(`${API_BASE_URL}/night-watchman/mark-read/${briefing.id}`, {
                method: 'POST'
            });
            setBriefing({ ...briefing, is_read: true });
            fetchHistory(); // Update history list status
        } catch (error) {
            console.error("Failed to mark as read:", error);
        }
    };

    const togglePodcastMode = () => {
        if (speaking) {
            window.speechSynthesis.cancel();
            setSpeaking(false);
        } else {
            if (!briefing) return;
            const utterance = new SpeechSynthesisUtterance(briefing.summary);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.onend = () => setSpeaking(false);
            window.speechSynthesis.speak(utterance);
            setSpeaking(true);
        }
    };

    // Quiz Functions
    const startQuiz = () => {
        setQuizMode(true);
        setCurrentQuestionIndex(0);
        setScore(0);
        setShowResults(false);
        setSelectedOption(null);
        setQuizFeedback(null);
    };

    const handleOptionSelect = (option: string) => {
        if (selectedOption) return; // Prevent multiple selections
        setSelectedOption(option);

        const currentQ = briefing?.quiz?.[currentQuestionIndex];
        if (currentQ) {
            const isCorrect = option === currentQ.correct_answer;
            if (isCorrect) setScore(s => s + 1);
            setQuizFeedback(isCorrect ? "✅ Correct!" : `❌ Incorrect. The answer is ${currentQ.correct_answer}.`);
        }
    };

    const nextQuestion = () => {
        if (!briefing?.quiz) return;

        if (currentQuestionIndex < briefing.quiz.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            setSelectedOption(null);
            setQuizFeedback(null);
        } else {
            setShowResults(true);
        }
    };

    const closeQuiz = () => {
        setQuizMode(false);
    };

    return (
        <div className="morning-briefing-container">
            <div className="briefing-header">
                <div>
                    <h1>🦉 The Night Watchman</h1>
                    <p className="subtitle">Autonomous Research & Intelligence Briefing</p>
                </div>
                <div className="header-actions">
                    <button
                        className={`history-toggle ${showHistory ? 'active' : ''}`}
                        onClick={() => setShowHistory(!showHistory)}
                    >
                        📜 Archives
                    </button>
                    <button
                        className="trigger-btn"
                        onClick={triggerWatchman}
                        disabled={triggering}
                    >
                        {triggering ? '🌙 Patrolling...' : '🌙 Force Patrol'}
                    </button>
                </div>
            </div>

            <div className="briefing-layout">
                {showHistory && (
                    <div className="history-sidebar">
                        <h3>Past Briefings</h3>
                        <div className="history-list">
                            {history.map(item => (
                                <div
                                    key={item.id}
                                    className={`history-item ${briefing?.id === item.id ? 'active' : ''} ${item.is_read ? 'read' : 'unread'}`}
                                    onClick={() => fetchBriefingById(item.id)}
                                >
                                    <span className="history-date">{item.date}</span>
                                    <span className="history-status">{item.is_read ? '✅' : '🆕'}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="briefing-main">
                    {loading ? (
                        <div className="loading-state">
                            <div className="owl-loader"></div>
                            <p>Retrieving Intelligence...</p>
                        </div>
                    ) : briefing ? (
                        <div className={`briefing-content ${briefing.is_read ? 'read' : 'unread'}`}>
                            <div className="briefing-meta">
                                <span className="date-badge">📅 {briefing.date}</span>
                                <span className="source-badge">📡 {briefing.articles_analyzed} Sources Analyzed</span>
                                <button className={`podcast-btn ${speaking ? 'active' : ''}`} onClick={togglePodcastMode}>
                                    {speaking ? '🔇 Stop Audio' : '🎧 Podcast Mode'}
                                    {speaking && (
                                        <div className="audio-visualizer">
                                            <div className="bar"></div>
                                            <div className="bar"></div>
                                            <div className="bar"></div>
                                            <div className="bar"></div>
                                        </div>
                                    )}
                                </button>
                            </div>

                            <div className="quote-section">
                                <blockquote>"{briefing.quote}"</blockquote>
                            </div>

                            {briefing.static_linkage && (
                                <div className="static-linkage-card">
                                    <h4>🔗 Static Syllabus Linkage</h4>
                                    <p>{briefing.static_linkage}</p>
                                </div>
                            )}

                            <div className="markdown-content">
                                <ReactMarkdown>{briefing.summary}</ReactMarkdown>
                            </div>

                            {briefing.mind_map && (
                                <div className="mind-map-section">
                                    <h4>🧠 Visual Intelligence (Mind Map)</h4>
                                    <pre className="mermaid-code">
                                        {briefing.mind_map}
                                    </pre>
                                </div>
                            )}

                            <div className="briefing-actions">
                                {!briefing.is_read && (
                                    <button className="action-btn primary" onClick={markAsRead}>
                                        ✅ Mark as Read
                                    </button>
                                )}
                                {briefing.quiz && briefing.quiz.length > 0 && (
                                    <button className="action-btn secondary" onClick={startQuiz}>
                                        📝 Take Daily Quiz
                                    </button>
                                )}
                            </div>

                            {/* Quiz Modal Overlay */}
                            {quizMode && briefing.quiz && (
                                <div className="quiz-overlay">
                                    <div className="quiz-modal">
                                        <button aria-label="Close" className="close-quiz-btn" onClick={closeQuiz}>×</button>

                                        {!showResults ? (
                                            <>
                                                <div className="quiz-header">
                                                    <h3>Daily Intelligence Test</h3>
                                                    <span className="quiz-progress">
                                                        Question {currentQuestionIndex + 1} / {briefing.quiz.length}
                                                    </span>
                                                </div>

                                                <div className="quiz-question">
                                                    <p>{briefing.quiz[currentQuestionIndex].question}</p>
                                                </div>

                                                <div className="quiz-options">
                                                    {briefing.quiz[currentQuestionIndex].options.map((opt: string, idx: number) => (
                                                        <button
                                                            key={idx}
                                                            className={`quiz-option ${selectedOption === opt ? (opt === briefing.quiz![currentQuestionIndex].correct_answer ? 'correct' : 'wrong') : ''} ${selectedOption && opt === briefing.quiz![currentQuestionIndex].correct_answer ? 'correct' : ''}`}
                                                            onClick={() => handleOptionSelect(opt)}
                                                            disabled={!!selectedOption}
                                                        >
                                                            {opt}
                                                        </button>
                                                    ))}
                                                </div>

                                                {quizFeedback && (
                                                    <div className="quiz-feedback">
                                                        <p>{quizFeedback}</p>
                                                        <p className="explanation">{briefing.quiz[currentQuestionIndex].explanation}</p>
                                                        <button className="next-btn" onClick={nextQuestion}>
                                                            {currentQuestionIndex < briefing.quiz.length - 1 ? 'Next Question' : 'View Results'}
                                                        </button>
                                                    </div>
                                                )}
                                            </>
                                        ) : (
                                            <div className="quiz-results">
                                                <h3>Quiz Complete!</h3>
                                                <div className="score-circle">
                                                    <span>{score} / {briefing.quiz.length}</span>
                                                </div>
                                                <p>{score === briefing.quiz.length ? "🌟 Perfect Score! Excellent retention." : "Keep reading! Review the briefing again."}</p>

                                                {score === briefing.quiz.length && (
                                                    <div className="confetti-container">
                                                        <p style={{ color: '#10b981', marginTop: '1rem', fontWeight: 'bold' }}>🎉 PERFECT SCORE BONUS UNLOCKED 🎉</p>
                                                    </div>
                                                )}

                                                <button className="close-quiz-btn-main" onClick={closeQuiz}>Close Quiz</button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <div className="owl-icon">🦉</div>
                            <h2>The Watchman is sleeping.</h2>
                            <p>Trigger a patrol to gather intelligence.</p>
                            <button className="trigger-btn large" onClick={triggerWatchman} disabled={triggering}>
                                {triggering ? '🌙 Patrolling...' : '🌙 Begin Night Patrol'}
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MorningBriefing;
