import React from 'react';
import './Renderers.css';

interface ChatInterfaceProps {
    content: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ content }) => {
    const parseChat = (text: string) => {
        return text.split('\n').map(line => {
            const parts = line.split(':');
            if (parts.length > 1) {
                return {
                    speaker: parts[0].trim(),
                    message: parts.slice(1).join(':').trim()
                };
            }
            // Ignore empty lines or malformed
            if (line.trim().length === 0) return null;
            return { speaker: 'System', message: line };
        }).filter(item => item !== null) as { speaker: string, message: string }[];
    };

    const messages = parseChat(content);
    const uniqueSpeakers = Array.from(new Set(messages.map(m => m.speaker)));

    // Assign avatars deterministically
    const avatars: Record<string, string> = {};
    const avatarPool = ['👨‍🏫', '👩‍🎓', '🤖', '🦊', '🦉'];
    uniqueSpeakers.forEach((s, i) => {
        avatars[s] = avatarPool[i % avatarPool.length];
    });

    return (
        <div className="chat-container">
            {messages.map((msg, idx) => {
                const isPrimary = msg.speaker === uniqueSpeakers[0];
                return (
                    <div key={idx} className={`chat-row ${isPrimary ? 'left' : 'right'}`}>
                        {isPrimary && <div className="avatar">{avatars[msg.speaker]}</div>}
                        <div className={`chat-bubble ${isPrimary ? 'speaker-1' : 'speaker-2'}`}>
                            <div className="speaker-label">{msg.speaker}</div>
                            {msg.message}
                        </div>
                        {!isPrimary && <div className="avatar">{avatars[msg.speaker]}</div>}
                    </div>
                );
            })}
        </div>
    );
};

export default ChatInterface;
