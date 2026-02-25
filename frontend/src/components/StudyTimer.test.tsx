import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import StudyTimer from './StudyTimer';

// Mock dependencies
vi.mock('../contexts/GlobalContext', () => ({
    useGlobal: () => ({ refreshDashboard: vi.fn() })
}));

vi.mock('../config', () => ({
    API_BASE_URL: 'http://localhost:5000'
}));

vi.mock('./Toast', () => ({
    ToastContainer: () => <div data-testid="toast-container" />,
    useToast: () => ({
        toasts: [],
        addToast: vi.fn(),
        removeToast: vi.fn()
    })
}));

describe('StudyTimer', () => {
    it('renders correctly with initial state', () => {
        render(<StudyTimer />);

        expect(screen.getByText('⏱️ Focus Timer')).toBeInTheDocument();
        expect(screen.getByText('00:00:00')).toBeInTheDocument();

        const startButton = screen.getByRole('button', { name: /start/i });
        expect(startButton).toBeInTheDocument();
    });

    it('starts timer when START is clicked', () => {
        render(<StudyTimer />);

        const startButton = screen.getByRole('button', { name: /start/i });
        fireEvent.click(startButton);

        expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /finish/i })).toBeInTheDocument();
    });

    it('shows saving state when finishing a long session', async () => {
        vi.useFakeTimers();

        // Mock fetch to hang forever (or resolve later)
        global.fetch = vi.fn(() => new Promise(() => {}));

        render(<StudyTimer />);

        const startButton = screen.getByRole('button', { name: /start/i });
        fireEvent.click(startButton);

        // Fast-forward 61 seconds
        act(() => {
            vi.advanceTimersByTime(61000);
        });

        const finishButton = screen.getByRole('button', { name: /finish/i });
        fireEvent.click(finishButton);

        expect(screen.getByRole('button', { name: /saving/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /saving/i })).toBeDisabled();

        vi.useRealTimers();
        vi.restoreAllMocks();
    });
});
