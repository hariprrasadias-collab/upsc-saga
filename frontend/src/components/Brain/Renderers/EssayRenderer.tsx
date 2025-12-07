import React, { useState, useEffect } from 'react';
import './Renderers.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface EssayRendererProps {
    content: string; // The prompt and thesis
}

// Simple hash to use as key for local storage based on content
const getHash = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = (hash << 5) - hash + char;
        hash = hash & hash;
    }
    return hash;
};

const EssayRenderer: React.FC<EssayRendererProps> = ({ content }) => {
    const [showThesis, setShowThesis] = useState(false);
    const contentHash = getHash(content);
    const [userEssay, setUserEssay] = useState(() => {
        return localStorage.getItem(`essay_draft_${contentHash}`) || '';
    });
    const [isTimerRunning, setIsTimerRunning] = useState(false);
    const [timeLeft, setTimeLeft] = useState(3 * 60 * 60); // 3 hours in seconds

    useEffect(() => {
        localStorage.setItem(`essay_draft_${contentHash}`, userEssay);
    }, [userEssay, contentHash]);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isTimerRunning && timeLeft > 0) {
            interval = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
            }, 1000);
        } else if (timeLeft === 0) {
            setIsTimerRunning(false);
        }
        return () => clearInterval(interval);
    }, [isTimerRunning, timeLeft]);

    const formatTime = (seconds: number) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes
            .toString()
            .padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const toggleTimer = () => {
        if (timeLeft === 0) {
            setTimeLeft(3 * 60 * 60); // Reset timer if finished
            setIsTimerRunning(true);
        } else {
            setIsTimerRunning(!isTimerRunning);
        }
    };

    const handleDownload = () => {
        const element = document.createElement("a");
        const file = new Blob([`ESSAY TOPIC:\n${content}\n\n---\n\nMY RESPONSE:\n\n${userEssay}`], {type: 'text/plain'});
        element.href = URL.createObjectURL(file);
        element.download = "upsc_essay_draft.txt";
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    const wordCount = userEssay.trim().split(/\s+/).filter(Boolean).length;
    const wordTarget = 1200;
    const progress = Math.min((wordCount / wordTarget) * 100, 100);

    return (
        <div className="essay-renderer-container">
            <div className="essay-paper glass-card">
                <div className="paper-header">
                    <span className="paper-icon">✍️</span>
                    <h3>UPSC Mains Evaluator</h3>
                    <span className="paper-marks">250 Marks</span>
                </div>

                <div className="paper-content">
                    <div className="prompt-section">
                        <h4>Essay Topic</h4>
                        <div className="prompt-text">
                            <MarkdownRenderer content={content} />
                        </div>
                    </div>

                    <div className="thesis-hint-section">
                        <button
                            className="reveal-btn"
                            onClick={() => setShowThesis(!showThesis)}
                        >
                            {showThesis ? '🙈 Hide Thesis Hint' : '💡 Reveal Thesis Hint'}
                        </button>

                        {showThesis && (
                            <div className="thesis-content glass-panel">
                                <p>
                                    <em>Analysis:</em> Look for key keywords in the prompt above.
                                    (Note: Full thesis decomposition is available in the 'Socratic' mode).
                                </p>
                            </div>
                        )}
                    </div>

                    <div className="writing-section">
                        <h4>Your Response</h4>
                        <textarea
                            className="essay-textarea"
                            placeholder="Start writing your essay here..."
                            value={userEssay}
                            onChange={(e) => setUserEssay(e.target.value)}
                            rows={15}
                        />
                        <div className="essay-stats-bar">
                            <div className="word-count-group">
                                <div className="progress-ring-mini" style={{background: `conic-gradient(#4ade80 ${progress}%, #333 ${progress}%)`}}></div>
                                <span>{wordCount} / {wordTarget} words</span>
                            </div>
                            <button className="download-btn" onClick={handleDownload}>
                                💾 Download .txt
                            </button>
                        </div>
                    </div>
                </div>

                <div className="paper-footer">
                    <span className={`timer-display ${timeLeft < 300 ? 'urgent' : ''}`}>Time Left: {formatTime(timeLeft)}</span>
                    <button
                        className={`start-writing-btn ${isTimerRunning ? 'active' : ''}`}
                        onClick={toggleTimer}
                    >
                        {isTimerRunning ? 'Pause Timer' : 'Start Writing Timer'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EssayRenderer;
