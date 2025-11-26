import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './Mimir.css';

interface Message {
    role: 'user' | 'model';
    content: string;
}

interface MimirChatProps {
    mode?: 'floating' | 'fullpage';
}

const MimirChat: React.FC<MimirChatProps> = ({ mode = 'fullpage' }) => {
    const [isOpen, setIsOpen] = useState(mode === 'fullpage');
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (isOpen) {
            fetchHistory();
        }
    }, [isOpen]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const fetchHistory = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/mimir/history');
            if (!response.ok) {
                console.error('Failed to fetch history:', response.status);
                setMessages([]);
                return;
            }
            const data = await response.json();
            if (Array.isArray(data)) {
                setMessages(data);
            } else {
                console.error('History data is not an array:', data);
                setMessages([]);
            }
        } catch (error) {
            console.error('Error fetching history:', error);
            setMessages([]);
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { role: 'user' as const, content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:5000/api/mimir/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage.content })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            const aiMessage = { role: 'model' as const, content: data.response };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [...prev, {
                role: 'model',
                content: 'I cannot hear you, Brother. The connection is severed. Please check if the backend server is running.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleClear = async () => {
        if (!confirm("Clear Mimir's memory?")) return;
        try {
            await fetch('http://localhost:5000/api/mimir/clear', { method: 'POST' });
            setMessages([]);
        } catch (error) {
            console.error('Error clearing history:', error);
        }
    };

    // Floating mode - return both the button and the overlay
    if (mode === 'floating') {
        return (
            <>
                {/* Floating Mimir Head Button */}
                <button
                    className="mimir-head-btn"
                    onClick={() => setIsOpen(!isOpen)}
                    title="Consult Mimir"
                >
                    <img
                        src="/Mimir.png"
                        alt="Mimir's Head"
                        className="mimir-head-img"
                    />
                </button>

                {/* Chat Window Overlay */}
                {isOpen && (
                    <div className="mimir-chat-window" onClick={(e) => e.stopPropagation()}>
                        <div className="mimir-window-header">
                            <h3>MIMIR'S WISDOM</h3>
                            <div className="header-actions">
                                <button className="clear-chat-btn" onClick={handleClear}>Clear</button>
                                <button className="close-btn" onClick={() => setIsOpen(false)}>✕</button>
                            </div>
                        </div>

                        <div className="mimir-messages">
                            {messages.length === 0 && (
                                <div style={{ textAlign: 'center', padding: '20px', opacity: 0.8 }}>
                                    <p style={{ fontStyle: 'italic', color: '#5fb3e8' }}>"Ask, Brother. I know all."</p>
                                </div>
                            )}
                            {messages.map((msg, idx) => (
                                <div key={idx} className={`msg ${msg.role}`}>
                                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                                </div>
                            ))}
                            {isLoading && <div className="msg model">Thinking...</div>}
                            <div ref={messagesEndRef} />
                        </div>

                        <form className="mimir-input-area" onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
                            <input
                                type="text"
                                placeholder="Ask a doubt..."
                                value={input}
                                onChange={e => setInput(e.target.value)}
                            />
                            <button type="submit" className="mimir-send-btn" disabled={isLoading}>
                                ➤
                            </button>
                        </form>
                    </div>
                )}
            </>
        );
    }

    // Full-page mode - return the full interface
    return (
        <div className="mimir-container">
            <header className="mimir-header">
                <div className="header-content">
                    <h1>Mimir</h1>
                    <p>Your AI Study Companion</p>
                </div>
                <div className="mimir-status">
                    <span className="status-dot"></span> Online
                </div>
            </header>

            <div className="chat-window">
                {messages.length === 0 && (
                    <div className="welcome-message">
                        <img
                            src="/Mimir.png"
                            alt="Mimir"
                            style={{ width: '80px', borderRadius: '50%', marginBottom: '1rem' }}
                        />
                        <h2>Greetings, Aspirant!</h2>
                        <p>I am Mimir, keeper of wisdom. How may I assist you in your journey today?</p>
                        <div className="suggestion-chips">
                            <button onClick={() => setInput("Explain the Preamble")}>
                                Explain the Preamble
                            </button>
                            <button onClick={() => setInput("Summarize the Revolt of 1857")}>
                                Summarize Revolt of 1857
                            </button>
                            <button onClick={() => setInput("Give me a motivation quote")}>
                                I need motivation
                            </button>
                        </div>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <div key={idx} className={`message-bubble ${msg.role}`}>
                        <div className="avatar">
                            {msg.role === 'user' ? (
                                '👤'
                            ) : (
                                <img
                                    src="/Mimir.png"
                                    alt="Mimir"
                                    style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                                />
                            )}
                        </div>
                        <div className="message-content">
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="message-bubble model">
                        <div className="avatar">
                            <img
                                src="/Mimir.png"
                                alt="Mimir"
                                style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                            />
                        </div>
                        <div className="message-content typing">
                            <span>.</span><span>.</span><span>.</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask Mimir anything..."
                    rows={1}
                />
                <button
                    className="send-btn"
                    onClick={handleSend}
                    disabled={isLoading || !input.trim()}
                >
                    ➤
                </button>
            </div>
        </div>
    );
};

export default MimirChat;
