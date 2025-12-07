import React, { useState, useEffect, useRef } from 'react';
import './Renderers.css';
import './ChatInterface.css';
import MarkdownRenderer from '../../Shared/MarkdownRenderer';

interface ChatInterfaceProps {
    content: string;
    topic?: string;
}

interface Message {
    speaker: string;
    message: string;
    thoughts?: string;
    type?: string;
    score?: any;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ content, topic }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [userInput, setUserInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [expandedThoughts, setExpandedThoughts] = useState<number | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initial parsing of content
    useEffect(() => {
        const parsedMessages = content.split('\n').map(line => {
            const parts = line.split(':');
            if (parts.length > 1) {
                return {
                    speaker: parts[0].trim(),
                    message: parts.slice(1).join(':').trim()
                };
            }
            if (line.trim().length === 0) return null;
            return { speaker: 'System', message: line };
        }).filter(item => item !== null) as Message[];

        setMessages(parsedMessages);
    }, [content]);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async (autoReply = false) => {
        if (!topic) return;
        if (!autoReply && !userInput.trim()) return;

        setLoading(true);
        const inputToSend = autoReply ? null : userInput;

        // Optimistic update for user message
        if (inputToSend) {
            setMessages(prev => [...prev, { speaker: 'You', message: inputToSend }]);
            setUserInput('');
        }

        try {
            // Prepare history for API
            const history = messages.map(m => ({
                speakerId: mapSpeakerToId(m.speaker),
                text: m.message
            }));

            if (inputToSend) {
                history.push({ speakerId: 'user', text: inputToSend });
            }

            const response = await fetch('/api/socratic/debate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic,
                    history,
                    user_input: inputToSend
                })
            });

            const data = await response.json();

            if (data.speakerId) {
                const newMessage: Message = {
                    speaker: mapIdToSpeaker(data.speakerId),
                    message: data.text,
                    thoughts: data.thoughts,
                    type: data.type,
                    score: data.score
                };
                setMessages(prev => [...prev, newMessage]);
            } else if (data.error) {
                console.error("Debate error:", data.error);
            }
        } catch (error) {
            console.error("Failed to send message", error);
        } finally {
            setLoading(false);
        }
    };

    // Helper to map UI names to API IDs
    const mapSpeakerToId = (name: string) => {
        const lower = name.toLowerCase();
        if (lower.includes('socrates')) return 'skeptic';
        if (lower.includes('plato')) return 'idealist';
        if (lower.includes('aristotle')) return 'realist';
        return 'user';
    };

    const mapIdToSpeaker = (id: string) => {
        switch(id) {
            case 'skeptic': return 'Socrates';
            case 'idealist': return 'Plato';
            case 'realist': return 'Aristotle';
            default: return 'Unknown';
        }
    };

    // Avatars
    const getAvatar = (speaker: string) => {
        if (speaker === 'You') return '👤';
        if (speaker === 'Socrates') return '🦉'; // Wisdom/Skeptic
        if (speaker === 'Plato') return '🏛️'; // Idealist/Forms
        if (speaker === 'Aristotle') return '⚖️'; // Realist/Logic
        return '🤖';
    };

    return (
        <div className="chat-interface-container">
            <div className="chat-history custom-scrollbar">
                {messages.map((msg, idx) => {
                    const isUser = msg.speaker === 'You';
                    const hasThoughts = !!msg.thoughts;

                    return (
                        <div key={idx} className={`chat-message-row ${isUser ? 'user-row' : 'agent-row'}`}>
                            {!isUser && <div className="chat-avatar" title={msg.speaker}>{getAvatar(msg.speaker)}</div>}

                            <div className="chat-bubble-container">
                                <div className="speaker-name">{msg.speaker}</div>

                                {hasThoughts && (
                                    <div className="thought-bubble-toggle" onClick={() => setExpandedThoughts(expandedThoughts === idx ? null : idx)}>
                                        {expandedThoughts === idx ? '💭 Hide Thoughts' : '💭 Show Thoughts'}
                                    </div>
                                )}

                                {expandedThoughts === idx && msg.thoughts && (
                                    <div className="thought-content">
                                        <em>Thinking:</em> {msg.thoughts}
                                    </div>
                                )}

                                <div className={`chat-bubble ${isUser ? 'user-bubble' : 'agent-bubble'}`}>
                                    <MarkdownRenderer content={msg.message} />
                                </div>

                                {msg.score && Object.keys(msg.score).length > 0 && (
                                    <div className="score-badge">
                                        Logic: {msg.score.logic} | Impact: {msg.score.impact}
                                    </div>
                                )}
                            </div>

                            {isUser && <div className="chat-avatar">{getAvatar(msg.speaker)}</div>}
                        </div>
                    );
                })}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-controls glass-panel">
                {loading && <div className="typing-indicator">Philosophers are contemplating...</div>}

                <div className="input-group">
                    <input
                        type="text"
                        value={userInput}
                        onChange={(e) => setUserInput(e.target.value)}
                        placeholder={topic ? `Debate about ${topic}...` : "Enter your argument..."}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        disabled={loading}
                    />
                    <button className="send-btn" onClick={() => handleSend(false)} disabled={loading}>
                        Send Argument
                    </button>
                    <button className="auto-btn" onClick={() => handleSend(true)} disabled={loading}>
                        🤖 Auto-Debate
                    </button>
                </div>
                <div className="instructions-hint">
                    Use "Auto-Debate" to let the philosophers respond to each other.
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
