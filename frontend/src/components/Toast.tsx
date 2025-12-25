// Toast Notification Component
import React, { useEffect, useState } from 'react';
import './Toast.css';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastProps {
    message: string;
    type?: ToastType;
    duration?: number;
    onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({
    message,
    type = 'info',
    duration = 3000,
    onClose
}) => {
    const [isExiting, setIsExiting] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsExiting(true);
            setTimeout(onClose, 300); // Match exit animation duration
        }, duration);

        return () => clearTimeout(timer);
    }, [duration, onClose]);

    const getIcon = () => {
        switch (type) {
            case 'success': return '✓';
            case 'error': return '✕';
            case 'warning': return '⚠';
            case 'info': return 'ℹ';
            default: return '';
        }
    };

    const getRole = () => {
        if (type === 'error' || type === 'warning') return 'alert';
        return 'status';
    };

    return (
        <div
            className={`toast toast-${type} ${isExiting ? 'toast-exit' : 'toast-enter'}`}
            role={getRole()}
            aria-live={type === 'error' ? 'assertive' : 'polite'}
        >
            <div className="toast-icon" aria-hidden="true">{getIcon()}</div>
            <div className="toast-message">{message}</div>
            <button
                className="toast-close"
                onClick={() => {
                    setIsExiting(true);
                    setTimeout(onClose, 300);
                }}
                aria-label="Close notification"
            >
                ×
            </button>
        </div>
    );
};

export default Toast;
