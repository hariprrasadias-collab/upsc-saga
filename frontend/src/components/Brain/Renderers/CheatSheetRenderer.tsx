import React, { useState, useEffect, useRef } from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';
import mermaid from 'mermaid';
import { motion, AnimatePresence } from 'framer-motion';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import './CheatSheetRenderer.css';

interface CheatSheetTab {
    id: string;
    label: string;
    content: string;
    type?: string; // 'markdown', 'mermaid', 'quiz'
}

interface CheatSheetData {
    title: string;
    tabs: CheatSheetTab[];
}

interface CheatSheetRendererProps {
    content: string;
}

// Mermaid Renderer Component
const MermaidDiagram: React.FC<{ code: string }> = ({ code }) => {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (ref.current) {
            try {
                mermaid.initialize({ startOnLoad: true, theme: 'dark' });
                mermaid.run({ nodes: [ref.current] });
            } catch (e) {
                console.error("Mermaid Render Error:", e);
            }
        }
    }, [code]);

    return (
        <div className="mermaid-container">
            <div ref={ref} className="mermaid">{code}</div>
        </div>
    );
};

// Quiz Component
const ActiveRecallQuiz: React.FC<{ content: string }> = ({ content }) => {
    const [questions, setQuestions] = useState<{q: string, a: string}[]>([]);
    const [revealed, setRevealed] = useState<number[]>([]);

    useEffect(() => {
        try {
            const parsed = JSON.parse(content);
            if (Array.isArray(parsed)) {
                setQuestions(parsed);
            }
        } catch (e) {
            console.error("Quiz Parse Error", e);
        }
    }, [content]);

    const toggleReveal = (index: number) => {
        if (revealed.includes(index)) {
            setRevealed(prev => prev.filter(i => i !== index));
        } else {
            setRevealed(prev => [...prev, index]);
        }
    };

    return (
        <div className="quiz-container">
            {questions.map((item, index) => (
                <motion.div
                    key={index}
                    className="quiz-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => toggleReveal(index)}
                >
                    <div className="quiz-q">❓ {item.q}</div>
                    <AnimatePresence>
                        {revealed.includes(index) && (
                            <motion.div
                                className="quiz-a"
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                            >
                                ✅ {item.a}
                            </motion.div>
                        )}
                    </AnimatePresence>
                    {!revealed.includes(index) && <div className="click-hint">(Click to reveal)</div>}
                </motion.div>
            ))}
        </div>
    );
};

const CheatSheetRenderer: React.FC<CheatSheetRendererProps> = ({ content }) => {
    const [data, setData] = useState<CheatSheetData | null>(null);
    const [activeTab, setActiveTab] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');
    const [isLegacy, setIsLegacy] = useState<boolean>(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        try {
            const parsed = JSON.parse(content);
            if (parsed.tabs && Array.isArray(parsed.tabs)) {
                setData(parsed);
                if (parsed.tabs.length > 0) {
                    setActiveTab(parsed.tabs[0].id);
                }
                setIsLegacy(false);
            } else {
                setIsLegacy(true);
            }
        } catch (e) {
            setIsLegacy(true);
        }
    }, [content]);

    const handleSpeak = () => {
        if (isSpeaking) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
            return;
        }

        if (!data) return;

        const currentTabObj = data.tabs.find(t => t.id === activeTab);
        if (currentTabObj) {
            // If quiz, read Q&A
            let textToRead = currentTabObj.content;
            if (currentTabObj.type === 'quiz') {
                try {
                    const qData = JSON.parse(currentTabObj.content);
                    textToRead = qData.map((x: any) => `Question: ${x.q}. Answer: ${x.a}`).join('. ');
                } catch {}
            }

            const utterance = new SpeechSynthesisUtterance(textToRead);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.onend = () => setIsSpeaking(false);
            window.speechSynthesis.speak(utterance);
            setIsSpeaking(true);
        }
    };

    const handleExportPDF = async () => {
        if (!containerRef.current || !data) return;

        const element = containerRef.current;
        const canvas = await html2canvas(element, { backgroundColor: '#1a1a1a' });
        const imgData = canvas.toDataURL('image/png');

        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgProps = pdf.getImageProperties(imgData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(`${data.title.replace(/\s+/g, '_')}_CheatSheet.pdf`);
    };

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            containerRef.current?.requestFullscreen().catch(err => {
                console.error(`Error attempting to enable fullscreen: ${err.message}`);
            });
            setIsFullscreen(true);
        } else {
            document.exitFullscreen();
            setIsFullscreen(false);
        }
    };

    // Listen for fullscreen change events (ESC key)
    useEffect(() => {
        const handleFSChange = () => {
            setIsFullscreen(!!document.fullscreenElement);
        };
        document.addEventListener('fullscreenchange', handleFSChange);
        return () => document.removeEventListener('fullscreenchange', handleFSChange);
    }, []);

    const hasMatch = (tab: CheatSheetTab) => {
        if (!searchTerm) return false;
        return tab.content.toLowerCase().includes(searchTerm.toLowerCase());
    };

    if (isLegacy) {
        return (
            <div className="cheat-sheet-legacy">
                <div className="legacy-badge">Legacy Format</div>
                <MarkdownRenderer content={content} />
            </div>
        );
    }

    if (!data) return <div className="loading-pulse">Deciphering Codex...</div>;

    return (
        <div className={`cheat-sheet-container ${isFullscreen ? 'fullscreen-mode' : ''}`} ref={containerRef}>
            <header className="cs-header">
                <h3 className="cs-title">{data.title}</h3>
                <div className="cs-controls">
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="cs-search-input"
                    />
                    <button
                        className={`cs-action-btn ${isSpeaking ? 'active' : ''}`}
                        onClick={handleSpeak}
                        title={isSpeaking ? "Stop Speaking" : "Read Aloud"}
                    >
                        {isSpeaking ? '🔇' : '🔊'}
                    </button>
                    <button
                        className="cs-action-btn"
                        onClick={handleExportPDF}
                        title="Export to PDF"
                    >
                        📄
                    </button>
                    <button
                        className="cs-action-btn"
                        onClick={toggleFullscreen}
                        title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
                    >
                        {isFullscreen ? '🔽' : '⛶'}
                    </button>
                </div>
            </header>

            <div className="cs-tabs-nav">
                {data.tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`cs-tab-btn ${activeTab === tab.id ? 'active' : ''} ${hasMatch(tab) ? 'match-highlight' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                        {hasMatch(tab) && <span className="match-dot" />}
                    </button>
                ))}
            </div>

            <div className="cs-tab-content glass-panel">
                {data.tabs.map(tab => (
                    <div
                        key={tab.id}
                        className={`cs-tab-pane ${activeTab === tab.id ? 'active' : ''}`}
                        style={{ display: activeTab === tab.id ? 'block' : 'none' }}
                    >
                        {tab.type === 'mermaid' ? (
                            <MermaidDiagram code={tab.content} />
                        ) : tab.type === 'quiz' ? (
                            <ActiveRecallQuiz content={tab.content} />
                        ) : (
                            <MarkdownRenderer content={tab.content} />
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CheatSheetRenderer;
