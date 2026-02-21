import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AnkiDojo from './AnkiDojo';

// Mock AudioManager
vi.mock('../../util/AudioManager', () => ({
    audioManager: {
        play: vi.fn(),
    },
}));

// Mock Ebisu Scheduler
vi.mock('./ebisuAlgorithm', () => ({
    ebisuScheduler: {
        importState: vi.fn(),
        exportState: vi.fn(),
        sortCardsByPriority: vi.fn((ids) => ids),
        updateAfterReview: vi.fn(),
        getCardStats: vi.fn(() => ({
            halfLife: 24,
            nextReviewHours: 24,
            recallProbability: 0.5,
            successRate: 0.8,
        })),
    },
}));

// Mock global.fetch
global.fetch = vi.fn();

describe('AnkiDojo Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Mock queue response
        (global.fetch as any).mockImplementation((url: string) => {
            if (url.includes('/queue')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([1, 2]),
                });
            }
            if (url.includes('/card')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        id: 1,
                        question: 'What is the capital of France?',
                        answer: 'Paris',
                        deckName: 'Geography'
                    }),
                });
            }
            if (url.includes('/answer')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ success: true }),
                });
            }
            return Promise.reject(new Error('Unknown URL'));
        });
    });

    it('renders and loads a card', async () => {
        render(<AnkiDojo />);
        await waitFor(() => {
            expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
        });
    });

    it('flips card on Space key', async () => {
        render(<AnkiDojo />);
        await waitFor(() => {
            expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
        });

        const card = screen.getByText('What is the capital of France?').closest('.flip-card');
        expect(card).not.toHaveClass('flipped');

        fireEvent.keyDown(window, { key: ' ' });

        await waitFor(() => {
            expect(card).toHaveClass('flipped');
        });
    });

    it('flips card on Enter key', async () => {
        render(<AnkiDojo />);
        await waitFor(() => {
            expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
        });

        const card = screen.getByText('What is the capital of France?').closest('.flip-card');
        expect(card).not.toHaveClass('flipped');

        fireEvent.keyDown(window, { key: 'Enter' });

        await waitFor(() => {
            expect(card).toHaveClass('flipped');
        });
    });

    it('handles answer shortcuts (1=Wrong) correctly', async () => {
        render(<AnkiDojo />);
        await waitFor(() => {
            expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
        });

        // Flip the card first
        fireEvent.keyDown(window, { key: ' ' });

        const card = screen.getByText('What is the capital of France?').closest('.flip-card');
        await waitFor(() => {
            expect(card).toHaveClass('flipped');
        });

        // Press '1' for Wrong
        fireEvent.keyDown(window, { key: '1' });

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/answer'),
                expect.objectContaining({
                    method: 'POST',
                    body: JSON.stringify({ card_id: 1, ease: 1 })
                })
            );
        });
    });

    it('does not answer if card is not flipped', async () => {
        render(<AnkiDojo />);
        await waitFor(() => {
            expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
        });

        const card = screen.getByText('What is the capital of France?').closest('.flip-card');
        expect(card).not.toHaveClass('flipped');

        // Press '1' before flipping
        fireEvent.keyDown(window, { key: '1' });

        // Should NOT have called answer API
        expect(global.fetch).not.toHaveBeenCalledWith(
            expect.stringContaining('/answer'),
            expect.anything()
        );
    });

    it('does not flip card on Space if a button is focused', async () => {
        render(<AnkiDojo />);
        await waitFor(() => {
            expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
        });

        const card = screen.getByText('What is the capital of France?').closest('.flip-card');
        expect(card).not.toHaveClass('flipped');

        // Create a dummy button to focus
        const button = document.createElement('button');
        button.textContent = 'Test Button';
        document.body.appendChild(button);
        button.focus();

        // Simulate Space keydown on the button
        // Note: We need to ensure the event bubbles up to window where the listener is
        fireEvent.keyDown(button, { key: ' ', bubbles: true });

        // Wait a bit to ensure no flip happens
        await new Promise(r => setTimeout(r, 100));

        expect(card).not.toHaveClass('flipped');

        document.body.removeChild(button);
    });
});
