import React, { useState, useEffect, useRef } from 'react';
import { SocraticEngine, type DebateTurn, type DebateAgent } from '../../util/SocraticEngine';
import './StudyPlanDashboard.css'; // Reuse existing styles for now

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

    const handleSend = () => {
        if (!userInput.trim()) return;

        // 1. Add User Turn
        const userTurn: DebateTurn = {
            speakerId: 'user',
            text: userInput,
            type: 'ARGUMENT',
            timestamp: Date.now()
        };

        // Manually push to history for UI (Engine doesn't store user turns in its main history array in this simple version, 
        // but we should probably add it to the engine history too if we want full context. 
        // For now, let's just update local state and let engine generate response)

        const newHistory = [...history, userTurn];
        setHistory(newHistory);
        setUserInput("");

        // 2. Get AI Response
        setTimeout(() => {
            const aiTurn = engine.processUserResponse(userInput);
            setHistory(prev => [...prev, aiTurn]);
        }, 1000); // Simulate thinking delay
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="socratic-arena-overlay">
            <div className="socratic-arena-modal">
                <div className="arena-header">
                    <h2>🏛️ The Socratic Arena</h2>
                    <span className="topic-badge">{topic}</span>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>

                <div className="arena-chat-area">
                    {history.map((turn, index) => {
                        const isUser = turn.speakerId === 'user';
                        const agent = agents.find(a => a.id === turn.speakerId);

                        return (
                            <div key={index} className={`chat-message ${isUser ? 'user-message' : 'ai-message'}`}>
                                {!isUser && agent && (
                                    <div className="agent-avatar" style={{ backgroundColor: agent.color }}>
                                        {agent.avatar}
                                    </div>
                                )}
                                <div className="message-content">
                                    {!isUser && agent && <div className="agent-name">{agent.name}</div>}
                                    <div className="message-text">{turn.text}</div>
                                </div>
                            </div>
                        );
                    })}
                    <div ref={chatEndRef} />
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
