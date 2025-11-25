// QuizSession.tsx - Interactive Quiz Mode
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './QuizSession.css';

interface Question {
    id: number;
    question_id: number;
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    correct_option: string;
    explanation: string;
    subject: string;
    topic: string;
    year: number;
    difficulty: string;
    selected_answer?: string;
    marked_for_review?: boolean;
}

const QuizSession: React.FC = () => {
    const { sessionId } = useParams<{ sessionId: string }>();
    const navigate = useNavigate();

    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [answers, setAnswers] = useState<Map<number, string>>(new Map());
    const [markedForReview, setMarkedForReview] = useState<Set<number>>(new Set());
    const [startTime] = useState(new Date());
    const [questionStartTime, setQuestionStartTime] = useState<Date>(new Date());
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [showPalette, setShowPalette] = useState(false);

    // Fetch quiz session on mount
    useEffect(() => {
        const fetchSession = async () => {
            try {
                const res = await fetch(`http://localhost:5000/api/pyq/quiz/${sessionId}`);
                const data = await res.json();
                if (data.questions && Array.isArray(data.questions)) {
                    setQuestions(data.questions);
                } else {
                    console.error('Invalid quiz data:', data);
                }
                setLoading(false);
            } catch (err) {
                console.error('Failed to load quiz session', err);
                setLoading(false);
            }
        };
        fetchSession();
    }, [sessionId]);

    // Track time spent on each question
    useEffect(() => {
        setQuestionStartTime(new Date());
    }, [currentIndex]);

    const currentQuestion = questions?.[currentIndex];

    const handleSelectAnswer = (option: string) => {
        if (!currentQuestion) return;

        const newAnswers = new Map(answers);
        newAnswers.set(currentQuestion.question_id, option);
        setAnswers(newAnswers);

        // Save answer to backend
        const timeDiff = Math.floor((new Date().getTime() - questionStartTime.getTime()) / 1000);
        fetch(`http://localhost:5000/api/pyq/quiz/${sessionId}/answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: currentQuestion.question_id,
                selected_answer: option,
                time_spent: timeDiff,
                marked_for_review: markedForReview.has(currentQuestion.question_id)
            })
        });
    };

    const handleMarkForReview = () => {
        if (!currentQuestion) return;

        const newMarked = new Set(markedForReview);
        if (newMarked.has(currentQuestion.question_id)) {
            newMarked.delete(currentQuestion.question_id);
        } else {
            newMarked.add(currentQuestion.question_id);
        }
        setMarkedForReview(newMarked);
    };

    const handleNext = () => {
        if (currentIndex < questions.length - 1) {
            setCurrentIndex(currentIndex + 1);
        }
    };

    const handlePrevious = () => {
        if (currentIndex > 0) {
            setCurrentIndex(currentIndex - 1);
        }
    };

    const handleJumpTo = (index: number) => {
        setCurrentIndex(index);
        setShowPalette(false);
    };

    const handleSubmit = async () => {
        const confirmSubmit = window.confirm(
            `You have answered ${answers.size} out of ${questions.length} questions. Submit quiz?`
        );

        if (!confirmSubmit) return;

        setSubmitting(true);
        try {
            const res = await fetch(`http://localhost:5000/api/pyq/quiz/${sessionId}/submit`, {
                method: 'POST'
            });
            const data = await res.json();

            // Navigate to results page
            navigate(`/pyq-quiz-results/${sessionId}`, { state: { results: data } });
        } catch (err) {
            console.error('Failed to submit quiz', err);
            setSubmitting(false);
        }
    };

    const getElapsedTime = () => {
        const elapsed = Math.floor((new Date().getTime() - startTime.getTime()) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    const getQuestionStatus = (index: number) => {
        const q = questions?.[index];
        if (!q) return 'unanswered';

        if (answers.has(q.question_id)) return 'answered';
        if (markedForReview.has(q.question_id)) return 'marked';
        return 'unanswered';
    };

    if (loading) {
        return <div className="quiz-loading">Loading Quiz...</div>;
    }

    if (!currentQuestion) {
        return <div className="quiz-error">No questions found</div>;
    }

    return (
        <div className="quiz-container">
            <div className="quiz-header">
                <div className="quiz-info">
                    <span className="question-counter">{currentIndex + 1} / {questions.length}</span>
                    <span className="quiz-timer">⏱️ {getElapsedTime()}</span>
                </div>
                <div className="quiz-actions">
                    <button
                        className="palette-btn"
                        onClick={() => setShowPalette(!showPalette)}
                    >
                        {showPalette ? 'Hide' : 'Show'} Questions
                    </button>
                    <button
                        className="submit-btn"
                        onClick={handleSubmit}
                        disabled={submitting}
                    >
                        {submitting ? 'Submitting...' : 'Submit Quiz'}
                    </button>
                </div>
            </div>

            <div className="quiz-content">
                {showPalette && (
                    <div className="question-palette">
                        <h3>All Questions</h3>
                        <div className="palette-grid">
                            {questions.map((_, idx) => (
                                <button
                                    key={idx}
                                    className={`palette-item ${getQuestionStatus(idx)} ${idx === currentIndex ? 'current' : ''}`}
                                    onClick={() => handleJumpTo(idx)}
                                >
                                    {idx + 1}
                                </button>
                            ))}
                        </div>
                        <div className="palette-legend">
                            <span className="legend-item"><span className="dot answered"></span> Answered</span>
                            <span className="legend-item"><span className="dot marked"></span> Marked</span>
                            <span className="legend-item"><span className="dot unanswered"></span> Not Answered</span>
                        </div>
                    </div>
                )}

                <div className="question-main">
                    <div className="question-meta">
                        <span className="tag">{currentQuestion.subject}</span>
                        {currentQuestion.topic && <span className="tag topic">{currentQuestion.topic}</span>}
                        <span className="tag">{currentQuestion.year}</span>
                        <span className="tag">{currentQuestion.difficulty}</span>
                    </div>

                    <div className="question-text">
                        {currentQuestion.question_text}
                    </div>

                    <div className="options-grid">
                        {['A', 'B', 'C', 'D'].map(opt => {
                            const optionKey = `option_${opt.toLowerCase()}` as keyof Question;
                            const optionText = currentQuestion[optionKey];
                            const isSelected = answers.get(currentQuestion.question_id) === opt;

                            return (
                                <button
                                    key={opt}
                                    className={`option-btn ${isSelected ? 'selected' : ''}`}
                                    onClick={() => handleSelectAnswer(opt)}
                                >
                                    <span className="option-label">{opt}</span>
                                    <span className="option-text">{optionText}</span>
                                </button>
                            );
                        })}
                    </div>

                    <div className="question-controls">
                        <button
                            className="mark-btn"
                            onClick={handleMarkForReview}
                        >
                            {markedForReview.has(currentQuestion.question_id) ? '★ Marked' : '☆ Mark for Review'}
                        </button>

                        <div className="navigation-btns">
                            <button
                                onClick={handlePrevious}
                                disabled={currentIndex === 0}
                            >
                                ← Previous
                            </button>
                            <button
                                onClick={handleNext}
                                disabled={currentIndex === questions.length - 1}
                            >
                                Next →
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default QuizSession;
