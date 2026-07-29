import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { API_BASE_URL } from '../../config';
import './PYQHeatmap.css';
import './PYQHeatmap_additions.css';

interface CellQuestion {
    id: number;
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    correct_option: string;
    explanation: string;
    year: number;
    subject: string;
    topic: string;
    difficulty: string;
}

interface HeatmapStats {
    total_questions: number;
    unique_topics: number;
    year_range: string;
    most_asked_topic: string;
    most_asked_count: number;
    most_active_year: number;
    questions_in_active_year: number;
}

const COLOR_SCALE = [
    'rgba(255, 255, 255, 0.02)',  // 0
    'rgba(59, 130, 246, 0.25)',   // 1
    'rgba(59, 130, 246, 0.4)',    // 2
    'rgba(168, 85, 247, 0.45)',   // 3
    'rgba(212, 165, 116, 0.5)',   // 4-5
    'rgba(212, 165, 116, 0.65)',  // 6-7
    'rgba(239, 68, 68, 0.6)',     // 8-9
    'rgba(239, 68, 68, 0.8)',     // 10+
];

function getCellColor(count: number): string {
    if (count === 0) return COLOR_SCALE[0];
    if (count === 1) return COLOR_SCALE[1];
    if (count === 2) return COLOR_SCALE[2];
    if (count === 3) return COLOR_SCALE[3];
    if (count <= 5) return COLOR_SCALE[4];
    if (count <= 7) return COLOR_SCALE[5];
    if (count <= 9) return COLOR_SCALE[6];
    return COLOR_SCALE[7];
}

