import React, { useState, useEffect } from 'react';
import './PYQHeatmap.css';

interface HeatmapData {
    heatmap_data: [string, number, number][];
    topics: string[];
    years: number[];
    stats: {
        total_questions: number;
        unique_topics: number;
        year_range: string;
        most_asked_topic: string;
        most_asked_count: number;
        most_active_year: number;
        questions_in_active_year: number;
    };
}

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

const PYQHeatmap: React.FC = () => {
    const [data, setData] = useState<HeatmapData | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedSubject, setSelectedSubject] = useState<string>('');
    const [yearRange, setYearRange] = useState<[number, number]>([2013, 2024]);
    const [searchTopic, setSearchTopic] = useState('');
    const [availableSubjects, setAvailableSubjects] = useState<string[]>([]);
    const [selectedCell, setSelectedCell] = useState<{ topic: string; year: number } | null>(null);
    const [cellQuestions, setCellQuestions] = useState<CellQuestion[]>([]);

    useEffect(() => {
        fetchSubjects();
    }, []);

    useEffect(() => {
        fetchHeatmapData();
    }, [selectedSubject, yearRange]);

    const fetchSubjects = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/heatmap/subjects');
            const result = await response.json();
            if (result.success) {
                setAvailableSubjects(result.subjects);
            }
        } catch (error) {
            console.error('Error fetching subjects:', error);
        }
    };

    const fetchHeatmapData = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (selectedSubject) params.append('subject', selectedSubject);
            params.append('year_start', yearRange[0].toString());
            params.append('year_end', yearRange[1].toString());
            if (searchTopic) params.append('topic', searchTopic);

            const response = await fetch(`http://localhost:5000/api/heatmap/pyq?${params}`);
            const result = await response.json();
            if (result.success) {
                setData(result);
            }
        } catch (error) {
            console.error('Error fetching heatmap:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCellClick = async (topic: string, year: number) => {
        setSelectedCell({ topic, year });
        try {
            const params = new URLSearchParams();
            params.append('topic', topic);
            params.append('year', year.toString());
            const response = await fetch(`http://localhost:5000/api/heatmap/cell?${params}`);
            const result = await response.json();
            if (result.success) {
                setCellQuestions(result.questions);
            }
        } catch (error) {
            console.error('Error fetching cell questions:', error);
        }
    };

    const getColorIntensity = (count: number, maxCount: number): string => {
        if (count === 0) return 'rgba(255, 255, 255, 0.03)';
        const intensity = Math.min(count / maxCount, 1);
        // Gold/Orange theme: 243, 156, 18
        return `rgba(243, 156, 18, ${0.15 + intensity * 0.85})`;
    };

    const filteredTopics = data?.topics.filter(topic =>
        topic.toLowerCase().includes(searchTopic.toLowerCase())
    ) || [];

    const maxCount = Math.max(...(data?.heatmap_data.map(([_, __, count]) => count) || [1]));

    return (
        <div className="pyq-heatmap-container">
            <div className="heatmap-header">
                <h1>📊 PYQ Topic Heatmap</h1>
                <p className="heatmap-subtitle">Visualize question patterns across years</p>
            </div>

            <div className="heatmap-filters">
                <div className="filter-group">
                    <label>Subject</label>
                    <select value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)} className="filter-select">
                        <option value="">All Subjects</option>
                        {availableSubjects.map(subject => <option key={subject} value={subject}>{subject}</option>)}
                    </select>
                </div>

                <div className="filter-group">
                    <label>Year Range: {yearRange[0]} - {yearRange[1]}</label>
                    <div className="year-range-sliders">
                        <input type="range" min="2013" max="2024" value={yearRange[0]}
                            onChange={(e) => setYearRange([parseInt(e.target.value), yearRange[1]])} className="year-slider" />
                        <input type="range" min="2013" max="2024" value={yearRange[1]}
                            onChange={(e) => setYearRange([yearRange[0], parseInt(e.target.value)])} className="year-slider" />
                    </div>
                </div>

                <div className="filter-group">
                    <label>Search Topic</label>
                    <input type="text" placeholder="Filter topics..." value={searchTopic}
                        onChange={(e) => setSearchTopic(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && fetchHeatmapData()} className="topic-search" />
                </div>
            </div>

            {data && (
                <div className="stats-cards">
                    <div className="stat-card"><div className="stat-value">{data.stats.total_questions}</div><div className="stat-label">Total Questions</div></div>
                    <div className="stat-card"><div className="stat-value">{data.stats.unique_topics}</div><div className="stat-label">Unique Topics</div></div>
                    <div className="stat-card highlight"><div className="stat-value">{data.stats.most_asked_topic}</div><div className="stat-label">Most Asked ({data.stats.most_asked_count}x)</div></div>
                    <div className="stat-card"><div className="stat-value">{data.stats.most_active_year}</div><div className="stat-label">Most Active Year</div></div>
                </div>
            )}

            {loading ? (
                <div className="loading-state">Analyzing PYQ data...</div>
            ) : data && data.heatmap_data.length > 0 ? (
                <div className="heatmap-wrapper">
                    <div className="heatmap-grid">
                        <div className="heatmap-row header-row">
                            <div className="heatmap-cell corner-cell">Topic</div>
                            {data.years.map(year => <div key={year} className="heatmap-cell year-cell">{year}</div>)}
                        </div>
                        {filteredTopics.map(topic => (
                            <div key={topic} className="heatmap-row">
                                <div className="heatmap-cell topic-cell" title={topic}>{topic}</div>
                                {data.years.map(year => {
                                    const cellData = data.heatmap_data.find(([t, y, _]) => t === topic && y === year);
                                    const count = cellData ? cellData[2] : 0;
                                    return (
                                        <div key={`${topic}-${year}`} className="heatmap-cell data-cell"
                                            style={{ backgroundColor: getColorIntensity(count, maxCount) }}
                                            onClick={() => count > 0 && handleCellClick(topic, year)}
                                            title={`${topic} (${year}): ${count} questions`}>
                                            {count > 0 ? count : ''}
                                        </div>
                                    );
                                })}
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="empty-state">No data available for selected filters</div>
            )}

            {selectedCell && (
                <div className="cell-modal-overlay" onClick={() => setSelectedCell(null)}>
                    <div className="cell-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{selectedCell.topic} ({selectedCell.year})</h2>
                            <button className="close-btn" onClick={() => setSelectedCell(null)}>×</button>
                        </div>
                        <div className="modal-content">
                            {cellQuestions.map((q, idx) => (
                                <div key={q.id} className="question-item">
                                    <div className="question-number">Q{idx + 1}</div>
                                    <div className="question-details">
                                        <p className="question-text">{q.question_text}</p>

                                        {/* Options */}
                                        <div className="question-options">
                                            {['A', 'B', 'C', 'D'].map(opt => {
                                                const optionKey = `option_${opt.toLowerCase()}` as keyof CellQuestion;
                                                const optionText = q[optionKey];
                                                const isCorrect = q.correct_option?.toUpperCase() === opt;

                                                // Debug logging
                                                if (idx === 0 && opt === 'A') {
                                                    console.log('Question Data:', q);
                                                }

                                                return (
                                                    <div key={opt} className={`option ${isCorrect ? 'correct-option' : ''}`}>
                                                        <span className="opt-label">{opt}.</span>
                                                        <span className="opt-text">{optionText || 'Option text missing'}</span>
                                                        {isCorrect && <span className="correct-badge"> ✓ Correct</span>}
                                                    </div>
                                                );
                                            })}
                                        </div>

                                        {/* Explanation */}
                                        {q.explanation && (
                                            <div className="question-explanation">
                                                <strong>Explanation:</strong> {q.explanation}
                                            </div>
                                        )}

                                        <div className="question-meta">
                                            <span className="difficulty-badge">{q.difficulty}</span>
                                            <span className="subject-badge">{q.subject}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PYQHeatmap;
