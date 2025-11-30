// frontend/src/components/Ravens/NewsCardEnhanced.tsx
import React, { useState } from 'react';

interface NewsCardProps {
    article: {
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
        isBookmarked?: boolean;
        userNotes?: string;
        ankiCardId?: number;
        imageUrl?: string;
        relatedPyqs?: Array<{ year: number; paper: string; question: string }>;
    };
    onProcess?: (article: any) => void;
    onTag?: (id: number, papers: string[], subjects: string[]) => void;
    onImportance?: (id: number, importance: number) => void;
    onBookmark?: (id: number) => void;
    onNotes?: (id: number, notes: string) => void;
    onAnki?: (id: number) => void;
}

const NewsCardEnhanced: React.FC<NewsCardProps> = ({
    article,
    onProcess,

    onImportance,
    onBookmark,
    onNotes,
    onAnki
}) => {
    const [showNotes, setShowNotes] = useState(false);
    const [notes, setNotes] = useState(article.userNotes || '');
    const [isExpanded, setIsExpanded] = useState(false);

    const isProcessed = article.upscSummary !== undefined;

    const importanceStars = ['⭐', '⭐⭐', '⭐⭐⭐'];

    const paperColors: Record<string, string> = {
        'GS1': '#FF6B6B',
        'GS2': '#4ECDC4',
        'GS3': '#45B7D1',
        'GS4': '#96CEB4',
        'Essay': '#FFEAA7',
        'Optional': '#DFE6E9'
    };

    const handleSaveNotes = () => {
        if (article.id && onNotes) {
            onNotes(article.id, notes);
            setShowNotes(false);
        }
    };

    return (
        <div className={`news-card-enhanced ${isProcessed ? 'processed' : ''}`}>
            {/* Header */}
            <div className="card-header">
                <span className="source-badge">{article.source}</span>
                <span className="date-badge">{article.published}</span>
            </div>

            {/* Image (if available) */}
            {article.imageUrl && (
                <div className="card-image">
                    <img src={article.imageUrl} alt={article.title} />
                </div>
            )}

            {/* Title */}
            <h3 className="card-title">
                <a href={article.link} target="_blank" rel="noreferrer">
                    {article.title}
                </a>
            </h3>

            {/* Tags (if processed) */}
            {isProcessed && (
                <div className="tags-container">
                    {article.papers?.map(paper => (
                        <span
                            key={paper}
                            className="tag tag-paper"
                            style={{ backgroundColor: paperColors[paper] }}
                        >
                            {paper}
                        </span>
                    ))}
                    {article.subjects?.slice(0, 3).map(subject => (
                        <span key={subject} className="tag tag-subject">
                            {subject}
                        </span>
                    ))}
                </div>
            )}

            {/* Summary */}
            <div className="card-summary">
                {isProcessed ? (
                    <>
                        <p>{article.upscSummary}</p>
                        {isExpanded && (
                            <>
                                {article.keyPoints && article.keyPoints.length > 0 && (
                                    <div className="key-points">
                                        <h4>🎯 Key Points:</h4>
                                        <ul>
                                            {article.keyPoints.map((point, idx) => (
                                                <li key={idx}>{point}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                {article.relatedPyqs && article.relatedPyqs.length > 0 && (
                                    <div className="related-pyqs">
                                        <h4>📚 Related PYQs:</h4>
                                        {article.relatedPyqs.map((pyq, idx) => (
                                            <div key={idx} className="pyq-item">
                                                <span className="pyq-year">{pyq.year} {pyq.paper}</span>
                                                <span className="pyq-question">{pyq.question}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        )}
                    </>
                ) : (
                    <p>{article.link}</p>
                )}
            </div>

            {/* Actions */}
            <div className="card-actions">
                {!isProcessed ? (
                    <button
                        className="action-btn primary"
                        onClick={() => onProcess && onProcess(article)}
                    >
                        🤖 Process with AI
                    </button>
                ) : (
                    <>
                        <button
                            className="action-btn"
                            onClick={() => setIsExpanded(!isExpanded)}
                        >
                            {isExpanded ? '📖 Show Less' : '📖 Read More'}
                        </button>

                        <button
                            className={`action-btn ${article.isBookmarked ? 'active' : ''}`}
                            onClick={() => article.id && onBookmark && onBookmark(article.id)}
                        >
                            {article.isBookmarked ? '📌 Bookmarked' : '📌 Bookmark'}
                        </button>

                        <button
                            className="action-btn"
                            onClick={() => setShowNotes(!showNotes)}
                        >
                            ✏️ Notes
                        </button>

                        {article.importance && onImportance && (
                            <select
                                className="importance-select"
                                value={article.importance}
                                onChange={(e) => article.id && onImportance(article.id, Number(e.target.value))}
                            >
                                <option value={1}>{importanceStars[0]} Low</option>
                                <option value={2}>{importanceStars[1]} Medium</option>
                                <option value={3}>{importanceStars[2]} High</option>
                            </select>
                        )}

                        {article.ankiCardId ? (
                            <button className="action-btn success" disabled>
                                ✅ In Anki
                            </button>
                        ) : (
                            <button
                                className="action-btn primary"
                                onClick={() => article.id && onAnki && onAnki(article.id)}
                            >
                                📇 Add to Anki
                            </button>
                        )}
                    </>
                )}
            </div>

            {/* Notes Editor */}
            {showNotes && (
                <div className="notes-editor">
                    <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder="Add your notes here..."
                        rows={4}
                    />
                    <div className="notes-actions">
                        <button className="action-btn primary" onClick={handleSaveNotes}>
                            💾 Save Notes
                        </button>
                        <button className="action-btn" onClick={() => setShowNotes(false)}>
                            ❌ Cancel
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default NewsCardEnhanced;
