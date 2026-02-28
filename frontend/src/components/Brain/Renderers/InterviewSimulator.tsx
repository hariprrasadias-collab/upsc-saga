import { API_BASE_URL } from '../../../config';

import React, { useState, useRef, useEffect } from 'react';
import './InterviewSimulator.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface Message {
    sender: 'user' | 'board';
    text: string;
    timestamp: Date;
    mood?: 'neutral' | 'skeptical' | 'impressed' | 'aggressive';
}

interface InterviewSimulatorProps {
    content: string; // Initial prompt/context or previous session
    topic: string;
}

const InterviewSimulator: React.FC<InterviewSimulatorProps> = ({ content, topic }) => {
    // Determine if content is a stringified session or just a prompt
    const initialHistory: Message[] = [];
    try {
        const parsed = JSON.parse(content);
        if (Array.isArray(parsed)) {
            // It's a saved session
            parsed.forEach((msg: any) => initialHistory.push({
                ...msg,
                timestamp: new Date(msg.timestamp)
            }));
        }
    } catch (e) {
        // Not a saved session, start fresh
        initialHistory.push({
            sender: 'board',
            text: "Welcome to the interview. Please introduce yourself and tell us why you want to join the Civil Services.",
            timestamp: new Date(),
            mood: 'neutral'
        });
    }

    const [messages, setMessages] = useState<Message[]>(initialHistory);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            sender: 'user',
            text: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        try {
            // Call Backend for Board Response
            const response = await fetch(`${API_BASE_URL}/api/interview/respond`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: topic,
                    history: messages.concat(userMsg),
                    daf_profile: {} // Todo: Inject real DAF
                })
            });

            const data = await response.json();

            if (data.success) {
                const boardMsg: Message = {
                    sender: 'board',
                    text: data.reply,
                    timestamp: new Date(),
                    mood: data.mood || 'neutral'
                };
                setMessages(prev => [...prev, boardMsg]);
            } else {
                throw new Error("Board refused to answer.");
            }

        } catch (error) {
            console.error("Interview API Error", error);
            // Fallback for simulation
            setTimeout(() => {
                 setMessages(prev => [...prev, {
                    sender: 'board',
                    text: "I see. Let's move to the next question. (Simulation Mode: API Error)",
                    timestamp: new Date(),
                    mood: 'neutral'
                }]);
            }, 1000);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="interview-sim-container">
            <div className="interview-header">
                <h3>🏛️ UPSC Interview Board Simulator</h3>
                <div className="board-status">
                    <span className="status-dot online"></span> Board is In Session
                </div>
            </div>

            <div className="interview-chat-area custom-scrollbar">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message-row ${msg.sender}`}>
                        <div className="avatar">
                            {msg.sender === 'board' ? '👨‍⚖️' : '👤'}
                        </div>
                        <div className={`message-bubble ${msg.mood || ''}`}>
                            <div className="sender-name">
                                {msg.sender === 'board' ? 'Chairman' : 'Candidate'}
                            </div>
                            <MarkdownRenderer content={msg.text} />
                            <div className="timestamp">
                                {msg.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </div>
                        </div>
                    </div>
                ))}

                {isTyping && (
                    <div className="message-row board">
                        <div className="avatar">👨‍⚖️</div>
                        <div className="typing-indicator">
                            <span>.</span><span>.</span><span>.</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="interview-input-area">
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                    placeholder="Type your answer confidently..."
                    disabled={isTyping}
                />
                <button
                    className="send-btn"
                    onClick={handleSend}
                    disabled={!input.trim() || isTyping}
                >
                    Speak 🎤
                </button>
            </div>
        </div>
    );
};

export default InterviewSimulator;
