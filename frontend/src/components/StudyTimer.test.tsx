import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import StudyTimer from './StudyTimer';
import React from 'react';

// Mock the hooks
vi.mock('../contexts/GlobalContext', () => ({
    useGlobal: () => ({
        refreshDashboard: vi.fn(),
    }),
}));

vi.mock('./Toast', () => ({
    useToast: () => ({
        toasts: [],
        addToast: vi.fn(),
        removeToast: vi.fn(),
    }),
    ToastContainer: () => <div data-testid="toast-container" />,
}));

// Mock config
vi.mock('../config', () => ({
    API_BASE_URL: 'http://localhost:test',
}));

describe('StudyTimer', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
        vi.clearAllMocks();
    });

    it('renders correctly with initial state', () => {
        render(<StudyTimer />);
        expect(screen.getByText('⏱️ Focus Timer')).toBeInTheDocument();
        expect(screen.getByText('00:00:00')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /start study timer/i })).toBeInTheDocument();

        // Check a11y attributes
        const timerDisplay = screen.getByTitle('Current session duration');
        expect(timerDisplay).toHaveAttribute('role', 'timer');
        expect(timerDisplay).toHaveAttribute('aria-live', 'off');
    });

    it('starts and pauses the timer', () => {
        render(<StudyTimer />);

        const startBtn = screen.getByRole('button', { name: /start study timer/i });
        fireEvent.click(startBtn);

        act(() => {
            vi.advanceTimersByTime(2000);
        });

        expect(screen.getByText('00:00:02')).toBeInTheDocument();

        const pauseBtn = screen.getByRole('button', { name: /pause study timer/i });
        fireEvent.click(pauseBtn);

        act(() => {
            vi.advanceTimersByTime(2000);
        });

        // Should not advance while paused
        expect(screen.getByText('00:00:02')).toBeInTheDocument();
    });

    it('shows loading state when saving', async () => {
        // Mock fetch
        global.fetch = vi.fn(() =>
            new Promise(resolve => {
                setTimeout(() => {
                    resolve({
                        ok: true,
                        json: () => Promise.resolve({ xp_earned: 10 }),
                    } as Response);
                }, 100);
            })
        );

        render(<StudyTimer />);

        // Start timer
        fireEvent.click(screen.getByRole('button', { name: /start study timer/i }));

        // Advance time to 61 seconds (min 1 minute)
        act(() => {
            vi.advanceTimersByTime(61000);
        });

        expect(screen.getByText('00:01:01')).toBeInTheDocument();

        // Click finish
        const finishBtn = screen.getByRole('button', { name: /finish study session/i });
        fireEvent.click(finishBtn);

        // Expect button to be disabled and show loading text
        // State update should be immediate after click in event handler (before await)
        expect(finishBtn).toBeDisabled();
        expect(finishBtn).toHaveTextContent('SAVING...');

        // Verify Resume button is also disabled
        const resumeBtn = screen.getByRole('button', { name: /resume/i });
        expect(resumeBtn).toBeDisabled();

        // Resolve the fetch
        await act(async () => {
            vi.runAllTimers();
        });

        expect(global.fetch).toHaveBeenCalled();

        // Should reset after save
        expect(screen.getByText('00:00:00')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /start study timer/i })).toBeInTheDocument();
    });

    it('does not reset timer on save error', async () => {
        // Mock fetch to fail
        global.fetch = vi.fn(() =>
            Promise.resolve({
                ok: false,
                json: () => Promise.resolve({}),
            } as Response)
        );

        render(<StudyTimer />);

        // Start and advance
        fireEvent.click(screen.getByRole('button', { name: /start study timer/i }));
        act(() => { vi.advanceTimersByTime(61000); });

        // Click finish
        const finishBtn = screen.getByRole('button', { name: /finish study session/i });
        fireEvent.click(finishBtn);

        // Wait for fetch
        await act(async () => { vi.runAllTimers(); });

        // Should still be active (Resume/Finish visible) and not reset
        expect(screen.getByRole('button', { name: /finish study session/i })).toBeInTheDocument();
        expect(screen.getByText('00:01:01')).toBeInTheDocument();
    });
});
