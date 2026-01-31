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
    const [isPaused, setIsPaused] = useState(false);

    useEffect(() => {
        if (isPaused) {
            return;
        }

        const timer = setTimeout(() => {
            setIsExiting(true);
            setTimeout(onClose, 300); // Match exit animation duration
        }, duration);

        return () => clearTimeout(timer);
    }, [duration, onClose, isPaused]);

    const getIcon = () => {
        switch (type) {
            case 'success': return '✓';
            case 'error': return '✕';
            case 'warning': return '⚠';
            case 'info': return 'ℹ';
            default: return '';
        }
    };

    const isUrgent = type === 'error' || type === 'warning';

    return (
        <div
            className={`toast toast-${type} ${isExiting ? 'toast-exit' : 'toast-enter'}`}
            role={isUrgent ? 'alert' : 'status'}
            aria-live={isUrgent ? 'assertive' : 'polite'}
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
            onFocus={() => setIsPaused(true)}
            onBlur={() => setIsPaused(false)}
            style={{ '--toast-duration': `${duration}ms` } as React.CSSProperties}
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
                <span aria-hidden="true">×</span>
            </button>
        </div>
    );
};

// Toast Container Component
interface ToastContainerProps {
    toasts: Array<{ id: string; message: string; type: ToastType }>;
    removeToast: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, removeToast }) => {
    return (
        <div
            className="toast-container"
            role="region"
            aria-label="Notifications"
        >
            {toasts.map(toast => (
                <Toast
                    key={toast.id}
                    message={toast.message}
                    type={toast.type}
                    onClose={() => removeToast(toast.id)}
                />
            ))}
        </div>
    );
};

// Toast Hook
export const useToast = () => {
    const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: ToastType }>>([]);

    const addToast = (message: string, type: ToastType = 'info') => {
        const id = Math.random().toString(36).substr(2, 9);
        setToasts(prev => [...prev, { id, message, type }]);
    };

    const removeToast = (id: string) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    };

    return { toasts, addToast, removeToast };
};

export default Toast;
