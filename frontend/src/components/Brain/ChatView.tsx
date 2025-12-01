import React, { useRef, useEffect } from 'react';
import { FaBrain, FaPaperPlane, FaBolt } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import type { Message, Action } from './types';

interface ChatViewProps {
    messages: Message[];
    isThinking: boolean;
    inputValue: string;
    setInputValue: (val: string) => void;
    onSendMessage: () => void;
    onExecuteAction: (action: Action) => void;
}

const ChatView: React.FC<ChatViewProps> = ({
    messages,
    isThinking,
    inputValue,
    setInputValue,
    onSendMessage,
    onExecuteAction
}) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isThinking]);

    return (
        <div className="chat-view">
            <div className="messages-container">
                {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.sender}`}>
                        <div className="message-avatar">
                            {msg.sender === 'brain' ? <FaBrain /> : <div className="user-avatar">U</div>}
                        </div>
                        <div className="message-bubble">
                            <ReactMarkdown>{msg.text}</ReactMarkdown>
                            {msg.actions && msg.actions.length > 0 && (
                                <div className="message-actions">
                                    {msg.actions.map((action, idx) => (
                                        <button key={idx} className="action-btn" onClick={() => onExecuteAction(action)}>
                                            <FaBolt /> {action.label || action.type}
                                        </button>
                                    ))}
                                </div>
                            )}
                            <span className="timestamp">
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    </div>
                ))}
                {isThinking && (
                    <div className="message brain">
                        <div className="message-avatar"><FaBrain /></div>
                        <div className="message-bubble thinking">
                            <div className="dots"><span>.</span><span>.</span><span>.</span></div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <div className="brain-input-area">
                <div className="brain-input-wrapper">
                    <input
                        className="brain-input"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), onSendMessage())}
                        placeholder="Ask the Brain..."
                    />
                    <button className="brain-send-btn" onClick={onSendMessage} aria-label="Send Message">
                        <FaPaperPlane />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatView;
