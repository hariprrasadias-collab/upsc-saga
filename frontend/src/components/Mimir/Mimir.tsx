// /frontend/src/components/Mimir/Mimir.tsx
import React, { useState, useEffect, useRef } from 'react';
import './Mimir.css';
import ReactMarkdown from 'react-markdown';

interface ChatMessage {
    id: number;
    sender: 'user' | 'mimir';
    message: string;
}

interface MimirChatProps {
    mode?: 'floating' | 'fullpage';
}

const MimirChat: React.FC<MimirChatProps> = ({ mode = 'fullpage' }) => {
    const [isOpen, setIsOpen] = useState(mode === 'fullpage');
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Scroll to bottom on new message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isOpen]);

    // Fetch History on Load
    useEffect(() => {
        if (isOpen) {
            fetch('http://localhost:5000/api/mimir/history')
                .then(res => {
                    if (!res.ok) throw new Error('Failed to fetch history');
                    return res.json();
                })
                .then((data: any[]) => {
                    // Map backend format (role, content) to frontend format (sender, message)
                    const mappedMessages: ChatMessage[] = data.map((msg, index) => ({
                        id: index, // Use index as ID for history
                        sender: msg.role === 'model' ? 'mimir' : 'user',
                        message: msg.content
                    }));
                    setMessages(mappedMessages);
                })
                .catch(err => console.error("Mimir sleeping:", err));
        }
    }, [isOpen]);

    const handleSend = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg = input;
        setInput('');
        setLoading(true);

        const tempId = Date.now();
        setMessages(prev => [...prev, { id: tempId, sender: 'user', message: userMsg }]);

        try {
            // FIX: Use correct endpoint /api/mimir/chat
            const res = await fetch('http://localhost:5000/api/mimir/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg })
            });

            if (!res.ok) throw new Error(`Server error: ${res.status}`);

            const data = await res.json();

            setMessages(prev => [
                ...prev,
                { id: tempId + 1, sender: 'mimir', message: data.response }
            ]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [
                ...prev,
                { id: tempId + 1, sender: 'mimir', message: "I cannot hear you, Brother. The connection is severed." }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = async () => {
        if (!confirm("Clear Mimir's memory?")) return;
        try {
            // FIX: Use POST method as defined in backend
            await fetch('http://localhost:5000/api/mimir/clear', { method: 'POST' });
            setMessages([]);
        } catch (error) {
            console.error("Clear error:", error);
        }
    };

    // Floating mode - return both the button and the overlay
    if (mode === 'floating') {
        return (
            <>
                {/* THE FLOATING HEAD IMAGE BUTTON */}
                <button className="mimir-head-btn" onClick={() => setIsOpen(!isOpen)} title="Consult Mimir">
                    <img
                        src="/Mimir.png"
                        alt="Mimir's Head"
                        className="mimir-head-img"
                    />
                </button>

                {/* THE CHAT WINDOW */}
                {isOpen && (
                    <div className="mimir-chat-window">
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
                            {messages.map((msg, index) => (
                                <div key={msg.id || index} className={`msg ${msg.sender}`}>
                                    <ReactMarkdown>{msg.message}</ReactMarkdown>
                                </div>
                            ))}
                            {loading && <div className="msg mimir">Thinking...</div>}
                            <div ref={messagesEndRef} />
                        </div>

                        <form className="mimir-input-area" onSubmit={handleSend}>
                            <input
                                type="text"
                                placeholder="Ask a doubt..."
                                value={input}
                                onChange={e => setInput(e.target.value)}
                            />
                            <button type="submit" className="mimir-send-btn" disabled={loading}>
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
        <div className="mimir-full-page-container" style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            flexDirection: 'column',
            background: '#0f172a',
            zIndex: 1
        }}>
            <header className="mimir-header">
                <div className="header-content">
                    <h1>Mimir</h1>
                    <p>Your AI Study Companion</p>
                </div>
                <div className="mimir-status">
                    <span className="status-dot"></span> Online
                </div>
            </header>

            <div className="chat-window" style={{
                flex: 1,
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                background: '#0f172a'
            }}>
                {messages.length === 0 && (
                    <div className="welcome-message">
                        <img
                            src="/Mimir.png"
                            alt="Mimir"
                            style={{ width: '80px', borderRadius: '50%', marginBottom: '1rem' }}
                        />
                        <h2>Greetings, Aspirant!</h2>
                        <p>I am Mimir, keeper of wisdom. How may I assist you in your journey today?</p>
                    </div>
                )}

                {messages.map((msg, index) => (
                    <div key={msg.id || index} className={`message-bubble ${msg.sender}`}>
                        <div className="avatar">
                            {msg.sender === 'user' ? '👤' : (
                                <img
                                    src="/Mimir.png"
                                    alt="Mimir"
                                    style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                                />
                            )}
                        </div>
                        <div className="message-content">
                            <ReactMarkdown>{msg.message}</ReactMarkdown>
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="message-bubble mimir">
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
                    onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                    placeholder="Ask Mimir anything..."
                    rows={1}
                />
                <button
                    className="send-btn"
                    onClick={() => handleSend()}
                    disabled={loading || !input.trim()}
                >
                    ➤
                </button>
            </div>
        </div>
    );
};

export default MimirChat;