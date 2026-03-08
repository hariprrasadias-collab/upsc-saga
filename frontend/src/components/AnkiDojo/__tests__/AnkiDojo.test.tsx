import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import '@testing-library/jest-dom';
import AnkiDojo from '../AnkiDojo';

// Mock audioManager and ebisuScheduler
vi.mock('../../../util/AudioManager', () => ({
  audioManager: {
    play: vi.fn(),
  },
}));

vi.mock('../ebisuAlgorithm', () => ({
  ebisuScheduler: {
    importState: vi.fn(),
    exportState: vi.fn(() => 'mockState'),
    sortCardsByPriority: vi.fn((ids) => ids),
    updateAfterReview: vi.fn(),
    getCardStats: vi.fn(() => ({
      halfLife: 1,
      nextReviewHours: 1,
      recallProbability: 0.9,
      successRate: 0.9,
    })),
  },
}));

const mockFetch = vi.fn();
window.fetch = mockFetch;

describe('AnkiDojo Security', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    // Setup generic successful fetch responses
    mockFetch.mockImplementation((url) => {
      if (url.endsWith('/api/anki/queue')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [1] }),
        });
      }
      if (url.endsWith('/api/anki/card')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            success: true,
            data: {
              id: 1,
              question: '<b>Question Text</b><script>alert("XSS")</script>',
              answer: '<i>Answer Text</i><img src="x" onerror="alert(1)">',
              deckName: 'Default',
            },
          }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  it('sanitizes HTML content using DOMPurify', async () => {
    render(<AnkiDojo />);

    // Wait for card to load
    await waitFor(() => {
      expect(screen.getByText('Question Text')).toBeInTheDocument();
    });

    // Check that script tags are removed
    const cardContent = document.querySelector('.card-content');
    expect(cardContent?.innerHTML).not.toContain('<script>');
    expect(cardContent?.innerHTML).toBe('<b>Question Text</b>');

    // Flip card
    const flipCard = document.querySelector('.flip-card');
    if (flipCard) {
        fireEvent.click(flipCard);
    }

    // Check answer content
    await waitFor(() => {
      expect(screen.getByText('Answer Text')).toBeInTheDocument();
    });

    // Check that onerror attributes are removed
    const backCardContent = document.querySelectorAll('.card-content')[1];
    expect(backCardContent?.innerHTML).not.toContain('onerror');
    expect(backCardContent?.innerHTML).toBe('<i>Answer Text</i><img src="x">');
  });
});
