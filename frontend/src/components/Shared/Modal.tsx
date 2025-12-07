import React, { useEffect, useRef } from 'react';
import './Modal.css';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    children: React.ReactNode;
    className?: string;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className = '' }) => {
    const modalRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div className="shared-modal-overlay" onClick={onClose}>
            <div
                className={`shared-modal-content ${className}`}
                onClick={e => e.stopPropagation()}
                ref={modalRef}
                role="dialog"
                aria-modal="true"
            >
                <div className="shared-modal-header">
                    {title && <h2 className="shared-modal-title">{title}</h2>}
                    <button className="shared-modal-close" onClick={onClose} aria-label="Close">
                        &times;
                    </button>
                </div>
                <div className="shared-modal-body">
                    {children}
                </div>
            </div>
        </div>
    );
};

export default Modal;
