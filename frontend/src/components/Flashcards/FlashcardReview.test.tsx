import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import FlashcardReview from './FlashcardReview';

// Mock the context
const mockRefreshAnalytics = vi.fn();
vi.mock('../../contexts/AnalyticsContext', () => ({
  useAnalytics: () => ({
    refreshAnalytics: mockRefreshAnalytics
  })
}));

// Mock MarkdownRenderer to avoid complexity
vi.mock('../Shared/MarkdownRenderer', () => ({
  default: ({ content }: { content: string }) => <div>{content}</div>
}));

// Mock MapWorkCard
vi.mock('./MapWorkCard', () => ({
  default: () => <div>MapWorkCard Mock</div>
}));

describe('FlashcardReview Performance', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        global.fetch = vi.fn();
    });

    const mockCards = [
        { id: 1, front: 'Front 1', back: 'Back 1', card_type: 'basic' },
        { id: 2, front: 'Front 2', back: 'Back 2', card_type: 'basic' }
    ];

    it('optimistically updates UI when rating a card', async () => {
        // Mock initial fetch of cards
        (global.fetch as any).mockResolvedValueOnce({
            json: async () => mockCards
        });

        // Mock rating request with a delay
        let resolveRatingPromise: (value: any) => void;
        const ratingPromise = new Promise(resolve => {
            resolveRatingPromise = resolve;
        });

        (global.fetch as any).mockImplementation((url: string) => {
            if (url.includes('/review')) {
                return ratingPromise;
            }
            return Promise.resolve({ json: async () => ({}) });
        });

        render(<FlashcardReview deckId={1} onFinish={vi.fn()} />);

        // Wait for cards to load
        await waitFor(() => expect(screen.getByText('Front 1')).toBeInTheDocument());

        // Flip the card
        fireEvent.click(screen.getByText('Front 1'));
        expect(screen.getByText('Back 1')).toBeInTheDocument();

        // Click "Good" (rating 3)
        fireEvent.click(screen.getByText('Good'));

        // The card should IMMEDIATELY change to the next one (Front 2)
        // BEFORE the rating request completes
        // If the code awaits the fetch, this expectation will fail (timeout or not found)
        expect(screen.getByText('Front 2')).toBeInTheDocument();

        // Now resolve the promise to clean up
        if (resolveRatingPromise!) resolveRatingPromise({ json: async () => ({}) });
    });
});
