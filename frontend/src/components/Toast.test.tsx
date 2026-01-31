import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import Toast from './Toast';

describe('Toast Component', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('renders the message correctly', () => {
        render(<Toast message="Test Message" onClose={() => {}} />);
        expect(screen.getByText('Test Message')).toBeInTheDocument();
    });

    it('calls onClose after duration', () => {
        const onClose = vi.fn();
        render(<Toast message="Test Message" duration={3000} onClose={onClose} />);

        // Fast-forward time
        act(() => {
            vi.advanceTimersByTime(3000);
        });

        // The component has a delay for exit animation (300ms)
        act(() => {
            vi.advanceTimersByTime(300);
        });

        expect(onClose).toHaveBeenCalled();
    });

    it('pauses timer on hover', () => {
        const onClose = vi.fn();
        render(<Toast message="Test Message" duration={3000} onClose={onClose} />);

        // Hover over the toast
        const toast = screen.getByRole('status'); // default role is status for info
        fireEvent.mouseEnter(toast);

        // Fast-forward past the duration
        act(() => {
            vi.advanceTimersByTime(3500);
        });

        expect(onClose).not.toHaveBeenCalled();

        // Un-hover
        fireEvent.mouseLeave(toast);

        // Fast-forward again
        act(() => {
            vi.advanceTimersByTime(3000);
        });

        act(() => {
             vi.advanceTimersByTime(300);
        });

        expect(onClose).toHaveBeenCalled();
    });

    it('pauses timer on focus', () => {
        const onClose = vi.fn();
        render(<Toast message="Test Message" duration={3000} onClose={onClose} />);

        // Focus the toast
        const toast = screen.getByRole('status');
        fireEvent.focus(toast);

        act(() => {
            vi.advanceTimersByTime(3500);
        });

        expect(onClose).not.toHaveBeenCalled();

        fireEvent.blur(toast);

        act(() => {
            vi.advanceTimersByTime(3300);
        });

        expect(onClose).toHaveBeenCalled();
    });
});
