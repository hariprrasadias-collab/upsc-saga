import React, { useState, useMemo, useEffect } from 'react';
import './Renderers.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';
import { API_BASE_URL } from '../../../config';

interface QuizItem {
    question: string;
    options: string[];
    answer: string;
}

interface ELI5Data {
    eli5: string;
    eli15: string;
    eli_expert: string;
    analogy: string;
    visual_analogy_prompt?: string;
    real_world_example: string;
    quiz?: QuizItem[];
}

interface ELI5Props {
    content: string;
}

const ELI5Renderer: React.FC<ELI5Props> = ({ content }) => {
    // 1. Parse content (handle debug envelope + error objects)
    const data: ELI5Data = useMemo(() => {
        const fallback: ELI5Data = {
            eli5: content,
            eli15: "",
            eli_expert: "",
            analogy: "",
            real_world_example: "",
            visual_analogy_prompt: "",
            quiz: []
        };
        try {
            let parsed = JSON.parse(content);

            // Handle error objects
            if (parsed.error) {
                return { ...fallback, eli5: `⚠️ ${parsed.error}: Content generation was limited. Try regenerating.` };
            }

            // Unwrap debug envelope
            if (parsed.response_text && !parsed.eli5) {
                let inner = parsed.response_text;
                const jsonMatch = inner.match(/```json\s*\n?([\s\S]*?)\n?```/);
                if (jsonMatch) inner = jsonMatch[1].trim();
                try { parsed = JSON.parse(inner); } catch { return { ...fallback, eli5: inner }; }
            }

            if (typeof parsed === 'object' && parsed !== null && parsed.eli5) {
                return parsed as ELI5Data;
            }
            return fallback;
        } catch (e) {
            return fallback;
        }
    }, [content]);

    const [level, setLevel] = useState<'eli5' | 'eli15' | 'eli_expert'>('eli5');
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [isGeneratingImg, setIsGeneratingImg] = useState(false);
    const [quizAnswers, setQuizAnswers] = useState<{ [key: number]: string }>({});
    const [showQuizResult, setShowQuizResult] = useState<{ [key: number]: boolean }>({});

    // TTS cleanup
    useEffect(() => {
        return () => {
            if (window.speechSynthesis) window.speechSynthesis.cancel();
        };
    }, []);

    const speak = (text: string) => {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = level === 'eli5' ? 1.2 : 1.0;
        window.speechSynthesis.speak(utterance);
    };

    const generateImage = async () => {
        if (!data.visual_analogy_prompt) return;
        setIsGeneratingImg(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/generate-image`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: data.visual_analogy_prompt })
            });
            const result = await response.json();
            if (result.success && result.image_url) {
                setGeneratedImage(result.image_url);
            }
        } catch (e) {
            console.error('ELI5 image gen failed:', e);
        } finally {
            setIsGeneratingImg(false);
        }
    };

    const handleQuizOption = (qIndex: number, option: string) => {
        if (showQuizResult[qIndex]) return; // locked
        setQuizAnswers(prev => ({ ...prev, [qIndex]: option }));
        setShowQuizResult(prev => ({ ...prev, [qIndex]: true }));
    };

    const getIconForLevel = () => {
        switch (level) {
            case 'eli5': return '🧸';
            case 'eli15': return '🎒';
            case 'eli_expert': return '🎓';
            default: return '🧸';
        }
    };

    const activeContent = data[level] || "Content not available.";

    return (
        <div className="eli5-container glass-card advanced-eli5">
            <div className="eli5-header-row">
                <div className="eli5-title-group">
                    <span className="eli5-icon-large">{getIconForLevel()}</span>
                    <h2>{level === 'eli5' ? "Explain Like I'm 5" : level === 'eli15' ? "Explain Like I'm 15" : "Professor Mode"}</h2>
                </div>
                <button className="tts-btn" onClick={() => speak(activeContent)} title="Read Aloud">🔊</button>
            </div>

            {data.eli15 && (
                <div className="eli5-tabs">
                    {(['eli5', 'eli15', 'eli_expert'] as const).map(l => (
                        <button
                            key={l}
                            className={`tab-btn ${level === l ? 'active' : ''}`}
                            onClick={() => setLevel(l)}
                        >
                            {l === 'eli5' ? '🧸 5yo' : l === 'eli15' ? '🎒 15yo' : '🎓 Expert'}
                        </button>
                    ))}
                </div>
            )}

            <div className={`eli5-content fade-in ${level}`}>
                <MarkdownRenderer content={activeContent} />
            </div>

            {/* Extras: Analogy & Real World */}
            {(data.analogy || data.real_world_example) && (
                <div className="eli5-extras">
                    {data.analogy && (
                        <div className="extra-card analogy-card">
                            <div className="card-label">💡 The Analogy</div>
                            <p>{data.analogy}</p>
                            {data.visual_analogy_prompt && !generatedImage && (
                                <button
                                    className="gen-img-btn"
                                    onClick={generateImage}
                                    disabled={isGeneratingImg}
                                >
                                    {isGeneratingImg ? '🎨 Painting...' : '🎨 Visualize This'}
                                </button>
                            )}
                            {generatedImage && (
                                <div className="analogy-image-container fade-in">
                                    <img src={generatedImage} alt="Analogy visualization" />
                                </div>
                            )}
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

            {/* Quiz Section */}
            {data.quiz && data.quiz.length > 0 && (
                <div className="eli5-quiz-section">
                    <h3>🧠 Quick Check</h3>
                    <div className="quiz-grid">
                        {data.quiz.map((q, idx) => (
                            <div key={idx} className="quiz-card">
                                <p className="quiz-question">{q.question}</p>
                                <div className="quiz-options">
                                    {q.options.map((opt, oIdx) => {
                                        const isSelected = quizAnswers[idx] === opt;
                                        const isCorrect = opt === q.answer;
                                        const showResult = showQuizResult[idx];

                                        let btnClass = "quiz-opt-btn";
                                        if (showResult) {
                                            if (isCorrect) btnClass += " correct";
                                            else if (isSelected) btnClass += " wrong";
                                        }

                                        return (
                                            <button
                                                key={oIdx}
                                                className={btnClass}
                                                onClick={() => handleQuizOption(idx, opt)}
                                                disabled={showResult}
                                            >
                                                {opt}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="eli5-footer">
                <span className="tag">#Simplified</span>
                <span className="tag">#Interactive</span>
            </div>
        </div>
    );
};

export default ELI5Renderer;
