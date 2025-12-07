import React, { useState, useMemo, useEffect } from 'react';
import './Renderers.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface ELI5Props {
    content: string;
}

interface ELI5Data {
    eli5: string;
    eli15: string;
    eli_expert: string;
    analogy: string;
    real_world_example: string;
}

const ELI5Renderer: React.FC<ELI5Props> = ({ content }) => {
    // 1. Parse content (JSON or Legacy String)
    const data: ELI5Data = useMemo(() => {
        try {
            const parsed = JSON.parse(content);
            if (typeof parsed === 'object' && parsed !== null && parsed.eli5) {
                return parsed as ELI5Data;
            }
            throw new Error("Not structured data");
        } catch (e) {
            // Legacy fallback
            return {
                eli5: content,
                eli15: "",
                eli_expert: "",
                analogy: "",
                real_world_example: ""
            };
        }
    }, [content]);

    // 2. State for Tabs/Levels
    const [level, setLevel] = useState<'eli5' | 'eli15' | 'eli_expert'>('eli5');

    // 3. TTS Functionality
    useEffect(() => {
        return () => {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        };
    }, []);

    const speak = (text: string) => {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = level === 'eli5' ? 1.2 : 1.0; // Slightly higher pitch for "kid" mode fun
        window.speechSynthesis.speak(utterance);
    };

    const getIconForLevel = () => {
        switch (level) {
            case 'eli5': return '🧸';
            case 'eli15': return '🎒';
            case 'eli_expert': return '🎓';
            default: return '🧸';
        }
    };

    const getTitleForLevel = () => {
        switch (level) {
            case 'eli5': return "Explain Like I'm 5";
            case 'eli15': return "Explain Like I'm 15";
            case 'eli_expert': return "Professor Mode";
        }
    };

    const activeContent = data[level] || "Content not available for this level.";

    return (
        <div className="eli5-container glass-card advanced-eli5">
            <div className="eli5-header-row">
                <div className="eli5-title-group">
                    <span className="eli5-icon-large">{getIconForLevel()}</span>
                    <h2>{getTitleForLevel()}</h2>
                </div>

                <div className="eli5-controls">
                    <button
                        className="tts-btn"
                        onClick={() => speak(activeContent)}
                        title="Read Aloud"
                    >
                        🔊
                    </button>
                </div>
            </div>

            {/* Level Selector Tabs */}
            {data.eli15 && (
                <div className="eli5-tabs">
                    <button
                        className={`tab-btn ${level === 'eli5' ? 'active' : ''}`}
                        onClick={() => setLevel('eli5')}
                    >
                        🧸 5yo
                    </button>
                    <button
                        className={`tab-btn ${level === 'eli15' ? 'active' : ''}`}
                        onClick={() => setLevel('eli15')}
                    >
                        🎒 15yo
                    </button>
                    <button
                        className={`tab-btn ${level === 'eli_expert' ? 'active' : ''}`}
                        onClick={() => setLevel('eli_expert')}
                    >
                        🎓 Expert
                    </button>
                </div>
            )}

            {/* Main Explanation */}
            <div className={`eli5-content fade-in ${level}`}>
                <MarkdownRenderer content={activeContent} />
            </div>

            {/* Extra Sections (Analogy & Real World) */}
            {(data.analogy || data.real_world_example) && (
                <div className="eli5-extras">
                    {data.analogy && (
                        <div className="extra-card analogy-card">
                            <div className="card-label">💡 The Analogy</div>
                            <p>{data.analogy}</p>
                        </div>
                    )}

                    {data.real_world_example && (
                        <div className="extra-card example-card">
                            <div className="card-label">🌍 Real World</div>
                            <p>{data.real_world_example}</p>
                        </div>
                    )}
                </div>
            )}

            <div className="eli5-footer">
                <span className="tag">#Simplified</span>
                <span className="tag">#Learning</span>
                {level === 'eli_expert' && <span className="tag">#Academic</span>}
            </div>
        </div>
    );
};

export default ELI5Renderer;
