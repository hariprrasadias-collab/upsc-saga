import React, { useState, useEffect, useRef } from 'react';
import { SocraticEngine, type DebateTurn, type DebateAgent } from '../../util/SocraticEngine';
import './StudyPlanDashboard.css'; // Reuse existing styles for now
import { brainService } from '../../services/BrainService';

interface SocraticArenaProps {
    engine: SocraticEngine;
    topic: string;
    onClose: () => void;
}

const SocraticArena: React.FC<SocraticArenaProps> = ({ engine, topic, onClose }) => {
    const [history, setHistory] = useState<DebateTurn[]>([]);
    const [userInput, setUserInput] = useState("");
    const [agents, setAgents] = useState<DebateAgent[]>([]);
    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        setAgents(engine.getAgents());
        // Start the debate if history is empty
        if (engine.getHistory().length === 0) {
            engine.startDebate(topic);
        }
        setHistory([...engine.getHistory()]);
    }, [engine, topic]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [history]);

    const [isThinking, setIsThinking] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const handleSend = async () => {
        if (!userInput.trim() && !isThinking) return;

        // 1. Add User Turn Optimistically (Optional, but Engine handles it)
        const userTurn: DebateTurn = {
            speakerId: 'user',
            text: userInput,
            type: 'ARGUMENT',
            timestamp: Date.now()
        };

        // Update local history immediately for responsiveness
        if (userInput) {
            setHistory(prev => [...prev, userTurn]);
        }

        const currentInput = userInput;
        setUserInput("");
        setIsThinking(true);

        // 2. Get AI Response
        try {
            const aiTurn = await engine.fetchNextTurn(currentInput);
            setHistory(prev => [...prev, aiTurn]);
        } catch (error) {
            console.error("Arena Error:", error);
        } finally {
            setIsThinking(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleAnalyzeDebate = async () => {
        setIsAnalyzing(true);
        try {
            const result = await brainService.executeAction('ANALYZE_DEBATE', { history });
            if (result.success) {
                // Add analysis as a special system message
                const analysisTurn: DebateTurn = {
                    speakerId: 'system',
                    text: `🏛️ **THE BRAIN'S VERDICT:**\n\n${result.analysis}`,
                    type: 'REBUTTAL',
                    timestamp: Date.now()
                };
                setHistory(prev => [...prev, analysisTurn]);
            } else {
                alert("Analysis failed: " + result.message);
            }
        } catch (err) {
            console.error("Analysis error:", err);
            alert("The Brain is silent.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="socratic-arena-overlay">
            <div className="socratic-arena-modal">
                <div className="arena-header">
                    <h2>🏛️ The Socratic Arena</h2>
                    <span className="topic-badge">{topic}</span>
                    <button
                        className="analyze-btn"
                        onClick={handleAnalyzeDebate}
                        disabled={isAnalyzing}
                        style={{ marginLeft: 'auto', marginRight: '10px', background: '#e67e22', border: 'none', padding: '5px 10px', color: 'white', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        {isAnalyzing ? 'Judging...' : '⚖️ Analyze Debate'}
                    </button>
                    <button aria-label="Close" className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="arena-chat-area">
                    {history.map((turn, index) => {
                        const isUser = turn.speakerId === 'user';
                        const agent = agents.find(a => a.id === turn.speakerId);

                        return (
                            <div key={index} className={`chat-message ${isUser ? 'user-message' : 'ai-message'}`}>
                                {!isUser && (
                                    <div className="agent-avatar" style={{ background: agent?.color }}>
                                        {agent?.avatar}
                                    </div>
                                )}
                                <div className="message-content">
                                    {!isUser && <div className="agent-name" style={{ color: agent?.color }}>{agent?.name}</div>}

                                    {/* Inner Thought Trace */}
                                    {turn.thoughts && (
                                        <div className="agent-thought">
                                            <span className="thought-icon">💭</span>
                                            <span className="thought-text">{turn.thoughts}</span>
                                        </div>
                                    )}

                                    <div className="message-text">{turn.text}</div>

                                    {/* User Score Feedback */}
                                    {turn.score && turn.score.logic > 0 && (
                                        <div className="turn-score">
                                            <span title="Logic">🧠 {turn.score.logic}</span>
                                            <span title="Relevance">🎯 {turn.score.relevance}</span>
                                            <span title="Impact">🔥 {turn.score.impact}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                    <div ref={chatEndRef} />
                    {isThinking && (
                        <div className="chat-message ai-message">
                            <div className="message-content">
                                <span className="thinking-dots">The Council is deliberating...</span>
                            </div>
                        </div>
                    )}
                </div>

                <div className="arena-input-area">
                    <textarea
                        value={userInput}
                        onChange={(e) => setUserInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Defend your position..."
                    />
                    <button onClick={handleSend}>Speak</button>
                </div>
            </div>
        </div>
    );
};

export default SocraticArena;
