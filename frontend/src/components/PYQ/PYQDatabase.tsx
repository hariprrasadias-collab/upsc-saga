// /frontend/src/components/PYQ/PYQDatabase.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './PYQDatabase.css';
import { brainService } from '../../services/BrainService';
import MarkdownRenderer from '../Shared/MarkdownRenderer';
import { Virtuoso } from 'react-virtuoso';
import PYQHeatmap from '../Analytics/PYQHeatmap';
import DifficultyTrendChart from '../Analytics/DifficultyTrendChart';
import Modal from '../Shared/Modal';
import { generateCombatSheet } from '../../util/exportUtils';
import { API_BASE_URL } from '../../config';

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
    difficulty_trend?: any[];
}

const PYQDatabase: React.FC = () => {
    const navigate = useNavigate();
    const [questions, setQuestions] = useState<Question[]>([]);
    const [analytics, setAnalytics] = useState<Analytics | null>(null);
    const [loading, setLoading] = useState(true);
    const [startingQuiz, setStartingQuiz] = useState(false);
    const [strategosAnalysis, setStrategosAnalysis] = useState<string | null>(null);
    const [analyzingId, setAnalyzingId] = useState<number | null>(null);

    // Filters
    const [selectedYears, setSelectedYears] = useState<number[]>([]);
    const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
    const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
    const [availableTopics, setAvailableTopics] = useState<{ topic: string, subject: string }[]>([]);
    const [loadingTopics, setLoadingTopics] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [trendAnalysis, setTrendAnalysis] = useState<string | null>(null);
    const [showHeatmap, setShowHeatmap] = useState(false);
    const [showSimilar, setShowSimilar] = useState<number | null>(null);
    const [similarQuestions, setSimilarQuestions] = useState<Question[]>([]);
    const [loadingSimilar, setLoadingSimilar] = useState(false);

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
                    const res = await fetch(`${API_BASE_URL}/api/pyq/topics?${params.toString()}`);
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

            const res = await fetch(`${API_BASE_URL}/api/pyq/questions?${params.toString()}`);
            const data = await res.json();
            setQuestions(data);

            // Fetch Analytics (Dynamic based on filters)
            const analyticsParams = new URLSearchParams();
            selectedSubjects.forEach(s => analyticsParams.append('subjects', s));
            selectedYears.forEach(y => analyticsParams.append('years', y.toString()));

            const analyticsRes = await fetch(`${API_BASE_URL}/api/pyq/analytics?${analyticsParams.toString()}`);
            const analyticsData = await analyticsRes.json();
            setAnalytics(analyticsData);

        } catch (err) {
            console.error("Failed to fetch PYQ data", err);
        } finally {
            setLoading(false);
        }
    }, [searchQuery, showFavoritesOnly, selectedYears, selectedSubjects, selectedTopics]);

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
            const res = await fetch(`${API_BASE_URL}/api/pyq/${id}/favorite`, { method: 'POST' });
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

            const res = await fetch(`${API_BASE_URL}/api/pyq/start-quiz`, {
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

            const res = await fetch(`${API_BASE_URL}/api/arena/create-custom-boss`, {
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

    const handleAnalyzeTrends = async () => {
        setIsAnalyzing(true);
        try {
            const filters = {
                year: selectedYears[0],
                subject: selectedSubjects[0],
            };
            const result = await brainService.executeAction('ANALYZE_PYQ_TRENDS', { filters });
            if (result.success) {
                setTrendAnalysis(result.analysis);
            } else {
                alert("Analysis failed: " + result.message);
            }
        } catch (err) {
            console.error("Analysis error:", err);
            alert("The Brain is silent.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    const askStrategos = async (id: number) => {
        setAnalyzingId(id);
        try {
            const res = await fetch(`${API_BASE_URL}/api/pyq/strategos/${id}`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                setStrategosAnalysis(data.analysis);
            } else {
                alert("Strategos is offline.");
            }
        } catch (err) {
            console.error(err);
        } finally {
            setAnalyzingId(null);
        }
    };

    const findSimilar = async (id: number) => {
        if (showSimilar === id) {
            setShowSimilar(null);
            return;
        }
        setShowSimilar(id);
        setLoadingSimilar(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/pyq/similar/${id}`);
            const data = await res.json();
            setSimilarQuestions(data);
        } catch (err) {
            console.error("Failed to fetch similar questions", err);
        } finally {
            setLoadingSimilar(false);
        }
    };

    // Virtualized List Row Renderer
    const Row = (index: number) => {
        const q = questions[index];
        const isRevealed = revealedAnswers[q.id];

        return (
            <div style={{ padding: '0 10px 10px 0' }}>
                <div className="question-card">
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
                            const isCorrect = q.correct_option === opt;
                            let className = 'option';
                            if (isRevealed) {
                                if (isCorrect) className += ' correct';
                                else className += ' wrong';
                            }
                            return (
                                <div key={opt} className={className}>
                                    <strong>{opt}.</strong> {optionText}
                                </div>
                            );
                        })}
                    </div>

                    <div className="q-actions-footer">
                        <button className="reveal-btn" onClick={() => toggleReveal(q.id)}>
                            {isRevealed ? 'Hide Answer' : 'Show Answer'}
                        </button>
                        <button className="similar-btn" onClick={() => findSimilar(q.id)}>
                             🔍 Find Similar
                        </button>
                        <button
                            className="strategos-btn"
                            onClick={() => askStrategos(q.id)}
                            disabled={analyzingId === q.id}
                            style={{ background: '#8e44ad', marginLeft: '10px' }}
                        >
                             {analyzingId === q.id ? 'Thinking...' : '🧠 Ask Strategos'}
                        </button>
                    </div>

                    {isRevealed && (
                        <div className="explanation">
                            <h4>Explanation</h4>
                            {q.explanation}
                        </div>
                    )}

                    {showSimilar === q.id && (
                        <div className="similar-panel">
                            <h4>Similar Questions</h4>
                            {loadingSimilar ? <div>Scanning Archives...</div> :
                                similarQuestions.length === 0 ? <div>No similar questions found.</div> : (
                                <div className="similar-list">
                                    {similarQuestions.map(sq => (
                                        <div key={sq.id} className="similar-item" onClick={() => {
                                            // Maybe navigate or open modal? For now just show snippet
                                            alert(sq.question_text);
                                        }}>
                                            <span className="tag">{sq.year}</span> {sq.question_text.substring(0, 80)}...
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="pyq-container">
            {/* SIDEBAR FILTERS */}
            <div className="pyq-sidebar">
                <div className="filter-section">
                    {analytics?.difficulty_trend && <DifficultyTrendChart data={analytics.difficulty_trend} />}
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
                    <div className="pyq-title">The Grand Archives</div>
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
                            onClick={() => setShowHeatmap(!showHeatmap)}
                            title="Toggle Heatmap View"
                            style={{ marginRight: '10px', background: '#2980b9', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}
                        >
                           {showHeatmap ? '📋 List View' : '🔥 Heatmap'}
                        </button>
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
                            className="export-btn"
                            onClick={() => generateCombatSheet(questions)}
                            disabled={questions.length === 0}
                            title="Print Combat Sheet"
                            style={{ marginRight: '10px', background: '#7f8c8d', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}
                        >
                            📄 Export Combat Sheet
                        </button>
                        <button
                            className="start-quiz-btn"
                            onClick={handleAnalyzeTrends}
                            disabled={isAnalyzing}
                            title="Analyze trends for selected filters"
                            style={{ marginRight: '10px', background: '#8e44ad' }}
                        >
                            {isAnalyzing ? 'Analyzing...' : '🧠 Analyze Trends'}
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

                {/* Trend Analysis Modal */}
                <Modal
                    isOpen={!!trendAnalysis}
                    onClose={() => setTrendAnalysis(null)}
                    title="🧠 Strategos Trend Analysis"
                >
                    <MarkdownRenderer content={trendAnalysis || ''} />
                </Modal>

                {/* Strategos Analysis Modal */}
                <Modal
                    isOpen={!!strategosAnalysis}
                    onClose={() => setStrategosAnalysis(null)}
                    title="🧠 Tactical Breakdown"
                >
                    <MarkdownRenderer content={strategosAnalysis || ''} />
                </Modal>

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
                                <span onClick={() => handleYearChange(year)} style={{ cursor: 'pointer', fontWeight: 'bold' }} role="button" aria-label={`Remove year ${year}`} tabIndex={0} onKeyDown={(e) => { if(e.key==='Enter' || e.key===' ') handleYearChange(year); }}><span aria-hidden="true">×</span></span>
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
                                <span onClick={() => handleSubjectChange(subject)} style={{ cursor: 'pointer', fontWeight: 'bold' }} role="button" aria-label={`Remove subject ${subject}`} tabIndex={0} onKeyDown={(e) => { if(e.key==='Enter' || e.key===' ') handleSubjectChange(subject); }}><span aria-hidden="true">×</span></span>
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
                                <span onClick={() => handleTopicChange(topic)} style={{ cursor: 'pointer', fontWeight: 'bold' }} role="button" aria-label={`Remove topic ${topic}`} tabIndex={0} onKeyDown={(e) => { if(e.key==='Enter' || e.key===' ') handleTopicChange(topic); }}><span aria-hidden="true">×</span></span>
                            </span>
                        ))}
                    </div>
                )}

                <div className="question-list-container" style={{ flex: 1, minHeight: 0 }}>
                    {showHeatmap ? (
                        <div style={{ height: '100%', overflowY: 'auto' }}>
                            <PYQHeatmap />
                        </div>
                    ) : loading ? (
                        <div style={{ textAlign: 'center', padding: '50px' }}>Accessing Archives...</div>
                    ) : questions.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '50px', opacity: 0.5 }}>No records found in the archives.</div>
                    ) : (
                        <Virtuoso
                            style={{ height: '100%' }}
                            totalCount={questions.length}
                            itemContent={Row}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

export default PYQDatabase;
