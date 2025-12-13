import React, { useState, useEffect, useRef } from 'react';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';
import mermaid from 'mermaid';
import { motion, AnimatePresence } from 'framer-motion';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import './Renderers.css';

// --- Types ---
interface CheatSheetTab {
    id: string;
    label: string;
    content: string;
    type?: 'markdown' | 'mermaid' | 'quiz';
}

interface CheatSheetData {
    title: string;
    tabs: CheatSheetTab[];
}

interface CheatSheetRendererProps {
    content: string;
}

// --- Sub-Components ---
const MermaidDiagram: React.FC<{ code: string }> = ({ code }) => {
    const ref = useRef<HTMLDivElement>(null);
    useEffect(() => {
        if (ref.current) {
            try {
                mermaid.initialize({ startOnLoad: true, theme: 'dark' });
                mermaid.run({ nodes: [ref.current] });
            } catch (e) { console.error("Mermaid Error:", e); }
        }
    }, [code]);
    return <div className="mermaid-container"><div ref={ref} className="mermaid">{code}</div></div>;
};

const ActiveRecallQuiz: React.FC<{ content: string }> = ({ content }) => {
    const [questions, setQuestions] = useState<{ q: string, a: string }[]>([]);
    const [revealed, setRevealed] = useState<number[]>([]);

    useEffect(() => {
        try {
            const parsed = JSON.parse(content);
            if (Array.isArray(parsed)) setQuestions(parsed);
        } catch (e) { }
    }, [content]);

    return (
        <div className="quiz-container">
            {questions.map((item, index) => (
                <motion.div
                    key={index}
                    className="quiz-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => setRevealed(prev => prev.includes(index) ? prev.filter(i => i !== index) : [...prev, index])}
                >
                    <div className="quiz-q">❓ {item.q}</div>
                    <AnimatePresence>
                        {revealed.includes(index) && (
                            <motion.div className="quiz-a" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}>
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

// --- Main Component ---
const CheatSheetRenderer: React.FC<CheatSheetRendererProps> = ({ content }) => {
    const [data, setData] = useState<CheatSheetData | null>(null);
    const [activeTab, setActiveTab] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // --- Smart Parsing & Auto-Labelling ---
    useEffect(() => {
        // Deep Content Analysis: Guesses the tab Type/Title from the raw text content
        const categorizeContent = (text: string, currentLabel: string): string => {
            const t = text.toLowerCase();
            const l = currentLabel.toLowerCase();

            // 1. If label is already good, just embellish it
            if (l.includes('fact')) return '⚡ Facts';
            if (l.includes('mnemonic')) return '🧠 Mnemonic';
            if (l.includes('law') || l.includes('judgment') || l.includes('article')) return '⚖️ Law';
            if (l.includes('time') || l.includes('chronology')) return '📅 Time';
            if (l.includes('examiner') || l.includes('trap')) return '🧐 Examiner';
            if (l.includes('map')) return '🗺️ Concept Map';
            if (l.includes('quiz') || l.includes('active recall')) return '❓ Active Recall';

            // 2. If label is generic ("Section", "Tab", "Overview"), analyze content
            if (l.includes('section') || l.includes('tab') || l.includes('overview')) {
                // Heuristics
                if (t.includes('mnemonics') || t.includes('memory trick')) return '🧠 Mnemonic';
                if (t.includes('article') && (t.includes('constitution') || t.includes('act'))) return '⚖️ Law';
                if (t.match(/\d{4}.*?event/i) || t.match(/\d{4}\s*-\s*\d{4}/)) return '📅 Time'; // Dates
                if (t.includes('examiner') || t.includes('prelims') || t.includes('upsc')) return '🧐 Examiner';
                if (t.includes('graph') || t.includes('TD') || t.includes('LR')) return '🗺️ Concept Map';
                if (t.includes('question') && t.includes('answer')) return '❓ Active Recall';
                if (t.includes('fact') || t.includes('point')) return '⚡ Facts';
            }

            return currentLabel; // Return original if no better guess
        };

        const parseContent = (raw: string): CheatSheetData => {
            let parsedData: any = null;

            // A. Try JSON Parse
            let jsonString = raw.trim();
            const jsonMatch = raw.match(/```json\n([\s\S]*?)\n```/) || raw.match(/\{[\s\S]*\}/);
            if (jsonMatch) jsonString = jsonMatch[1] || jsonMatch[0];

            try {
                parsedData = JSON.parse(jsonString);
            } catch (e) {
                // Failed JSON
            }

            // B. Construct Tabs
            let tabs: CheatSheetTab[] = [];

            if (parsedData && parsedData.tabs && Array.isArray(parsedData.tabs)) {
                // Scenario 1: JSON Data Available
                tabs = parsedData.tabs.map((t: any, idx: number) => {
                    const originalLabel = t.label || t.title || t.name || t.header || `Section ${idx + 1}`;
                    const content = t.content || t.body || t.text || "";

                    return {
                        id: t.id || `tab-${idx}`,
                        label: categorizeContent(content, originalLabel),
                        content: content,
                        type: t.type || 'markdown'
                    };
                });
            } else {
                // Scenario 2: Smart Splitting (Markdown)
                const lines = raw.split('\n');
                let currentTab: Partial<CheatSheetTab> | null = null;
                let currentContent: string[] = [];

                // Regex: Headers, Bolds with colons, or "Title:" lines
                const headerRegex = /^(#{1,3})\s+(.+)|^\*\*(.+?)\*\*[:]?|^\s*([A-Z][a-zA-Z\s]+):$/;

                lines.forEach((line) => {
                    const match = line.match(headerRegex);
                    // Filter out false positives (e.g. bold words in sentences)
                    // H1/H2 are always headers. Bold/Plain must be short (< 60 chars) to be headers.
                    const isHeader = match && line.length < 60;

                    if (isHeader) {
                        if (currentTab) {
                            const combinedContent = currentContent.join('\n');
                            tabs.push({
                                id: `tab-${tabs.length}`,
                                label: categorizeContent(combinedContent, currentTab.label || "Section"),
                                content: combinedContent,
                                type: 'markdown'
                            });
                        }
                        const extractedTitle = match[2] || match[3] || match[4];
                        currentTab = { label: extractedTitle.trim() };
                        currentContent = [];
                    } else {
                        currentContent.push(line);
                    }
                });

                // Push final tab
                if (currentTab) {
                    const combinedContent = currentContent.join('\n');
                    tabs.push({
                        id: `tab-${tabs.length}`,
                        label: categorizeContent(combinedContent, currentTab.label || "End Notes"),
                        content: combinedContent,
                        type: 'markdown'
                    });
                } else {
                    // Fallback: Single Overview
                    tabs.push({
                        id: 'overview',
                        label: categorizeContent(raw, 'Overview'),
                        content: raw,
                        type: 'markdown'
                    });
                }
            }

            // Ensure we never return 0 tabs
            if (tabs.length === 0) {
                tabs.push({ id: 'err', label: 'Overview', content: raw, type: 'markdown' });
            }

            return {
                title: parsedData?.title || "Cheat Sheet",
                tabs
            };
        };

        const result = parseContent(content);
        setData(result);
        if (result.tabs.length > 0) setActiveTab(result.tabs[0].id);

    }, [content]);

    // --- Handlers ---
    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            containerRef.current?.requestFullscreen();
            setIsFullscreen(true);
        } else {
            document.exitFullscreen();
            setIsFullscreen(false);
        }
    };

    const handleSpeak = () => {
        if (isSpeaking) { window.speechSynthesis.cancel(); setIsSpeaking(false); return; }
        if (!data) return;
        const currentContent = data.tabs.find(t => t.id === activeTab)?.content || "";
        const utterance = new SpeechSynthesisUtterance(currentContent.substring(0, 4000));
        utterance.onend = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utterance);
        setIsSpeaking(true);
    };

    const handleExportPDF = async () => {
        if (!containerRef.current || !data) return;
        const canvas = await html2canvas(containerRef.current, { backgroundColor: '#0d1117' });
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save('cheatsheet.pdf');
    };

    if (!data) return <div className="loading-pulse">Analyzing...</div>;

    return (
        <div className={`cheat-sheet-container ${isFullscreen ? 'fullscreen-mode' : ''}`} ref={containerRef}>
            <header className="cs-header">
                <h3 className="cs-title">
                    <span style={{ color: '#00fff2' }}>📑</span> {data.title}
                </h3>
                <div className="cs-controls">
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <input
                            type="text"
                            placeholder="Find..."
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                            className="search-wrapper"
                            style={{ width: '150px', padding: '5px 10px' }}
                        />
                        <button onClick={handleSpeak} className={`icon-btn ${isSpeaking ? 'active' : ''}`} title="Read Aloud">🔊</button>
                        <button onClick={handleExportPDF} className="icon-btn" title="Save PDF">💾</button>
                        <button onClick={toggleFullscreen} className="icon-btn" title="Fullscreen">⛶</button>
                    </div>
                </div>
            </header>

            <nav className="cs-tabs-nav">
                {data.tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`cs-tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
            </nav>

            <div className="cs-tab-content custom-scrollbar">
                <AnimatePresence mode='wait'>
                    {data.tabs.map(tab => (
                        activeTab === tab.id && (
                            <motion.div
                                key={tab.id}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                transition={{ duration: 0.2 }}
                                style={{ height: '100%' }}
                            >
                                {tab.type === 'mermaid' ? <MermaidDiagram code={tab.content} /> :
                                    tab.type === 'quiz' ? <ActiveRecallQuiz content={tab.content} /> :
                                        <MarkdownRenderer content={tab.content} />}
                            </motion.div>
                        )
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default CheatSheetRenderer;
