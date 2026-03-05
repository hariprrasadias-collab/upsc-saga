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
    content: string | SubjectBook;
}

const tryParseBook = (raw: string): SubjectBook | null => {
    try {
        const tryJSON = (s: string) => {
            try { return JSON.parse(s); } catch { }
            // Fix literal newlines inside JSON string values
            let result = '', inStr = false, esc = false;
            for (let i = 0; i < s.length; i++) {
                const c = s[i];
                if (esc) { result += c; esc = false; continue; }
                if (c === '\\') { result += c; esc = true; continue; }
                if (c === '"') { inStr = !inStr; result += c; continue; }
                if (inStr && c === '\n') { result += '\\n'; continue; }
                if (inStr && c === '\t') { result += '\\t'; continue; }
                result += c;
            }
            try { return JSON.parse(result); } catch { return null; }
        };

        const parsed = typeof raw === 'string' ? tryJSON(raw) : raw;
        if (!parsed) return null;

        if (parsed.chapters && Array.isArray(parsed.chapters)) {
            return parsed as SubjectBook;
        }

        // Unwrap debug envelope {thought_process, response_text}
        if (parsed.response_text) {
            let innerText = parsed.response_text;
            const jsonMatch = innerText.match(/```json\s*\n?([\s\S]*?)\n?```/);
            if (jsonMatch) {
                innerText = jsonMatch[1].trim();
            }
            return tryParseBook(innerText);
        }

        return null;
    } catch {
        return null;
    }
};

const extractFallbackText = (content: string | SubjectBook): string => {
    const rawText = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
    try {
        const parsed = JSON.parse(rawText);
        if (parsed.response_text) {
            return parsed.response_text.replace(/```json\s*\n?/g, '').replace(/\n?```/g, '');
        }
    } catch { }
    return rawText;
};

const SubjectBookFallback: React.FC<{ content: string | SubjectBook }> = ({ content }) => {
    const displayText = extractFallbackText(content);
    return (
        <div className="subject-book-container" style={{ padding: '20px' }}>
            <h3 style={{ color: '#f0c040' }}>📚 Subject Book (Legacy Format)</h3>
            <MarkdownRenderer content={displayText} />
        </div>
    );
};

const SubjectBookContent: React.FC<{ bookData: SubjectBook }> = ({ bookData }) => {
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
                    {chapters.map((chap: Chapter, idx: number) => (
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
                        {currentChapter.key_concepts?.slice(0, 3).map((tag: string, i: number) => (
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

const SubjectBookRenderer: React.FC<SubjectBookRendererProps> = ({ content }) => {
    const bookData = tryParseBook(typeof content === 'string' ? content : JSON.stringify(content));

    if (!bookData) {
        return <SubjectBookFallback content={content} />;
    }

    return <SubjectBookContent bookData={bookData} />;
};

export default SubjectBookRenderer;
