import { API_BASE_URL } from '../../config';
import React, { useState, useEffect, useRef, useCallback } from 'react';

interface Question {
    id: number;
    category: string;
    topic: string;
    question_text: string;
    options: string[];
    correct_option: string;
    explanation: string;
    difficulty: string;
}

interface AnswerRecord {
    questionIndex: number;
    selected: string | null;
    correct: string;
    isCorrect: boolean;
    timeTaken: number; // seconds
}

const QUESTION_TIME_LIMIT = 90; // seconds per question

const PracticeMode: React.FC = () => {
    const [topics, setTopics] = useState<Record<string, string[]>>({});
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [selectedDifficulty, setSelectedDifficulty] = useState('');
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [showExplanation, setShowExplanation] = useState(false);
    const [selectedOption, setSelectedOption] = useState<string | null>(null);

    // Enhanced state
    const [answers, setAnswers] = useState<AnswerRecord[]>([]);
    const [sessionActive, setSessionActive] = useState(false);
    const [showSummary, setShowSummary] = useState(false);
    const [timer, setTimer] = useState(QUESTION_TIME_LIMIT);
    const [totalTime, setTotalTime] = useState(0);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const questionStartRef = useRef<number>(Date.now());

    useEffect(() => {
        fetchTopics();
    }, []);

    // Timer logic
    useEffect(() => {
        if (sessionActive && !showExplanation && !showSummary) {
            timerRef.current = setInterval(() => {
                setTimer(prev => {
                    if (prev <= 1) {
                        // Time's up — auto-skip
                        handleTimeUp();
                        return QUESTION_TIME_LIMIT;
                    }
                    return prev - 1;
                });
                setTotalTime(prev => prev + 1);
            }, 1000);
        }
        return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, [sessionActive, showExplanation, showSummary, currentQuestionIndex]);

    const handleTimeUp = useCallback(() => {
        if (selectedOption) return; // Already answered
        const timeTaken = Math.round((Date.now() - questionStartRef.current) / 1000);
        const currentQ = questions[currentQuestionIndex];
        if (!currentQ) return;

        setAnswers(prev => [...prev, {
            questionIndex: currentQuestionIndex,
            selected: null,
            correct: currentQ.correct_option,
            isCorrect: false,
            timeTaken
        }]);
        setSelectedOption('__TIMED_OUT__');
        setShowExplanation(true);
    }, [selectedOption, currentQuestionIndex, questions]);

    const fetchTopics = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/csat/topics`);
            const raw = await response.json();
            const data = raw.data || raw;
            setTopics(data || {});
        } catch (error) {
            console.error('Error fetching topics:', error);
        }
    };

    const fetchQuestions = async () => {
        if (!selectedCategory || !selectedTopic) return;
        try {
            let url = `${API_BASE_URL}/api/csat/questions?category=${encodeURIComponent(selectedCategory)}&topic=${encodeURIComponent(selectedTopic)}`;
            if (selectedDifficulty) url += `&difficulty=${encodeURIComponent(selectedDifficulty)}`;

            const response = await fetch(url);
            const raw = await response.json();
            const data = raw.success === false ? [] : (raw.data || raw);
            const qs = Array.isArray(data) ? data : [];
            setQuestions(qs);
            setCurrentQuestionIndex(0);
            setShowExplanation(false);
            setSelectedOption(null);
            setAnswers([]);
            setSessionActive(qs.length > 0);
            setShowSummary(false);
            setTimer(QUESTION_TIME_LIMIT);
            setTotalTime(0);
            questionStartRef.current = Date.now();
        } catch (error) {
            console.error('Error fetching questions:', error);
        }
    };

    const handleOptionSelect = (option: string) => {
        if (selectedOption) return;
        const timeTaken = Math.round((Date.now() - questionStartRef.current) / 1000);
        const currentQ = questions[currentQuestionIndex];
        const isCorrect = option === currentQ.correct_option;

        setSelectedOption(option);
        setShowExplanation(true);
        setAnswers(prev => [...prev, {
            questionIndex: currentQuestionIndex,
            selected: option,
            correct: currentQ.correct_option,
            isCorrect,
            timeTaken
        }]);
    };

    const nextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            setShowExplanation(false);
            setSelectedOption(null);
            setTimer(QUESTION_TIME_LIMIT);
            questionStartRef.current = Date.now();
        } else {
            setSessionActive(false);
            setShowSummary(true);
            if (timerRef.current) clearInterval(timerRef.current);
        }
    };

    const resetSession = () => {
        setQuestions([]);
        setAnswers([]);
        setSessionActive(false);
        setShowSummary(false);
        setShowExplanation(false);
        setSelectedOption(null);
        setTimer(QUESTION_TIME_LIMIT);
        setTotalTime(0);
    };

    const currentQuestion = questions[currentQuestionIndex];
    const correctCount = answers.filter(a => a.isCorrect).length;
    const incorrectCount = answers.filter(a => !a.isCorrect && a.selected !== null).length;
    const timedOutCount = answers.filter(a => a.selected === null).length;
    const progressPct = questions.length > 0 ? ((currentQuestionIndex + (showExplanation ? 1 : 0)) / questions.length) * 100 : 0;

    const formatTime = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
    const timerWarning = timer <= 15;
    const timerCritical = timer <= 5;

    // Session Summary
    if (showSummary) {
        const avgTime = answers.length > 0 ? Math.round(answers.reduce((s, a) => s + a.timeTaken, 0) / answers.length) : 0;
        const scorePct = questions.length > 0 ? Math.round((correctCount / questions.length) * 100) : 0;

        return (
            <div className="practice-mode">
                <div className="question-card" style={{ textAlign: 'center' }}>
                    <h2 style={{ color: '#f59e0b', marginBottom: '1.5rem', fontFamily: "'Cinzel', serif" }}>📊 Session Complete</h2>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
                        <div style={{ background: 'rgba(16, 185, 129, 0.15)', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: '#10b981' }}>{correctCount}</div>
                            <div style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '0.3rem' }}>Correct</div>
                        </div>
                        <div style={{ background: 'rgba(239, 68, 68, 0.15)', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: '#ef4444' }}>{incorrectCount}</div>
                            <div style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '0.3rem' }}>Wrong</div>
                        </div>
                        <div style={{ background: 'rgba(245, 158, 11, 0.15)', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: '#f59e0b' }}>{timedOutCount}</div>
                            <div style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '0.3rem' }}>Timed Out</div>
                        </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginBottom: '2rem', color: '#94a3b8' }}>
                        <span>⏱️ Total: <strong style={{ color: '#e2e8f0' }}>{formatTime(totalTime)}</strong></span>
                        <span>📈 Score: <strong style={{ color: scorePct >= 70 ? '#10b981' : scorePct >= 40 ? '#f59e0b' : '#ef4444' }}>{scorePct}%</strong></span>
                        <span>⚡ Avg: <strong style={{ color: '#e2e8f0' }}>{avgTime}s/q</strong></span>
                    </div>

                    {/* Per-question breakdown */}
                    <div style={{ textAlign: 'left', marginBottom: '2rem' }}>
                        <h3 style={{ color: '#94a3b8', marginBottom: '0.75rem', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Question Breakdown</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            {answers.map((a, i) => (
                                <div key={i} style={{
                                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                    padding: '0.5rem 0.75rem', borderRadius: '6px',
                                    background: a.isCorrect ? 'rgba(16,185,129,0.08)' : a.selected === null ? 'rgba(245,158,11,0.08)' : 'rgba(239,68,68,0.08)',
                                    borderLeft: `3px solid ${a.isCorrect ? '#10b981' : a.selected === null ? '#f59e0b' : '#ef4444'}`
                                }}>
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Q{i + 1}</span>
                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>{a.timeTaken}s</span>
                                    <span>{a.isCorrect ? '✅' : a.selected === null ? '⏰' : '❌'}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                        <button className="next-btn" onClick={fetchQuestions}>🔄 Retry Same Topic</button>
                        <button className="next-btn" onClick={resetSession} style={{ background: '#475569' }}>← Pick New Topic</button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="practice-mode">
            {/* Filter Bar */}
            <div className="filters">
                <select
                    value={selectedCategory}
                    onChange={(e) => { setSelectedCategory(e.target.value); setSelectedTopic(''); }}
                    className="csat-select"
                >
                    <option value="">
                        {Object.keys(topics).length === 0 ? "Loading categories..." : "Select Category"}
                    </option>
                    {Object.keys(topics).map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                    ))}
                </select>

                <select
                    value={selectedTopic}
                    onChange={(e) => setSelectedTopic(e.target.value)}
                    disabled={!selectedCategory}
                    className="csat-select"
                >
                    <option value="">Select Topic</option>
                    {selectedCategory && topics[selectedCategory]?.map(topic => (
                        <option key={topic} value={topic}>{topic}</option>
                    ))}
                </select>

                <select
                    value={selectedDifficulty}
                    onChange={(e) => setSelectedDifficulty(e.target.value)}
                    className="csat-select"
                >
                    <option value="">All Difficulty</option>
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                </select>

                <button
                    className="start-btn"
                    onClick={fetchQuestions}
                    disabled={!selectedCategory || !selectedTopic}
                    style={{
                        background: (!selectedCategory || !selectedTopic) ? '#475569' : 'linear-gradient(135deg, #f59e0b, #d97706)',
                        color: '#fff', border: 'none', padding: '0.5rem 1.5rem', borderRadius: '6px',
                        fontWeight: 600, cursor: (!selectedCategory || !selectedTopic) ? 'not-allowed' : 'pointer',
                    }}
                >
                    ⚔️ Start Practice
                </button>
            </div>

            {/* Active Session */}
            {questions.length > 0 && currentQuestion && !showSummary && (
                <>
                    {/* Score + Timer Bar */}
                    <div style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        marginBottom: '1rem', padding: '0.75rem 1rem',
                        background: '#0f172a', borderRadius: '10px', border: '1px solid #334155'
                    }}>
                        <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.9rem' }}>
                            <span style={{ color: '#10b981' }}>✅ {correctCount}</span>
                            <span style={{ color: '#ef4444' }}>❌ {incorrectCount}</span>
                            <span style={{ color: '#f59e0b' }}>⏰ {timedOutCount}</span>
                        </div>
                        <div style={{
                            fontSize: '1.2rem', fontWeight: 700, fontFamily: "'Courier New', monospace",
                            color: timerCritical ? '#ef4444' : timerWarning ? '#f59e0b' : '#e2e8f0',
                            animation: timerCritical ? 'wrong-shake 0.5s infinite' : undefined
                        }}>
                            ⏱️ {formatTime(timer)}
                        </div>
                        <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                            Total: {formatTime(totalTime)}
                        </span>
                    </div>

                    {/* Progress Bar */}
                    <div style={{ marginBottom: '1.5rem', background: '#1e293b', borderRadius: '6px', height: '6px', overflow: 'hidden' }}>
                        <div style={{
                            width: `${progressPct}%`, height: '100%',
                            background: 'linear-gradient(90deg, #f59e0b, #d97706)',
                            transition: 'width 0.4s ease', borderRadius: '6px'
                        }} />
                    </div>

                    {/* Question Card */}
                    <div className="question-card">
                        <div className="question-header">
                            <span className="q-number">Question {currentQuestionIndex + 1}/{questions.length}</span>
                            <span className={`difficulty ${currentQuestion.difficulty?.toLowerCase()}`}>
                                {currentQuestion.difficulty}
                            </span>
                        </div>

                        <p className="question-text">{currentQuestion.question_text}</p>

                        <div className="options-grid">
                            {currentQuestion.options.map((option, idx) => (
                                <button
                                    key={idx}
                                    className={`option-btn 
                                        ${selectedOption === option ? (option === currentQuestion.correct_option ? 'correct' : 'wrong') : ''}
                                        ${selectedOption && option === currentQuestion.correct_option ? 'correct' : ''}
                                        ${selectedOption === '__TIMED_OUT__' && option === currentQuestion.correct_option ? 'correct' : ''}
                                    `}
                                    onClick={() => handleOptionSelect(option)}
                                    disabled={!!selectedOption}
                                >
                                    {option}
                                </button>
                            ))}
                        </div>

                        {showExplanation && (
                            <div className="explanation-box">
                                {selectedOption === '__TIMED_OUT__' && (
                                    <p style={{ color: '#f59e0b', fontWeight: 700, marginBottom: '0.5rem' }}>⏰ Time's up!</p>
                                )}
                                <h3>Explanation</h3>
                                <p>{currentQuestion.explanation}</p>
                                <button className="next-btn" onClick={nextQuestion}>
                                    {currentQuestionIndex < questions.length - 1 ? 'Next Question →' : '📊 View Results'}
                                </button>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};

export default PracticeMode;
