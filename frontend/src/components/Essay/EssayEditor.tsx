import { API_BASE_URL } from '../../config';
import React, { useState, useEffect, useRef, useCallback } from 'react';

interface EssayEditorProps {
    onSubmitSuccess: (data: any) => void;
}

const WORD_GOAL = 1200;
const AUTOSAVE_INTERVAL = 15000; // 15 seconds

const EssayEditor: React.FC<EssayEditorProps> = ({ onSubmitSuccess }) => {
    const [topics, setTopics] = useState<string[]>([]);
    const [selectedTopic, setSelectedTopic] = useState('');
    const [customTopic, setCustomTopic] = useState('');
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState(3 * 60 * 60);
    const [timerActive, setTimerActive] = useState(false);
    const [lastSaved, setLastSaved] = useState<string | null>(null);
    const [showTips, setShowTips] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => { fetchTopics(); loadDraft(); }, []);

    // Timer
    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;
        if (timerActive && timeLeft > 0) {
            interval = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
        }
        return () => clearInterval(interval);
    }, [timerActive, timeLeft]);

    // Autosave
    useEffect(() => {
        const interval = setInterval(() => {
            if (content.trim()) {
                saveDraft();
            }
        }, AUTOSAVE_INTERVAL);
        return () => clearInterval(interval);
    }, [content, selectedTopic, customTopic]);

    const saveDraft = useCallback(() => {
        const draft = {
            content,
            selectedTopic,
            customTopic,
            timeLeft,
            savedAt: new Date().toISOString()
        };
        localStorage.setItem('essay_draft', JSON.stringify(draft));
        setLastSaved(new Date().toLocaleTimeString());
    }, [content, selectedTopic, customTopic, timeLeft]);

    const loadDraft = () => {
        try {
            const saved = localStorage.getItem('essay_draft');
            if (saved) {
                const draft = JSON.parse(saved);
                setContent(draft.content || '');
                setSelectedTopic(draft.selectedTopic || '');
                setCustomTopic(draft.customTopic || '');
                if (draft.timeLeft) setTimeLeft(draft.timeLeft);
                setLastSaved(new Date(draft.savedAt).toLocaleTimeString());
            }
        } catch { /* ignore corrupt draft */ }
    };

    const clearDraft = () => {
        localStorage.removeItem('essay_draft');
        setContent('');
        setSelectedTopic('');
        setCustomTopic('');
        setTimeLeft(3 * 60 * 60);
        setTimerActive(false);
        setLastSaved(null);
    };

    const fetchTopics = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/essay/topics`);
            const data = await response.json();
            setTopics(data);
        } catch (error) {
            console.error('Error fetching topics:', error);
        }
    };

    const formatTime = (seconds: number) => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const handleSubmit = async () => {
        if (!content.trim()) return;
        const topicToSubmit = selectedTopic === 'custom' ? customTopic : selectedTopic;
        if (!topicToSubmit) return;

        setIsSubmitting(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/essay/submit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topicToSubmit, content })
            });
            const data = await response.json();
            localStorage.removeItem('essay_draft');
            onSubmitSuccess(data);
        } catch (error) {
            console.error('Error submitting essay:', error);
            alert('Failed to submit essay. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Writing stats
    const words = content.trim().split(/\s+/).filter(w => w.length > 0);
    const wordCount = words.length;
    const charCount = content.length;
    const paragraphCount = content.split(/\n\s*\n/).filter(p => p.trim().length > 0).length;
    const sentenceCount = content.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
    const readingTimeMin = Math.max(1, Math.ceil(wordCount / 200));
    const wordProgressPct = Math.min(100, (wordCount / WORD_GOAL) * 100);
    const isOverLimit = wordCount > WORD_GOAL * 1.1; // 10% buffer
    const isUnderTarget = wordCount < WORD_GOAL * 0.8; // Below 80%

    const wordProgressColor = isOverLimit ? '#ef4444' : wordProgressPct >= 80 ? '#10b981' : wordProgressPct >= 50 ? '#f59e0b' : '#64748b';

    return (
        <div className="essay-editor">
            <div className="editor-controls">
                <div className="topic-selector">
                    <label>Select Topic:</label>
                    <select
                        value={selectedTopic}
                        onChange={(e) => setSelectedTopic(e.target.value)}
                        disabled={timerActive}
                    >
                        <option value="">-- Choose a Topic --</option>
                        {topics.map((t, i) => (
                            <option key={i} value={t}>{t}</option>
                        ))}
                        <option value="custom">Custom Topic</option>
                    </select>
                </div>

                {selectedTopic === 'custom' && (
                    <input
                        type="text"
                        className="custom-topic-input"
                        placeholder="Enter your essay topic..."
                        value={customTopic}
                        onChange={(e) => setCustomTopic(e.target.value)}
                        disabled={timerActive}
                    />
                )}

                <div className="timer-control">
                    <div className={`timer-display ${timeLeft < 1800 ? 'warning' : ''} ${timeLeft < 600 ? 'critical' : ''}`}
                        style={{ animation: timeLeft < 300 && timerActive ? 'wrong-shake 1s infinite' : undefined }}>
                        {formatTime(timeLeft)}
                    </div>
                    <button
                        className={`timer-btn ${timerActive ? 'stop' : 'start'}`}
                        onClick={() => setTimerActive(!timerActive)}
                    >
                        {timerActive ? '⏸ Pause' : '▶ Start Timer'}
                    </button>
                </div>
            </div>

            {/* Writing Stats Bar */}
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.6rem 1rem', marginBottom: '0.75rem',
                background: '#0f172a', borderRadius: '8px', border: '1px solid #334155',
                fontSize: '0.85rem', flexWrap: 'wrap', gap: '0.5rem'
            }}>
                <div style={{ display: 'flex', gap: '1.2rem', alignItems: 'center' }}>
                    <span style={{ color: wordProgressColor, fontWeight: 700 }}>
                        📝 {wordCount} / {WORD_GOAL} words
                    </span>
                    <span style={{ color: '#64748b' }}>¶ {paragraphCount} paragraphs</span>
                    <span style={{ color: '#64748b' }}>📖 ~{readingTimeMin} min read</span>
                    <span style={{ color: '#64748b' }}>{sentenceCount} sentences</span>
                    <span style={{ color: '#64748b' }}>{charCount} chars</span>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    {lastSaved && (
                        <span style={{ color: '#475569', fontSize: '0.8rem' }}>💾 Saved {lastSaved}</span>
                    )}
                    <button onClick={() => setShowTips(!showTips)}
                        style={{ background: 'none', border: '1px solid #334155', color: '#94a3b8', padding: '2px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}>
                        {showTips ? '✕ Hide Tips' : '💡 Tips'}
                    </button>
                    <button onClick={saveDraft}
                        aria-label="Save Draft"
                        style={{ background: 'none', border: '1px solid #334155', color: '#94a3b8', padding: '2px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}>
                        <span aria-hidden="true">💾</span> Save
                    </button>
                    {content.trim() && (
                        <button onClick={clearDraft}
                            aria-label="Clear Draft"
                            style={{ background: 'none', border: '1px solid rgba(239,68,68,0.3)', color: '#ef4444', padding: '2px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}>
                            <span aria-hidden="true">🗑️</span> Clear
                        </button>
                    )}
                </div>
            </div>

            {/* Word Goal Progress Bar */}
            <div style={{ marginBottom: '0.75rem', background: '#1e293b', borderRadius: '4px', height: '4px', overflow: 'hidden' }}>
                <div style={{
                    width: `${Math.min(wordProgressPct, 100)}%`, height: '100%',
                    background: wordProgressColor,
                    transition: 'width 0.3s ease, background 0.3s ease',
                    borderRadius: '4px'
                }} />
            </div>

            {/* Writing Tips Panel */}
            {showTips && (
                <div style={{
                    background: '#0f172a', border: '1px solid rgba(245, 158, 11, 0.2)',
                    borderLeft: '3px solid #f59e0b', borderRadius: '8px',
                    padding: '1rem 1.25rem', marginBottom: '0.75rem', fontSize: '0.85rem', color: '#94a3b8'
                }}>
                    <h4 style={{ color: '#f59e0b', margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>📐 UPSC Essay Structure Guide</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                        <div><strong style={{ color: '#e2e8f0' }}>Introduction (~150 words)</strong> — Hook + thesis + roadmap</div>
                        <div><strong style={{ color: '#e2e8f0' }}>Body 1 (~200 words)</strong> — Main argument with examples</div>
                        <div><strong style={{ color: '#e2e8f0' }}>Body 2 (~200 words)</strong> — Counter-point or second dimension</div>
                        <div><strong style={{ color: '#e2e8f0' }}>Body 3 (~200 words)</strong> — Case studies / data / quotes</div>
                        <div><strong style={{ color: '#e2e8f0' }}>Body 4 (~200 words)</strong> — Government initiatives / reforms</div>
                        <div><strong style={{ color: '#e2e8f0' }}>Conclusion (~150 words)</strong> — Synthesis + forward-looking view</div>
                    </div>
                    <p style={{ marginTop: '0.5rem', color: '#64748b', fontSize: '0.8rem' }}>
                        Target: {WORD_GOAL} words • 6-8 paragraphs • Use quotes, data, committee reports • Balance multiple perspectives
                    </p>
                </div>
            )}

            {/* Editor Area */}
            <div className="editor-area">
                <textarea
                    ref={textareaRef}
                    placeholder="Start writing your essay here...&#10;&#10;Tip: Use paragraphs to structure your argument. UPSC values structured, multi-dimensional essays."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    disabled={isSubmitting}
                    style={{ minHeight: '500px' }}
                />
                <div className="editor-footer">
                    <span className="word-count" style={{ color: wordProgressColor }}>
                        {wordCount} / {WORD_GOAL} words
                        {isOverLimit && ' ⚠️ Over limit'}
                        {!isOverLimit && !isUnderTarget && wordCount > 0 && ' ✅ Good length'}
                        {isUnderTarget && wordCount > 0 && ` (${WORD_GOAL - wordCount} more needed)`}
                    </span>
                    <button
                        className="submit-btn"
                        onClick={handleSubmit}
                        disabled={isSubmitting || !content.trim() || (!selectedTopic && !customTopic)}
                    >
                        {isSubmitting ? '⏳ Evaluating...' : '🚀 Submit for Evaluation'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EssayEditor;
