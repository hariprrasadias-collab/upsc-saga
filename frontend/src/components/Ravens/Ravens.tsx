// frontend/src/components/Ravens/Ravens.tsx
import React, { useState, useEffect } from 'react';
import './Ravens.css';
import { audioManager } from '../../util/AudioManager';

interface Article {
    id?: number;
    title: string;
    link: string;
    source: string;
    published: string;
    upscSummary?: string;
    keyPoints?: string[];
    papers?: string[];
    subjects?: string[];
    importance?: number;
    ankiCardId?: number;
}

const Ravens: React.FC = () => {
    const [articles, setArticles] = useState<Article[]>([]);
    const [loading, setLoading] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [selectedPaper, setSelectedPaper] = useState<string>('');
    const [selectedSubject, setSelectedSubject] = useState<string>('');

    const papers = ['All Papers', 'GS1', 'GS2', 'GS3', 'GS4'];
    const subjects = ['All Subjects', 'Polity', 'Economics', 'International Relations',
        'Environment', 'Science & Tech', 'Internal Security', 'Social Issues'];

    useEffect(() => {
        fetchArticles();
    }, [selectedPaper, selectedSubject]);

    const fetchArticles = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (selectedPaper && selectedPaper !== 'All Papers') params.append('paper', selectedPaper);
            if (selectedSubject && selectedSubject !== 'All Subjects') params.append('subject', selectedSubject);

            const res = await fetch(`http://localhost:5000/api/ravens/saved?${params}`);
            if (res.ok) {
                const data = await res.json();
                setArticles(data);
            }
        } catch (err) {
            console.error("Error fetching articles:", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchAndProcessLatest = async () => {
        setProcessing(true);
        audioManager.play('click');

        try {
            const muninRes = await fetch('http://localhost:5000/api/ravens?type=munin');
            const huginRes = await fetch('http://localhost:5000/api/ravens?type=hugin');

            const muninNews = await muninRes.json();
            const huginNews = await huginRes.json();
            const allNews = [...muninNews, ...huginNews];

            console.log(`Processing ${allNews.length} articles with Gemini AI...`);

            for (let i = 0; i < allNews.length; i++) {
                const article = allNews[i];
                console.log(`Processing ${i + 1}/${allNews.length}: ${article.title}`);

                await fetch('http://localhost:5000/api/ravens/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(article)
                });

                await new Promise(resolve => setTimeout(resolve, 500));
            }

            console.log('All articles processed and saved!');
            audioManager.play('success');
            await fetchArticles();
        } catch (err) {
            console.error("Failed to fetch and process:", err);
            audioManager.play('click');
        } finally {
            setProcessing(false);
        }
    };

    const handleAnki = async (id: number) => {
        try {
            await fetch(`http://localhost:5000/api/ravens/${id}/to-anki`, { method: 'POST' });
            audioManager.play('success');
            fetchArticles();
        } catch (err) {
            console.error("Failed to add to Anki:", err);
        }
    };

    const handleImportance = async (id: number, importance: number) => {
        try {
            await fetch(`http://localhost:5000/api/ravens/${id}/importance`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ importance })
            });
            audioManager.play('click');
            fetchArticles();
        } catch (err) {
            console.error("Failed to update importance:", err);
        }
    };

    const paperColors: Record<string, string> = {
        'GS1': '#FF6B6B',
        'GS2': '#4ECDC4',
        'GS3': '#45B7D1',
        'GS4': '#96CEB4'
    };

    return (
        <div className="ravens-simple">
            <div className="header-row">
                <h1>📰 Current Affairs for UPSC</h1>
                <button
                    className="fetch-btn"
                    onClick={fetchAndProcessLatest}
                    disabled={processing}
                >
                    {processing ? '⏳ Processing...' : '🔄 Fetch Latest News'}
                </button>
            </div>

            <div className="filters-compact">
                <select value={selectedPaper} onChange={(e) => setSelectedPaper(e.target.value)}>
                    {papers.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
                <select value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)}>
                    {subjects.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
            </div>

            {loading ? (
                <div className="loading">Loading articles...</div>
            ) : articles.length === 0 ? (
                <div className="empty">
                    <p>No articles yet. Click "Fetch Latest News" to get started!</p>
                </div>
            ) : (
                <div className="articles-grid">
                    {articles.map((article) => (
                        <div key={article.id} className="article-card">
                            <div className="article-header">
                                <div className="tags">
                                    {article.papers?.map(p => (
                                        <span key={p} className="tag paper-tag" style={{ background: paperColors[p] }}>{p}</span>
                                    ))}
                                </div>
                                <span className="date">{article.published}</span>
                            </div>

                            {article.subjects && article.subjects.length > 0 && (
                                <div className="subject-badges">
                                    {article.subjects.map((sub, idx) => (
                                        <span key={idx} className="subject-badge">{sub}</span>
                                    ))}
                                </div>
                            )}

                            <h3><a href={article.link} target="_blank" rel="noreferrer">{article.title}</a></h3>

                            <p className="summary">{article.upscSummary}</p>

                            {article.keyPoints && article.keyPoints.length > 0 && (
                                <ul className="keypoints">
                                    {article.keyPoints.slice(0, 3).map((point, idx) => (
                                        <li key={idx}>{point}</li>
                                    ))}
                                </ul>
                            )}

                            <div className="actions">
                                <select
                                    value={article.importance || 2}
                                    onChange={(e) => article.id && handleImportance(article.id, Number(e.target.value))}
                                >
                                    <option value={1}>⭐ Low</option>
                                    <option value={2}>⭐⭐ Medium</option>
                                    <option value={3}>⭐⭐⭐ High</option>
                                </select>
                                {article.ankiCardId ? (
                                    <button disabled>✅ In Anki</button>
                                ) : (
                                    <button onClick={() => article.id && handleAnki(article.id)}>
                                        📇 Add to Anki
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Ravens;