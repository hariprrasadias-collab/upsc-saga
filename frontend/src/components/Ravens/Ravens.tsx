import React, { useState, useEffect } from 'react';
import './Ravens.css';
import { audioManager } from '../../util/AudioManager';
import { useToast } from '../Toast';
import IssueMappingViewer from '../IssueMapping/IssueMappingViewer';

type RelatedPyq = {
    year: string;
    question: string;
};

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
    isBookmarked?: boolean;
    userNotes?: string;
    imageUrl?: string;
    relatedPyqs?: RelatedPyq[];
}

const Ravens: React.FC = () => {
    const [articles, setArticles] = useState<Article[]>([]);
    const [loading, setLoading] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [processingStatus, setProcessingStatus] = useState<string>('');
    const [selectedPaper, setSelectedPaper] = useState<string>('');
    const [selectedSubject, setSelectedSubject] = useState<string>('');
    const [selectedSource, setSelectedSource] = useState<string>('All Sources');
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [showBookmarked, setShowBookmarked] = useState<boolean>(false);
    const [editingNotes, setEditingNotes] = useState<number | null>(null);
    const [mappingArticleId, setMappingArticleId] = useState<number | null>(null);
    const { addToast } = useToast();

    const papers = ['All Papers', 'GS1', 'GS2', 'GS3', 'GS4'];
    const subjects = ['All Subjects', 'Polity & Governance', 'Economics', 'International Relations',
        'Environment & Ecology', 'Science & Technology', 'Internal Security', 'Social Issues'];

    useEffect(() => {
        fetchArticles();
    }, [selectedPaper, selectedSubject, selectedSource, showBookmarked, searchQuery]);

    const fetchArticles = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (selectedPaper && selectedPaper !== 'All Papers') params.append('paper', selectedPaper);
            if (selectedSubject && selectedSubject !== 'All Subjects') params.append('subject', selectedSubject);
            if (selectedSource && selectedSource !== 'All Sources') params.append('source', selectedSource);
            if (showBookmarked) params.append('bookmarked', 'true');
            if (searchQuery) params.append('search', searchQuery);

            const res = await fetch(`http://localhost:5000/api/ravens/saved?${params}`);
            if (res.ok) {
                const data = await res.json();
                setArticles(data);
            }
        } catch (err) {
            console.error("Error fetching articles:", err);
            addToast('Failed to fetch articles', 'error');
        } finally {
            setLoading(false);
        }
    };

    const fetchAndProcessLatest = async () => {
        setProcessing(true);
        setProcessingStatus('Scouting for news...');
        audioManager.play('click');

        try {
            const muninRes = await fetch('http://localhost:5000/api/ravens?type=munin');
            const huginRes = await fetch('http://localhost:5000/api/ravens?type=hugin');

            const muninNews = await muninRes.json();
            const huginNews = await huginRes.json();
            const allNews = [...muninNews, ...huginNews];

            setProcessingStatus(`Found ${allNews.length} articles. Processing...`);

            for (let i = 0; i < allNews.length; i++) {
                const article = allNews[i];
                setProcessingStatus(`Processing ${i + 1}/${allNews.length}: ${article.title.substring(0, 30)}...`);

                await fetch('http://localhost:5000/api/ravens/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(article)
                });

                await new Promise(resolve => setTimeout(resolve, 500));
            }

            setProcessingStatus('All articles processed!');
            audioManager.play('success');
            await fetchArticles();
        } catch (err) {
            console.error("Failed to fetch and process:", err);
            setProcessingStatus('Error processing articles.');
            audioManager.play('click');
            addToast('Error processing articles', 'error');
        } finally {
            setProcessing(false);
            setProcessingStatus('');
        }
    };

    const handleAddToLore = async (article: Article) => {
        try {
            const content = `Source: ${article.source}\nPublished: ${article.published}\nLink: ${article.link}\n\nSummary:\n${article.upscSummary}\n\nKey Points:\n${article.keyPoints?.map(p => `- ${p}`).join('\n')}`;

            const res = await fetch('http://localhost:5000/api/lore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: article.title,
                    content: content
                })
            });

            if (res.ok) {
                addToast('Added to Lore Tablet', 'success');
                audioManager.play('success');
            } else {
                addToast('Failed to add to Lore', 'error');
            }
        } catch (err) {
            console.error("Failed to add to Lore:", err);
            addToast('Error adding to Lore', 'error');
        }
    };

    const handleAnki = async (id: number) => {
        try {
            await fetch(`http://localhost:5000/api/ravens/${id}/to-anki`, { method: 'POST' });
            audioManager.play('success');
            addToast('Added to Anki', 'success');
            fetchArticles();
        } catch (err) {
            console.error("Failed to add to Anki:", err);
            addToast('Failed to add to Anki', 'error');
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

    const handleBookmark = async (id: number) => {
        try {
            await fetch(`http://localhost:5000/api/ravens/${id}/bookmark`, { method: 'POST' });
            audioManager.play('click');
            fetchArticles();
        } catch (err) {
            console.error("Failed to toggle bookmark:", err);
        }
    };

    const handleNotesSave = async (id: number, notes: string) => {
        try {
            await fetch(`http://localhost:5000/api/ravens/${id}/notes`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes })
            });
            setEditingNotes(null);
            addToast('Notes saved', 'success');
        } catch (err) {
            console.error("Failed to save notes:", err);
            addToast('Failed to save notes', 'error');
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

            <div className="filters-enhanced">
                <input
                    type="text"
                    placeholder="🔍 Search articles..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                />
                <select value={selectedPaper} onChange={(e) => setSelectedPaper(e.target.value)}>
                    {papers.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
                <select value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)}>
                    {subjects.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <select
                    value={selectedSource}
                    onChange={(e) => setSelectedSource(e.target.value)}
                    className="source-select"
                >
                    <option value="All Sources">All Sources</option>
                    <option value="The Hindu">The Hindu</option>
                    <option value="Indian Express">Indian Express</option>
                    <option value="PIB">PIB</option>
                    <option value="LiveMint">LiveMint</option>
                    <option value="Project Syndicate">Project Syndicate</option>
                </select>
                <button
                    className={`bookmark-filter ${showBookmarked ? 'active' : ''}`}
                    onClick={() => setShowBookmarked(!showBookmarked)}
                >
                    {showBookmarked ? '⭐ Showing Bookmarked' : '☆ All Articles'}
                </button>
            </div>

            {processing && (
                <div className="processing-indicator">
                    <div className="spinner"></div>
                    <p>{processingStatus}</p>
                </div>
            )}

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
                            {article.imageUrl && (
                                <div className="article-image">
                                    <img src={article.imageUrl} alt={article.title} />
                                </div>
                            )}

                            <div className="article-header">
                                <div className="tags">
                                    {article.papers?.map(p => (
                                        <span key={p} className="tag paper-tag" style={{ background: paperColors[p] }}>{p}</span>
                                    ))}
                                </div>
                                <div className="header-actions">
                                    <span className="date">{article.published}</span>
                                    <button
                                        className="bookmark-btn"
                                        onClick={() => article.id && handleBookmark(article.id)}
                                    >
                                        {article.isBookmarked ? '⭐' : '☆'}
                                    </button>
                                </div>
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

                            {article.relatedPyqs && article.relatedPyqs.length > 0 && (
                                <div className="pyq-section">
                                    <strong>📚 Related PYQs:</strong>
                                    {article.relatedPyqs.map((pyq, idx) => (
                                        <div key={idx} className="pyq-item">
                                            <span className="pyq-year">{pyq.year}</span> - {pyq.question}
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="notes-section">
                                {editingNotes === article.id ? (
                                    <div className="notes-editor">
                                        <textarea
                                            defaultValue={article.userNotes || ''}
                                            placeholder="Add your notes here..."
                                            onBlur={(e) => article.id && handleNotesSave(article.id, e.target.value)}
                                            autoFocus
                                        />
                                    </div>
                                ) : (
                                    <div className="notes-display" onClick={() => setEditingNotes(article.id || null)}>
                                        <span className="notes-label">📝 Notes:</span>
                                        <span className="notes-text">{article.userNotes || 'Click to add notes...'}</span>
                                    </div>
                                )}
                            </div>

                            <div className="actions">
                                <select
                                    value={article.importance || 2}
                                    onChange={(e) => article.id && handleImportance(article.id, Number(e.target.value))}
                                >
                                    <option value={1}>⭐ Low</option>
                                    <option value={2}>⭐⭐ Medium</option>
                                    <option value={3}>⭐⭐⭐ High</option>
                                </select>
                                {article.id && (
                                    <button
                                        className="mapping-btn"
                                        onClick={() => setMappingArticleId(prev => prev === article.id ? null : (article.id ?? null))}
                                    >
                                        {mappingArticleId === article.id ? 'Hide Mapping' : 'Show Mapping'}
                                    </button>
                                )}

                                <button
                                    className="action-btn lore-btn"
                                    onClick={() => handleAddToLore(article)}
                                    title="Save to Lore Tablet"
                                >
                                    📜 Add to Lore
                                </button>

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
            {mappingArticleId && (
                <IssueMappingViewer articleId={mappingArticleId} />
            )}
        </div>
    );
};

export default Ravens;