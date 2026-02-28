import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import './Compilation.css';

interface Article {
    id: number;
    title: string;
    upsc_summary: string;
    original_summary: string;
    key_points: string[];
    papers: string[];
    subjects: string[];
    published_date: string;
    source: string;
    importance: number;
    link: string;
    image_url: string;
    related_pyqs: Array<{ year: string; question: string }>;
}

interface CompilationData {
    year: number;
    month: number;
    generated_at: string;
    total_articles: number;
    subjects: { [key: string]: Article[] };
    stats: {
        high_importance: number;
        medium_importance: number;
        low_importance: number;
    };
}

interface MonthOption {
    year: number;
    month: number;
    label: string;
    is_current?: boolean;
}

const CompilationGenerator: React.FC = () => {
    const [months, setMonths] = useState<MonthOption[]>([]);
    const [selectedMonth, setSelectedMonth] = useState<string>('');
    const [compilation, setCompilation] = useState<CompilationData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [expandedArticles, setExpandedArticles] = useState<Set<number>>(new Set());
    const [expandedSubjects, setExpandedSubjects] = useState<Set<string>>(new Set());

    useEffect(() => {
        fetchMonthsAndAutoLoad();
    }, []);

    const fetchMonthsAndAutoLoad = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/compilation/months`);
            if (res.ok) {
                const data = await res.json();
                setMonths(data);

                // Auto-select current month
                const currentMonth = data.find((m: MonthOption) => m.is_current);
                if (currentMonth) {
                    const monthKey = `${currentMonth.year}-${currentMonth.month}`;
                    setSelectedMonth(monthKey);
                    // Auto-generate current month
                    handleGenerate(currentMonth.year, currentMonth.month);
                } else if (data.length > 0) {
                    setSelectedMonth(`${data[0].year}-${data[0].month}`);
                }
            }
        } catch (err) {
            console.error("Failed to fetch months", err);
        }
    };

    const handleGenerate = async (year?: number, month?: number) => {
        let targetYear = year;
        let targetMonth = month;

        if (!targetYear || !targetMonth) {
            if (!selectedMonth) return;
            [targetYear, targetMonth] = selectedMonth.split('-').map(Number);
        }

        setLoading(true);
        setError(null);
        setCompilation(null);
        setExpandedArticles(new Set());
        setExpandedSubjects(new Set());

        try {
            const res = await fetch(`${API_BASE_URL}/api/compilation/${targetYear}/${targetMonth}`);
            if (!res.ok) {
                throw new Error('Failed to generate compilation');
            }
            const data = await res.json();
            setCompilation(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const toggleArticle = (id: number) => {
        const newExpanded = new Set(expandedArticles);
        if (newExpanded.has(id)) {
            newExpanded.delete(id);
        } else {
            newExpanded.add(id);
        }
        setExpandedArticles(newExpanded);
    };

    const toggleSubject = (subject: string) => {
        const newExpanded = new Set(expandedSubjects);
        if (newExpanded.has(subject)) {
            newExpanded.delete(subject);
        } else {
            newExpanded.add(subject);
        }
        setExpandedSubjects(newExpanded);
    };

    const getImportanceColor = (importance: number) => {
        switch (importance) {
            case 3: return '#ff6b6b'; // High - Red
            case 2: return '#fbbf24'; // Medium - Yellow
            default: return '#10b981'; // Low - Green
        }
    };

    const getImportanceLabel = (importance: number) => {
        switch (importance) {
            case 3: return 'High';
            case 2: return 'Medium';
            default: return 'Low';
        }
    };

    const handlePrint = () => {
        window.print();
    };

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <div className="compilation-container">
            <div className="compilation-header">
                <h1>📚 Monthly Compilation</h1>
                <p>Comprehensive UPSC Current Affairs Report</p>
            </div>

            <div className="compilation-controls">
                <select
                    className="month-select"
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}
                >
                    <option value="" disabled>Select Month</option>
                    {months.map((m, idx) => (
                        <option key={idx} value={`${m.year}-${m.month}`}>
                            {m.label}
                        </option>
                    ))}
                </select>

                <button
                    className="generate-btn"
                    onClick={() => handleGenerate()}
                    disabled={loading || !selectedMonth}
                >
                    {loading ? '⏳ Generating...' : '🔄 Generate Report'}
                </button>
            </div>

            {error && <div className="error-message">❌ {error}</div>}

            {compilation && (
                <div className="compilation-report">
                    <div className="print-actions no-print">
                        <button className="print-btn" onClick={handlePrint}>🖨️ Print / Save PDF</button>
                        <button className="scroll-top-btn" onClick={scrollToTop}>⬆️ Back to Top</button>
                    </div>

                    <div className="report-cover">
                        <div className="cover-title">
                            <h1>UPSC Current Affairs</h1>
                            <h2>{new Date(compilation.year, compilation.month - 1).toLocaleString('default', { month: 'long', year: 'numeric' })}</h2>
                        </div>
                        <div className="compile stats-grid">
                            <div className="stat-card">
                                <span className="stat-number">{compilation.total_articles}</span>
                                <span className="stat-label">Total Articles</span>
                            </div>
                            <div className="stat-card high">
                                <span className="stat-number">{compilation.stats.high_importance}</span>
                                <span className="stat-label">High Priority</span>
                            </div>
                            <div className="stat-card medium">
                                <span className="stat-number">{compilation.stats.medium_importance}</span>
                                <span className="stat-label">Medium Priority</span>
                            </div>
                            <div className="stat-card low">
                                <span className="stat-number">{compilation.stats.low_importance}</span>
                                <span className="stat-label">Low Priority</span>
                            </div>
                        </div>
                        <p className="generated-date">Generated on: {new Date(compilation.generated_at).toLocaleDateString()}</p>
                    </div>

                    <div className="toc">
                        <h2>📋 Table of Contents</h2>
                        <ul>
                            {Object.keys(compilation.subjects).sort().map(subject => (
                                <li key={subject}>
                                    <a href={`#${subject.replace(/\s+/g, '-')}`}>{subject}</a>
                                    <span className="toc-count">{compilation.subjects[subject].length} articles</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {Object.keys(compilation.subjects).sort().map(subject => (
                        <div key={subject} id={subject.replace(/\s+/g, '-')} className="subject-section">
                            <div className="subject-header-bar" onClick={() => toggleSubject(subject)}>
                                <h3 className="subject-header">
                                    <span className="subject-icon">{expandedSubjects.has(subject) ? '▼' : '▶'}</span>
                                    {subject}
                                    <span className="subject-badge">{compilation.subjects[subject].length}</span>
                                </h3>
                            </div>

                            {expandedSubjects.has(subject) && (
                                <div className="articles-list">
                                    {compilation.subjects[subject].map(article => (
                                        <div key={article.id} className="article-item">
                                            <div className="article-header-row" onClick={() => toggleArticle(article.id)}>
                                                <div className="article-title-section">
                                                    <span className="expand-icon">{expandedArticles.has(article.id) ? '▼' : '▶'}</span>
                                                    <div className="article-title">{article.title}</div>
                                                </div>
                                                <div className="article-badges">
                                                    <span
                                                        className="importance-badge"
                                                        style={{ backgroundColor: getImportanceColor(article.importance) }}
                                                    >
                                                        {getImportanceLabel(article.importance)}
                                                    </span>
                                                    {article.papers.map(p => (
                                                        <span key={p} className="paper-badge">{p}</span>
                                                    ))}
                                                </div>
                                            </div>

                                            <div className="article-meta">
                                                📅 {new Date(article.published_date).toLocaleDateString()} •
                                                📰 {article.source}
                                                {article.link && (
                                                    <> • <a href={article.link} target="_blank" rel="noreferrer" className="source-link">🔗 Source</a></>
                                                )}
                                            </div>

                                            {expandedArticles.has(article.id) && (
                                                <div className="article-content">
                                                    <div className="summary-section">
                                                        <h4>📝 Summary</h4>
                                                        <p className="upsc-summary">{article.upsc_summary}</p>
                                                    </div>

                                                    {article.key_points.length > 0 && (
                                                        <div className="key-points-section">
                                                            <h4>🔑 Key Points</h4>
                                                            <ul className="key-points">
                                                                {article.key_points.map((point, i) => (
                                                                    <li key={i}>{point}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    )}

                                                    {article.related_pyqs && article.related_pyqs.length > 0 && (
                                                        <div className="pyqs-section">
                                                            <h4>📚 Related PYQs</h4>
                                                            {article.related_pyqs.map((pyq, i) => (
                                                                <div key={i} className="pyq-item">
                                                                    <span className="pyq-year">{pyq.year}</span>
                                                                    <span className="pyq-question">{pyq.question}</span>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CompilationGenerator;
