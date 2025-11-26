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
}

interface CompilationData {
    year: number;
    month: number;
    generated_at: string;
    total_articles: number;
    subjects: { [key: string]: Article[] };
}

interface MonthOption {
    year: number;
    month: number;
    label: string;
}

const CompilationGenerator: React.FC = () => {
    const [months, setMonths] = useState<MonthOption[]>([]);
    const [selectedMonth, setSelectedMonth] = useState<string>('');
    const [compilation, setCompilation] = useState<CompilationData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchMonths();
    }, []);

    const fetchMonths = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/compilation/months');
            if (res.ok) {
                const data = await res.json();
                setMonths(data);
                if (data.length > 0) {
                    setSelectedMonth(`${data[0].year}-${data[0].month}`);
                }
            }
        } catch (err) {
            console.error("Failed to fetch months", err);
        }
    };

    const handleGenerate = async () => {
        if (!selectedMonth) return;

        const [year, month] = selectedMonth.split('-').map(Number);
        setLoading(true);
        setError(null);
        setCompilation(null);

        try {
            const res = await fetch(`http://localhost:5000/api/compilation/${year}/${month}`);
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

    const handlePrint = () => {
        window.print();
    };

    return (
        <div className="compilation-container">
            <div className="compilation-header">
                <h1>📚 Monthly Compilation Generator</h1>
                <p>Create print-ready monthly current affairs magazines.</p>
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
                    onClick={handleGenerate}
                    disabled={loading || !selectedMonth}
                >
                    {loading ? 'Generating...' : 'Generate Report'}
                </button>
            </div>

            {error && <div className="error-message">{error}</div>}

            {compilation && (
                <div className="compilation-report">
                    <div className="print-actions">
                        <button className="print-btn" onClick={handlePrint}>🖨️ Print / Save PDF</button>
                    </div>

                    <div className="report-cover">
                        <h1>UPSC Current Affairs</h1>
                        <h2>{new Date(compilation.year, compilation.month - 1).toLocaleString('default', { month: 'long', year: 'numeric' })}</h2>
                        <p>Total Articles: {compilation.total_articles}</p>
                        <p>Generated on: {new Date(compilation.generated_at).toLocaleDateString()}</p>
                    </div>

                    <div className="toc">
                        <h2>Table of Contents</h2>
                        <ul>
                            {Object.keys(compilation.subjects).sort().map(subject => (
                                <li key={subject}>
                                    <a href={`#${subject.replace(/\s+/g, '-')}`}>{subject}</a>
                                    <span>{compilation.subjects[subject].length} articles</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {Object.keys(compilation.subjects).sort().map(subject => (
                        <div key={subject} id={subject.replace(/\s+/g, '-')} className="subject-section">
                            <h3 className="subject-header">{subject}</h3>
                            {compilation.subjects[subject].map(article => (
                                <div key={article.id} className="article-item">
                                    <div className="article-title">{article.title}</div>
                                    <div className="article-meta">
                                        {article.papers.join(', ')} • {new Date(article.published_date).toLocaleDateString()} • {article.source}
                                    </div>
                                    <div className="article-content">
                                        <p>{article.upsc_summary}</p>
                                        {article.original_summary && article.original_summary !== article.upsc_summary && (
                                            <p className="original-summary"><em>{article.original_summary}</em></p>
                                        )}
                                        {article.key_points.length > 0 && (
                                            <div className="key-points">
                                                <strong>Key Points:</strong>
                                                <ul>
                                                    {article.key_points.map((point, i) => (
                                                        <li key={i}>{point}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CompilationGenerator;
