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
    const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
    const [availableTopics, setAvailableTopics] = useState<{ topic: string, subject: string }[]>([]);
    const [loadingTopics, setLoadingTopics] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

    // Expanded state for answers
    const [revealedAnswers, setRevealedAnswers] = useState<Record<number, boolean>>({});

    // Fetch topics dynamically when subjects change
    useEffect(() => {
        const fetchTopics = async () => {
            if (selectedSubjects.length > 0) {
                setLoadingTopics(true);
                try {
                    const params = new URLSearchParams();
                    selectedSubjects.forEach(subject => params.append('subjects', subject));
                    const res = await fetch(`http://localhost:5000/api/pyq/topics?${params.toString()}`);
                    const data = await res.json();
                    setAvailableTopics(data);
                } catch (err) {
                    console.error("Failed to fetch topics", err);
                    setAvailableTopics([]);
                } finally {
                    setLoadingTopics(false);
                }
            } else {
                setAvailableTopics([]);
                setSelectedTopics([]);  // Clear selected topics when no subject is selected
            }
        };

        fetchTopics();
    }, [selectedSubjects]);

    // Fetch Data
    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            // Build query string with multi-select support
            const params = new URLSearchParams();

            // Multi-select years
            selectedYears.forEach(year => params.append('years', year.toString()));

            // Multi-select subjects
            selectedSubjects.forEach(subject => params.append('subjects', subject));

            // Multi-select topics
            selectedTopics.forEach(topic => params.append('topics', topic));

            if (searchQuery) params.append('search', searchQuery);
            if (showFavoritesOnly) params.append('is_favorite', 'true');

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
    }, [searchQuery, showFavoritesOnly, selectedYears, selectedSubjects, selectedTopics, analytics]);

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
            prev.includes(year) ? prev.filter(y => y !== year) : [...prev, year]  // Multi-select
        );
    };

    const handleSubjectChange = (subject: string) => {
        setSelectedSubjects(prev =>
            prev.includes(subject) ? prev.filter(s => s !== subject) : [...prev, subject]  // Multi-select
        );
    };

    const handleTopicChange = (topic: string) => {
        setSelectedTopics(prev =>
            prev.includes(topic) ? prev.filter(t => t !== topic) : [...prev, topic]  // Multi-select
        );
    };

    const clearAllFilters = () => {
        setSelectedYears([]);
        setSelectedSubjects([]);
        setSelectedTopics([]);
        setSearchQuery('');
        setShowFavoritesOnly(false);
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

    const createBossBattle = async () => {
        const name = prompt("Enter a name for this Boss Battle (e.g., 'Polity 2023 Challenge'):");
        if (!name) return;

        try {
            const filters = {
                year: selectedYears[0],
                subject: selectedSubjects[0],
                search: searchQuery
            };

            const res = await fetch('http://localhost:5000/api/arena/create-custom-boss', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, filters })
            });

            if (res.ok) {
                alert("⚔️ Boss Battle Created! Go to the Battle Arena to fight.");
            } else {
                alert("Failed to create battle.");
            }
        } catch (err) {
            console.error("Error creating battle:", err);
            alert("Error creating battle.");
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
                    <h3>Topics {loadingTopics && '⏳'}</h3>
                    {selectedSubjects.length === 0 ? (
                        <p style={{ opacity: 0.5, fontSize: '12px', padding: '5px 0' }}>
                            Select a subject first
                        </p>
                    ) : availableTopics.length === 0 && !loadingTopics ? (
                        <p style={{ opacity: 0.5, fontSize: '12px', padding: '5px 0' }}>
                            No topics available
                        </p>
                    ) : (
                        <div className="filter-group" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                            {availableTopics.map(item => (
                                <label key={item.topic} className="filter-checkbox">
                                    <input
                                        type="checkbox"
                                        checked={selectedTopics.includes(item.topic)}
                                        onChange={() => handleTopicChange(item.topic)}
                                    />
                                    <span style={{ fontSize: '13px' }}>{item.topic}</span>
                                </label>
                            ))}
                        </div>
                    )}
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
                    <button
                        onClick={clearAllFilters}
                        style={{
                            marginTop: '15px',
                            width: '100%',
                            padding: '8px',
                            background: '#e74c3c',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '13px'
                        }}
                    >
                        🔄 Clear All Filters
                    </button>
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
                    <div className="header-actions">
                        <button
                            className="create-boss-btn"
                            onClick={createBossBattle}
                            disabled={questions.length === 0}
                            title="Create a Boss Battle from current filters"
                            style={{ marginRight: '10px', background: '#e74c3c', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}
                        >
                            ⚔️ Create Boss Battle
                        </button>
                        <button
                            className="start-quiz-btn"
                            onClick={startQuiz}
                            disabled={startingQuiz || questions.length === 0}
                            title="Start an interactive quiz with current filters"
                        >
                            {startingQuiz ? 'Starting...' : '🎯 Start Quiz'}
                        </button>
                    </div>
                </div>

                {/* Active Filters Display */}
                {(selectedYears.length > 0 || selectedSubjects.length > 0 || selectedTopics.length > 0) && (
                    <div style={{
                        padding: '10px 20px',
                        borderBottom: '1px solid #444',
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '8px',
                        alignItems: 'center'
                    }}>
                        <span style={{ opacity: 0.7, fontSize: '12px', marginRight: '5px' }}>Active Filters:</span>
                        {selectedYears.map(year => (
                            <span key={year} style={{
                                background: '#3498db',
                                color: 'white',
                                padding: '4px 10px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px'
                            }}>
                                📅 {year}
                                <span onClick={() => handleYearChange(year)} style={{ cursor: 'pointer', fontWeight: 'bold' }}>×</span>
                            </span>
                        ))}
                        {selectedSubjects.map(subject => (
                            <span key={subject} style={{
                                background: '#2ecc71',
                                color: 'white',
                                padding: '4px 10px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px'
                            }}>
                                📚 {subject}
                                <span onClick={() => handleSubjectChange(subject)} style={{ cursor: 'pointer', fontWeight: 'bold' }}>×</span>
                            </span>
                        ))}
                        {selectedTopics.map(topic => (
                            <span key={topic} style={{
                                background: '#9b59b6',
                                color: 'white',
                                padding: '4px 10px',
                                borderRadius: '12px',
                                fontSize: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px'
                            }}>
                                🏷️ {topic}
                                <span onClick={() => handleTopicChange(topic)} style={{ cursor: 'pointer', fontWeight: 'bold' }}>×</span>
                            </span>
                        ))}
                    </div>
                )}

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
