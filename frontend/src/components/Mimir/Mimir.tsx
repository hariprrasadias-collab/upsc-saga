// /frontend/src/components/Mimir/Mimir.tsx
import React, { useState, useEffect, useRef } from 'react';
import './Mimir.css';
import ReactMarkdown from 'react-markdown';
import { useGlobal } from '../../contexts/GlobalContext';

interface ChatMessage {
    id: number;
    sender: 'user' | 'mimir';
    message: string;
}

interface MimirChatProps {
    mode?: 'floating' | 'fullpage' | 'modal';
}

// Typewriter Component for streaming text
const Typewriter: React.FC<{ text: string; onComplete?: () => void }> = ({ text, onComplete }) => {
    const [displayedText, setDisplayedText] = useState('');
    const indexRef = useRef(0);

    useEffect(() => {
        indexRef.current = 0;
        setDisplayedText('');
        
        const interval = setInterval(() => {
            setDisplayedText((prev) => {
                if (indexRef.current < text.length) {
                    const char = text.charAt(indexRef.current);
                    indexRef.current++;
                    return prev + char;
                } else {
                    clearInterval(interval);
                    if (onComplete) onComplete();
                    return prev;
                }
            });
        }, 15); // Speed of typing

        return () => clearInterval(interval);
    }, [text, onComplete]);

    return <ReactMarkdown>{displayedText}</ReactMarkdown>;
};

const MimirChat: React.FC<MimirChatProps> = ({ mode = 'fullpage' }) => {
    const { isMimirOpen, toggleMimir } = useGlobal();
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    
    // Audio Refs
    const clickSound = useRef(new Audio('/sounds/click.wav'));
    const successSound = useRef(new Audio('/sounds/success.wav'));

    // Use global state for floating/modal, local for fullpage (always open)
    const isOpen = mode === 'fullpage' ? true : isMimirOpen;
    // setIsOpen is not needed as we use toggleMimir directly

    // Play sound on open
    useEffect(() => {
        if (isOpen && mode === 'modal') {
            successSound.current.volume = 0.2;
            successSound.current.play().catch(e => console.log("Audio play failed", e));
        }
    }, [isOpen, mode]);

    // Scroll to bottom on new message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isOpen, loading]);

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

        // Play click sound
        clickSound.current.currentTime = 0;
        clickSound.current.play().catch(e => console.log("Audio play failed", e));

        const userMsg = input;
        setInput('');
        setLoading(true);

        const tempId = Date.now();
        setMessages(prev => [...prev, { id: tempId, sender: 'user', message: userMsg }]);

        try {
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
            await fetch('http://localhost:5000/api/mimir/clear', { method: 'POST' });
            setMessages([]);
        } catch (error) {
            console.error("Clear error:", error);
        }
    };

    // Floating / Modal mode
    if (mode === 'floating' || mode === 'modal') {
        return (
            <>
                {/* THE FLOATING HEAD IMAGE BUTTON */}
                <button className="mimir-head-btn" onClick={() => toggleMimir()} title="Consult Mimir">
                    <img
                        src="/Mimir.png"
                        alt="Mimir's Head"
                        className="mimir-head-img"
                    />
                </button>

                {/* THE CHAT WINDOW */}
                {isOpen && (
                    <>
                        {/* Backdrop for modal mode */}
                        {mode === 'modal' && (
                            <div 
                                className="mimir-modal-backdrop"
                                onClick={() => toggleMimir(false)}
                            />
                        )}
                        
                        <div className={`mimir-chat-window ${mode === 'modal' ? 'modal-center' : ''}`}>
                            <div className="mimir-window-header">
                                <h3>MIMIR'S WISDOM</h3>
                                <div className="header-actions">
                                    <button className="clear-chat-btn" onClick={handleClear}>Clear</button>
                                    <button className="close-btn" onClick={() => toggleMimir(false)}>✕</button>
                                </div>
                            </div>

                            <div className="mimir-messages">
                                {messages.length === 0 && (
                                    <div className="empty-state">
                                        <p>"Ask, Brother. I know all."</p>
                                    </div>
                                )}
                                {messages.map((msg, index) => (
                                    <div key={msg.id || index} className={`msg ${msg.sender}`}>
                                        {msg.sender === 'mimir' && index === messages.length - 1 && !loading ? (
                                            <Typewriter text={msg.message} />
                                        ) : (
                                            <ReactMarkdown>{msg.message}</ReactMarkdown>
                                        )}
                                    </div>
                                ))}
                                {loading && (
                                    <div className="msg mimir">
                                        <div className="rune-spinner"></div>
                                    </div>
                                )}
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
                    </>
                )}
            </>
        );
    }

    // Full-page mode - return the full interface
    return (
        <div className="mimir-full-page-container">
            <header className="mimir-header">
                <div className="header-content">
                    <h1>MIMIR</h1>
                    <p>The Smartest Man Alive</p>
                </div>
                <div className="mimir-status">
                    <span className="status-dot"></span> Online
                </div>
            </header>

            <div className="chat-window">
                {messages.length === 0 && (
                    <div className="welcome-message">
                        <div className="avatar-large">
                            <img
                                src="/Mimir.png"
                                alt="Mimir"
                            />
                        </div>
                        <h2>Greetings, Brother!</h2>
                        <p>I am Mimir, keeper of wisdom. Ask, and I shall enlighten you.</p>
                        <div className="suggestion-chips">
                            <button onClick={() => setInput("Explain the Doctrine of Basic Structure")} className="chip-btn">Basic Structure</button>
                            <button onClick={() => setInput("Summarize the revolt of 1857")} className="chip-btn">Revolt of 1857</button>
                            <button onClick={() => setInput("What are the key features of the Preamble?")} className="chip-btn">Preamble Features</button>
                        </div>
                    </div>
                )}

                {messages.map((msg, index) => (
                    <div key={msg.id || index} className={`msg ${msg.sender}`}>
                        {msg.sender === 'mimir' && index === messages.length - 1 && !loading ? (
                            <Typewriter text={msg.message} />
                        ) : (
                            <ReactMarkdown>{msg.message}</ReactMarkdown>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="msg mimir">
                        <div className="rune-spinner"></div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="mimir-input-area fullpage-input">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                            handleSend();
                        }
                    }}
                    placeholder="Ask Mimir anything..."
                />
                <button
                    className="mimir-send-btn"
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