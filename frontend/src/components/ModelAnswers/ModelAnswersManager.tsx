import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import './ModelAnswersManager.css';

interface ModelAnswer {
    id: number;
    title: string;
    question_text: string;
    answer_text: string;
    word_count: number;
    score: number | null;
    year: number | null;
    paper: string | null;
    tags: string[];
    question_type: string | null;
    source: string;
    created_at: string;
}

const ModelAnswersManager: React.FC = () => {
    const [answers, setAnswers] = useState<ModelAnswer[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedAnswer, setSelectedAnswer] = useState<ModelAnswer | null>(null);
    const [showEditor, setShowEditor] = useState(false);

    // Filters
    const [filterPaper, setFilterPaper] = useState('');
    const [filterType, setFilterType] = useState('');
    const [filterMinScore, setFilterMinScore] = useState('');
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchAnswers();
    }, [filterPaper, filterType, filterMinScore]);

    const fetchAnswers = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (filterPaper) params.append('paper', filterPaper);
            if (filterType) params.append('type', filterType);
            if (filterMinScore) params.append('min_score', filterMinScore);

            const response = await fetch(`${API_BASE_URL}/api/model-answers?${params}`);
            const data = await response.json();

            if (data.success) {
                setAnswers(data.answers);
            }
        } catch (error) {
            console.error('Error fetching answers:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            fetchAnswers();
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/model-answers/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: searchQuery })
            });
            const data = await response.json();

            if (data.success) {
                setAnswers(data.answers);
            }
        } catch (error) {
            console.error('Error searching:', error);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this model answer?')) return;

        try {
            const response = await fetch(`${API_BASE_URL}/api/model-answers/${id}`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (data.success) {
                fetchAnswers();
                if (selectedAnswer?.id === id) {
                    setSelectedAnswer(null);
                }
            }
        } catch (error) {
            console.error('Error deleting:', error);
        }
    };

    const handleEdit = (answer: ModelAnswer) => {
        setSelectedAnswer(answer);
        setShowEditor(true);
    };

    const handleCreate = () => {
        setSelectedAnswer(null);
        setShowEditor(true);
    };

    return (
        <div className="model-answers-container">
            <div className="model-answers-header">
                <h1>📝 Model Answer Database</h1>
                <p className="subtitle">High-scoring reference answers for UPSC preparation</p>
            </div>

            {/* Search and Filters */}
            <div className="controls-section">
                <div className="search-bar">
                    <input
                        type="text"
                        placeholder="🔍 Search model answers (AI-powered)..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        className="search-input"
                    />
                    <button onClick={handleSearch} className="search-btn">Search</button>
                </div>

                <div className="filters">
                    <select value={filterPaper} onChange={(e) => setFilterPaper(e.target.value)} className="filter-select">
                        <option value="">All Papers</option>
                        <option value="GS1">GS1</option>
                        <option value="GS2">GS2</option>
                        <option value="GS3">GS3</option>
                        <option value="GS4">GS4</option>
                    </select>

                    <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="filter-select">
                        <option value="">All Types</option>
                        <option value="examine">Examine</option>
                        <option value="analyze">Analyze</option>
                        <option value="discuss">Discuss</option>
                        <option value="critically_examine">Critically Examine</option>
                        <option value="comment">Comment</option>
                    </select>

                    <select value={filterMinScore} onChange={(e) => setFilterMinScore(e.target.value)} className="filter-select">
                        <option value="">Any Score</option>
                        <option value="15">15+ marks</option>
                        <option value="18">18+ marks</option>
                        <option value="20">20+ marks</option>
                    </select>

                    <button onClick={handleCreate} className="create-btn">+ New Answer</button>
                </div>
            </div>

            {/* Answers Grid */}
            {loading ? (
                <div className="loading-state">Loading model answers...</div>
            ) : answers.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">📝</div>
                    <h3>No model answers found</h3>
                    <p>Start building your database of high-scoring answers</p>
                    <button onClick={handleCreate} className="empty-create-btn">Create First Answer</button>
                </div>
            ) : (
                <div className="answers-grid">
                    {answers.map(answer => (
                        <div key={answer.id} className="answer-card" onClick={() => setSelectedAnswer(answer)}>
                            <div className="card-header">
                                <h3 className="card-title">{answer.title}</h3>
                                {answer.score && (
                                    <div className="score-badge">{answer.score}/25</div>
                                )}
                            </div>

                            <p className="question-preview">{answer.question_text.substring(0, 150)}...</p>

                            <div className="card-meta">
                                {answer.paper && <span className="meta-badge">{answer.paper}</span>}
                                {answer.year && <span className="meta-badge">{answer.year}</span>}
                                {answer.question_type && <span className="meta-badge type-badge">{answer.question_type}</span>}
                                <span className="word-count">{answer.word_count} words</span>
                            </div>

                            {answer.tags.length > 0 && (
                                <div className="tags">
                                    {answer.tags.slice(0, 3).map((tag, idx) => (
                                        <span key={idx} className="tag">{tag}</span>
                                    ))}
                                </div>
                            )}

                            <div className="card-actions">
                                <button onClick={(e) => { e.stopPropagation(); handleEdit(answer); }} className="edit-btn">Edit</button>
                                <button onClick={(e) => { e.stopPropagation(); handleDelete(answer.id); }} className="delete-btn">Delete</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* View/Edit Modal */}
            {selectedAnswer && !showEditor && (
                <div className="modal-overlay" onClick={() => setSelectedAnswer(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{selectedAnswer.title}</h2>
                            <button className="close-btn" aria-label="Close" onClick={() => setSelectedAnswer(null)}>
                                <span aria-hidden="true">×</span>
                            </button>
                        </div>

                        <div className="modal-body">
                            <div className="section">
                                <h3>Question</h3>
                                <p className="question-full">{selectedAnswer.question_text}</p>
                            </div>

                            <div className="section">
                                <h3>Model Answer {selectedAnswer.score && `(${selectedAnswer.score}/25)`}</h3>
                                <div className="answer-full">{selectedAnswer.answer_text}</div>
                            </div>

                            <div className="metadata-section">
                                <div className="metadata-grid">
                                    {selectedAnswer.paper && <div><strong>Paper:</strong> {selectedAnswer.paper}</div>}
                                    {selectedAnswer.year && <div><strong>Year:</strong> {selectedAnswer.year}</div>}
                                    {selectedAnswer.question_type && <div><strong>Type:</strong> {selectedAnswer.question_type}</div>}
                                    <div><strong>Words:</strong> {selectedAnswer.word_count}</div>
                                    <div><strong>Source:</strong> {selectedAnswer.source}</div>
                                </div>
                            </div>

                            {selectedAnswer.tags.length > 0 && (
                                <div className="section">
                                    <h3>Tags</h3>
                                    <div className="tags-full">
                                        {selectedAnswer.tags.map((tag, idx) => (
                                            <span key={idx} className="tag">{tag}</span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="modal-footer">
                            <button onClick={() => handleEdit(selectedAnswer)} className="edit-btn-large">Edit Answer</button>
                            <button onClick={() => navigator.clipboard.writeText(selectedAnswer.answer_text)} className="copy-btn-large">Copy Answer</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ModelAnswersManager;
