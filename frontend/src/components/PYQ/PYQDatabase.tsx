// /frontend/src/components/PYQ/PYQDatabase.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './PYQDatabase.css';

interface Question {
    id: number;
    year: number;
    subject: string;
    topic: string;
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    correct_option: string;
    explanation: string;
    difficulty: string;
    is_favorite: boolean;
}

interface Analytics {
    by_subject: { subject: string; count: number }[];
    by_year: { year: number; count: number }[];
}

const PYQDatabase: React.FC = () => {
    const navigate = useNavigate();
    const [questions, setQuestions] = useState<Question[]>([]);
    const [analytics, setAnalytics] = useState<Analytics | null>(null);
    const [loading, setLoading] = useState(true);
    const [startingQuiz, setStartingQuiz] = useState(false);

    // Filters
    const [selectedYears, setSelectedYears] = useState<number[]>([]);
    const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

    // Expanded state for answers
    const [revealedAnswers, setRevealedAnswers] = useState<Record<number, boolean>>({});

    // Fetch Data
    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            // Build query string
            const params = new URLSearchParams();
            if (searchQuery) params.append('search', searchQuery);
            if (showFavoritesOnly) params.append('is_favorite', 'true');
            // Note: API currently supports single value, we might need to update API for multi-select
            // For now, let's just use client-side filtering for multi-select or simple single select in UI
            // To keep it simple for this iteration, we'll fetch all and filter client-side if needed, 
            // or just pass the first selected one. Let's pass the first one for now.
            if (selectedYears.length > 0) params.append('year', selectedYears[0].toString());
            if (selectedSubjects.length > 0) params.append('subject', selectedSubjects[0]);

            const res = await fetch(`http://localhost:5000/api/pyq/questions?${params.toString()}`);
            const data = await res.json();
            setQuestions(data);

            // Fetch Analytics only once
            if (!analytics) {
                const analyticsRes = await fetch('http://localhost:5000/api/pyq/analytics');
                const analyticsData = await analyticsRes.json();
                setAnalytics(analyticsData);
            }
        } catch (err) {
            console.error("Failed to fetch PYQ data", err);
        } finally {
            setLoading(false);
        }
    }, [searchQuery, showFavoritesOnly, selectedYears, selectedSubjects, analytics]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const toggleReveal = (id: number) => {
        setRevealedAnswers(prev => ({
            ...prev,
            [id]: !prev[id]
        }));
    };

    const toggleFavorite = async (id: number) => {
        try {
            const res = await fetch(`http://localhost:5000/api/pyq/${id}/favorite`, { method: 'POST' });
            if (res.ok) {
                setQuestions(prev => prev.map(q =>
                    q.id === id ? { ...q, is_favorite: !q.is_favorite } : q
                ));
            }
        } catch (err) {
            console.error("Failed to toggle favorite", err);
        }
    };

    const handleYearChange = (year: number) => {
        setSelectedYears(prev =>
            prev.includes(year) ? prev.filter(y => y !== year) : [year] // Single select behavior for now
        );
    };

    const handleSubjectChange = (subject: string) => {
        setSelectedSubjects(prev =>
            prev.includes(subject) ? prev.filter(s => s !== subject) : [subject] // Single select behavior for now
        );
    };

    const startQuiz = async () => {
        if (questions.length === 0) return;

        setStartingQuiz(true);
        try {
            const filters = {
                year: selectedYears[0],
                subject: selectedSubjects[0],
                search: searchQuery,
                is_favorite: showFavoritesOnly,
                limit: 25
            };

            const res = await fetch('http://localhost:5000/api/pyq/start-quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filters, title: 'PYQ Quiz' })
            });

            const data = await res.json();
            if (res.ok) {
                navigate(`/pyq-quiz/${data.session_id}`);
            } else {
                alert(data.error || 'Failed to start quiz');
            }
        } catch (err) {
            console.error("Error starting quiz", err);
            alert('Failed to start quiz');
        } finally {
            setStartingQuiz(false);
        }
    };

    return (
        <div className="pyq-container">
            {/* SIDEBAR FILTERS */}
            <div className="pyq-sidebar">
                <div className="filter-section">
                    <h3>Years</h3>
                    <div className="filter-group">
                        {analytics?.by_year.map(item => (
                            <label key={item.year} className="filter-checkbox">
                                <input
                                    type="checkbox"
                                    checked={selectedYears.includes(item.year)}
                                    onChange={() => handleYearChange(item.year)}
                                />
                                {item.year} <span style={{ opacity: 0.5 }}>({item.count})</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div className="filter-section">
                    <h3>Subjects</h3>
                    <div className="filter-group">
                        {analytics?.by_subject.map(item => (
                            <label key={item.subject} className="filter-checkbox">
                                <input
                                    type="checkbox"
                                    checked={selectedSubjects.includes(item.subject)}
                                    onChange={() => handleSubjectChange(item.subject)}
                                />
                                {item.subject} <span style={{ opacity: 0.5 }}>({item.count})</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div className="filter-section">
                    <h3>Options</h3>
                    <label className="filter-checkbox">
                        <input
                            type="checkbox"
                            checked={showFavoritesOnly}
                            onChange={() => setShowFavoritesOnly(!showFavoritesOnly)}
                        />
                        Show Favorites Only
                    </label>
                </div>
            </div>

            {/* MAIN CONTENT */}
            <div className="pyq-main">
                <div className="pyq-header">
                    <div className="pyq-title">The Archives</div>
                    <div className="search-bar">
                        <span className="search-icon">🔍</span>
                        <input
                            type="text"
                            placeholder="Search questions, topics..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <button
                        className="start-quiz-btn"
                        onClick={startQuiz}
                        disabled={startingQuiz || questions.length === 0}
                        title="Start an interactive quiz with current filters"
                    >
                        {startingQuiz ? 'Starting...' : '🎯 Start Quiz'}
                    </button>
                </div>

                <div className="question-list">
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '50px' }}>Accessing Archives...</div>
                    ) : questions.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '50px', opacity: 0.5 }}>No records found in the archives.</div>
                    ) : (
                        questions.map(q => (
                            <div key={q.id} className="question-card">
                                <div className="q-meta">
                                    <div className="q-tags">
                                        <span className="tag year">{q.year}</span>
                                        <span className="tag subject">{q.subject}</span>
                                        <span className="tag difficulty">{q.difficulty}</span>
                                    </div>
                                    <button
                                        className={`fav-btn ${q.is_favorite ? 'active' : ''}`}
                                        onClick={() => toggleFavorite(q.id)}
                                        title="Mark as Favorite"
                                    >
                                        {q.is_favorite ? '★' : '☆'}
                                    </button>
                                </div>

                                <div className="q-text">{q.question_text}</div>

                                <div className="q-options">
                                    {['A', 'B', 'C', 'D'].map(opt => {
                                        const optionText = q[`option_${opt.toLowerCase()}` as keyof Question];
                                        const isRevealed = revealedAnswers[q.id];
                                        const isCorrect = q.correct_option === opt;

                                        let className = 'option';
                                        if (isRevealed) {
                                            if (isCorrect) className += ' correct';
                                            else className += ' wrong'; // Could highlight selected wrong answer if we tracked user selection
                                        }

                                        return (
                                            <div key={opt} className={className}>
                                                <strong>{opt}.</strong> {optionText}
                                            </div>
                                        );
                                    })}
                                </div>

                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <button className="reveal-btn" onClick={() => toggleReveal(q.id)}>
                                        {revealedAnswers[q.id] ? 'Hide Answer' : 'Show Answer'}
                                    </button>
                                </div>

                                {revealedAnswers[q.id] && (
                                    <div className="explanation">
                                        <h4>Explanation</h4>
                                        {q.explanation}
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default PYQDatabase;
