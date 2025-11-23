// /frontend/src/components/Mimir/MimirChat.tsx
import React, { useState, useEffect, useRef } from 'react';
import './Mimir.css';

interface ChatMessage {
    id: number;
    sender: 'user' | 'mimir';
    message: string;
}

const MimirChat: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
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
                .then(res => res.json())
                .then(data => setMessages(data))
                .catch(() => console.error("Mimir sleeping"));
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
            const res = await fetch('http://localhost:5000/api/mimir/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg })
            });
            const data = await res.json();

            setMessages(prev => [
                ...prev,
                { id: tempId + 1, sender: 'mimir', message: data.response }
            ]);
        } catch {
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
        await fetch('http://localhost:5000/api/mimir/clear', { method: 'DELETE' });
        setMessages([]);
    };

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
                    <div className="mimir-header">
                        <h3>MIMIR'S WISDOM</h3>
                        <button className="clear-chat-btn" onClick={handleClear}>Clear</button>
                    </div>

                    <div className="mimir-messages">
                        {messages.length === 0 && (
                            <div style={{ textAlign: 'center', padding: '20px', opacity: 0.8 }}>
                                <p style={{ fontStyle: 'italic', color: '#5fb3e8' }}>"Ask, Brother. I know all."</p>
                            </div>
                        )}
                        {messages.map((msg) => (
                            <div key={msg.id} className={`msg ${msg.sender}`}>
                                {msg.message}
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
};

export default MimirChat;