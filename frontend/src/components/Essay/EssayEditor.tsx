import React, { useState, useEffect } from 'react';

interface EssayEditorProps {
    onSubmitSuccess: (data: any) => void;
}

const EssayEditor: React.FC<EssayEditorProps> = ({ onSubmitSuccess }) => {
    const [topics, setTopics] = useState<string[]>([]);
    const [selectedTopic, setSelectedTopic] = useState('');
    const [customTopic, setCustomTopic] = useState('');
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState(3 * 60 * 60); // 3 hours in seconds
    const [timerActive, setTimerActive] = useState(false);

    useEffect(() => {
        fetchTopics();
    }, []);

    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;
        if (timerActive && timeLeft > 0) {
            interval = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [timerActive, timeLeft]);

    const fetchTopics = async () => {
        try {
            const response = await fetch('/api/essay/topics');
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
            const response = await fetch('/api/essay/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: topicToSubmit,
                    content: content
                })
            });
            const data = await response.json();
            onSubmitSuccess(data);
        } catch (error) {
            console.error('Error submitting essay:', error);
            alert('Failed to submit essay. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const wordCount = content.trim().split(/\s+/).filter(w => w.length > 0).length;

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
                    <div className={`timer-display ${timeLeft < 1800 ? 'warning' : ''}`}>
                        {formatTime(timeLeft)}
                    </div>
                    <button
                        className={`timer-btn ${timerActive ? 'stop' : 'start'}`}
                        onClick={() => setTimerActive(!timerActive)}
                    >
                        {timerActive ? 'Pause Timer' : 'Start Timer'}
                    </button>
                </div>
            </div>

            <div className="editor-area">
                <textarea
                    placeholder="Start writing your essay here..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    disabled={isSubmitting}
                />
                <div className="editor-footer">
                    <span className="word-count">Words: {wordCount} / 1200</span>
                    <button
                        className="submit-btn"
                        onClick={handleSubmit}
                        disabled={isSubmitting || !content.trim() || (!selectedTopic && !customTopic)}
                    >
                        {isSubmitting ? 'Evaluating...' : 'Submit for Evaluation'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EssayEditor;
