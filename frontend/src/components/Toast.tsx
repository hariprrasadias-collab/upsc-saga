// Toast Notification Component
import React, { useEffect, useState, useRef } from 'react';
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
    const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
    const startTimeRef = useRef<number>(0);
    const remainingRef = useRef<number>(duration);

    useEffect(() => {
        remainingRef.current = duration;
    }, [duration]);

    useEffect(() => {
        if (isPaused || isExiting) return;

        startTimeRef.current = Date.now();
        timerRef.current = setTimeout(() => {
            setIsExiting(true);
            setTimeout(onClose, 300); // Match exit animation duration
        }, remainingRef.current);

        return () => {
            if (timerRef.current) clearTimeout(timerRef.current);
            const elapsed = Date.now() - startTimeRef.current;
            remainingRef.current = Math.max(0, remainingRef.current - elapsed);
        };
    }, [isPaused, isExiting, onClose]);

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

    const style = {
        '--toast-duration': `${duration}ms`
    } as React.CSSProperties;

    return (
        <div
            className={`toast toast-${type} ${isExiting ? 'toast-exit' : 'toast-enter'}`}
            role={isUrgent ? 'alert' : 'status'}
            aria-live={isUrgent ? 'assertive' : 'polite'}
            style={style}
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
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