const PYQHeatmap: React.FC = () => {
    const [heatmapData, setHeatmapData] = useState<[string, number, number][]>([]);
    const [topics, setTopics] = useState<string[]>([]);
    const [years, setYears] = useState<number[]>([]);
    const [stats, setStats] = useState<HeatmapStats | null>(null);
    const [subjects, setSubjects] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    // Filters
    const [selectedSubject, setSelectedSubject] = useState('');
    const [topicSearch, setTopicSearch] = useState('');
    const [yearStart, setYearStart] = useState<number>(0);
    const [yearEnd, setYearEnd] = useState<number>(9999);

    // Modal
    const [modalData, setModalData] = useState<{ topic: string; year: number; questions: CellQuestion[] } | null>(null);
    const [modalLoading, setModalLoading] = useState(false);

    // Fetch subjects for filter
    useEffect(() => {
        fetch(`${API_BASE_URL}/api/heatmap/subjects`)
            .then(r => r.json())
            .then(d => { if (d.success) setSubjects(d.subjects || []); })
            .catch(() => { });
    }, []);

    // Fetch heatmap data
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const params = new URLSearchParams();
                if (selectedSubject) params.set('subject', selectedSubject);
                if (yearStart > 0) params.set('year_start', String(yearStart));
                if (yearEnd < 9999) params.set('year_end', String(yearEnd));
                if (topicSearch) params.set('topic', topicSearch);

                const url = `${API_BASE_URL}/api/heatmap/pyq?${params.toString()}`;
                const res = await fetch(url);
                const data = await res.json();

                if (data.success) {
                    setHeatmapData(data.heatmap_data || []);
                    setTopics(data.topics || []);
                    setYears(data.years || []);
                    setStats(data.stats || null);

                    if (data.years?.length) {
                        if (yearStart === 0) setYearStart(Math.min(...data.years));
                        if (yearEnd === 9999) setYearEnd(Math.max(...data.years));
                    }
                }
            } catch (err) {
                console.error('Failed to load heatmap', err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [selectedSubject, topicSearch]);

    // Build lookup: topic→year→count
    const cellMap = useMemo(() => {
        const map: Record<string, Record<number, number>> = {};
        for (const [topic, year, count] of heatmapData) {
            if (!map[topic]) map[topic] = {};
            map[topic][year] = count;
        }
        return map;
    }, [heatmapData]);

    // Filter topics by search and year range
    const filteredTopics = useMemo(() => {
        return topics.filter(t => {
            if (topicSearch && !t.toLowerCase().includes(topicSearch.toLowerCase())) return false;
            // Check if topic has any data in current year range
            const topicData = cellMap[t];
            if (!topicData) return false;
            return Object.keys(topicData).some(y => {
                const yr = Number(y);
                return yr >= yearStart && yr <= yearEnd;
            });
        });
    }, [topics, topicSearch, cellMap, yearStart, yearEnd]);

    const filteredYears = useMemo(() => {
        return years.filter(y => y >= yearStart && y <= yearEnd);
    }, [years, yearStart, yearEnd]);

    // Cell click → fetch questions
    const handleCellClick = useCallback(async (topic: string, year: number) => {
        const count = cellMap[topic]?.[year] || 0;
        if (count === 0) return;

        setModalLoading(true);
        setModalData({ topic, year, questions: [] });

        try {
            const res = await fetch(`${API_BASE_URL}/api/heatmap/cell?topic=${encodeURIComponent(topic)}&year=${year}`);
            const data = await res.json();
            if (data.success) {
                setModalData({ topic, year, questions: data.questions || [] });
            }
        } catch (err) {
            console.error('Failed to load cell questions', err);
        } finally {
            setModalLoading(false);
        }
    }, [cellMap]);

    if (loading) {
        return (
            <div className="pyq-heatmap-container">
                <div className="loading-state">
                    <span style={{ fontSize: '2rem' }}>🔥</span>
                    <p>Loading Tactical Intelligence...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="pyq-heatmap-container">
            {/* Header */}
            <div className="heatmap-header">
                <h1>⚔️ PYQ Tactical Heatmap</h1>
                <p className="heatmap-subtitle">Topic × Year Question Distribution</p>
            </div>

            {/* Stat Cards */}
            {stats && (
                <div className="stats-cards">
                    <div className="stat-card highlight">
                        <div className="stat-value">{stats.total_questions}</div>
                        <div className="stat-label">Total Questions</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{stats.unique_topics}</div>
                        <div className="stat-label">Unique Topics</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{stats.year_range}</div>
                        <div className="stat-label">Year Range</div>
                    </div>
                    <div className="stat-card highlight">
                        <div className="stat-value">{stats.most_asked_count}</div>
                        <div className="stat-label">{stats.most_asked_topic ? `Most Asked: ${stats.most_asked_topic}` : 'Most Asked Topic'}</div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="heatmap-filters">
                <div className="filter-group">
                    <label>Subject</label>
                    <select
                        className="filter-select"
                        value={selectedSubject}
                        onChange={e => setSelectedSubject(e.target.value)}
                    >
                        <option value="">All Subjects</option>
                        {subjects.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
                <div className="filter-group">
                    <label>Search Topic</label>
                    <input
                        type="text"
                        className="topic-search"
                        placeholder="Type to filter topics..."
                        value={topicSearch}
                        onChange={e => setTopicSearch(e.target.value)}
                    />
                </div>
                <div className="filter-group">
                    <label>Year Range: {yearStart} – {yearEnd}</label>
                    <div className="year-range-sliders">
                        <input type="range" className="year-slider" min={years[0] || 1990} max={years[years.length - 1] || 2024} value={yearStart} onChange={e => setYearStart(Number(e.target.value))} />
                        <input type="range" className="year-slider" min={years[0] || 1990} max={years[years.length - 1] || 2024} value={yearEnd} onChange={e => setYearEnd(Number(e.target.value))} />
                    </div>
                </div>
            </div>

            {/* Color Legend */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap' }}>
                <span style={{ color: '#8899a6', fontSize: '13px', marginRight: '8px' }}>Intensity:</span>
                {['0', '1', '2', '3', '4-5', '6-7', '8-9', '10+'].map((label, i) => (
                    <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <div style={{ width: '20px', height: '20px', borderRadius: '3px', background: COLOR_SCALE[i], border: '1px solid rgba(255,255,255,0.1)' }} />
                        <span style={{ color: '#8899a6', fontSize: '11px' }}>{label}</span>
                    </div>
                ))}
            </div>

            {/* Heatmap Grid */}
            {filteredTopics.length === 0 ? (
                <div className="empty-state">
                    <span style={{ fontSize: '3rem' }}>📭</span>
                    <p>No topics match your filters. Try adjusting the subject or year range.</p>
                </div>
            ) : (
                <div className="heatmap-wrapper">
                    <div className="heatmap-grid">
                        {/* Header Row */}
                        <div className="heatmap-row header-row">
                            <div className="heatmap-cell corner-cell">TOPIC / YEAR</div>
                            {filteredYears.map(year => (
                                <div key={year} className="heatmap-cell year-cell">{year}</div>
                            ))}
                        </div>

                        {/* Data Rows */}
                        {filteredTopics.map(topic => (
                            <div key={topic} className="heatmap-row">
                                <div className="heatmap-cell topic-cell" title={topic}>{topic}</div>
                                {filteredYears.map(year => {
                                    const count = cellMap[topic]?.[year] || 0;
                                    return (
                                        <div
                                            key={`${topic}-${year}`}
                                            className={`heatmap-cell data-cell${count > 0 ? ' has-data' : ''}`}
                                            style={{ backgroundColor: getCellColor(count) }}
                                            onClick={() => handleCellClick(topic, year)}
                                            title={`${topic} (${year}): ${count} questions`}
                                        >
                                            {count > 0 ? count : ''}
                                        </div>
                                    );
                                })}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Drilldown Modal */}
            {modalData && (
                <div className="cell-modal-overlay" onClick={() => setModalData(null)}>
                    <div className="cell-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>📜 {modalData.topic} — {modalData.year}</h2>
                            <button className="close-btn" onClick={() => setModalData(null)} aria-label="Close"><span aria-hidden="true">✕</span></button>
                        </div>
                        <div className="modal-content">
                            {modalLoading ? (
                                <div className="loading-state">Loading questions...</div>
                            ) : modalData.questions.length === 0 ? (
                                <div className="empty-state">No questions found for this cell.</div>
                            ) : (
                                modalData.questions.map((q, idx) => (
                                    <div key={q.id} className="question-item">
                                        <div className="question-number">{idx + 1}</div>
                                        <div className="question-details">
                                            <div className="question-text">{q.question_text}</div>
                                            <div className="question-options">
                                                {['a', 'b', 'c', 'd'].map(opt => {
                                                    const optText = q[`option_${opt}` as keyof CellQuestion] as string;
                                                    if (!optText) return null;
                                                    const isCorrect = q.correct_option?.toLowerCase() === opt;
                                                    return (
                                                        <div key={opt} className={`option${isCorrect ? ' correct-option' : ''}`}>
                                                            <span className="opt-label">{opt.toUpperCase()}.</span>
                                                            <span className="opt-text">{optText}</span>
                                                            {isCorrect && <span className="correct-badge">✓ CORRECT</span>}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                            {q.explanation && (
                                                <div className="question-explanation">
                                                    <strong>💡 Explanation</strong>
                                                    {q.explanation}
                                                </div>
                                            )}
                                            <div className="question-meta">
                                                {q.difficulty && <span className="difficulty-badge">{q.difficulty}</span>}
                                                {q.subject && <span className="subject-badge">{q.subject}</span>}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PYQHeatmap;
