import React, { useState } from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';
import './SubjectBookRenderer.css';

interface Chapter {
    title: string;
    content: string;
    key_concepts: string[];
}

interface SubjectBook {
    title: string;
    subject: string;
    chapters: Chapter[];
    generated_at: string;
}

interface SubjectBookRendererProps {
    content: string | SubjectBook; // Can be stringified JSON or object
}

const SubjectBookRenderer: React.FC<SubjectBookRendererProps> = ({ content }) => {
    let bookData: SubjectBook;

    try {
        bookData = typeof content === 'string' ? JSON.parse(content) : content;
    } catch (e) {
        console.error("Failed to parse Subject Book data", e);
        return <div className="error-message">📚 Book Data Corrupted</div>;
    }

    const [currentChapterIndex, setCurrentChapterIndex] = useState(0);

    const chapters = bookData.chapters || [];
    const currentChapter = chapters[currentChapterIndex];

    if (!currentChapter) {
        return <div className="empty-state">📖 This book has no pages yet.</div>;
    }

    return (
        <div className="subject-book-container">
            <div className="book-spine">
                <h2>{bookData.title || "Untitled Tome"}</h2>
                <div className="chapter-list">
                    {chapters.map((chap, idx) => (
                        <button
                            key={idx}
                            className={`chapter-tab ${idx === currentChapterIndex ? 'active' : ''}`}
                            onClick={() => setCurrentChapterIndex(idx)}
                        >
                            <span className="chapter-num">{idx + 1}</span>
                            <span className="chapter-title">{chap.title}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div className="book-page">
                <div className="page-header">
                    <h3>Chapter {currentChapterIndex + 1}: {currentChapter.title}</h3>
                    <div className="page-meta">
                        {currentChapter.key_concepts?.slice(0, 3).map((tag, i) => (
                            <span key={i} className="concept-tag">{tag}</span>
                        ))}
                    </div>
                </div>

                <div className="page-content custom-scrollbar">
                    <MarkdownRenderer content={currentChapter.content} />
                </div>

                <div className="page-footer">
                    <button
                        disabled={currentChapterIndex === 0}
                        onClick={() => setCurrentChapterIndex(p => p - 1)}
                    >
                        ← Prev
                    </button>
                    <span className="page-number">Page {currentChapterIndex + 1} of {chapters.length}</span>
                    <button
                        disabled={currentChapterIndex === chapters.length - 1}
                        onClick={() => setCurrentChapterIndex(p => p + 1)}
                    >
                        Next →
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SubjectBookRenderer;
