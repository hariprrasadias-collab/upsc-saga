import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import SyllabusTracker from './SyllabusTracker';

// Mock dependencies
vi.mock('../../services/BrainService', () => ({
  brainService: {
    think: vi.fn(),
    executeAction: vi.fn()
  }
}));

vi.mock('../Shared/MarkdownRenderer', () => ({
  default: ({ content }: { content: string }) => <div>{content}</div>
}));

const mockTopics = [
  {
    id: 1,
    paper: 'GS1',
    subject: 'History',
    topic: 'Ancient History',
    subtopic: null,
    status: 'Not Started',
    has_notes: 1, // Has notes
    last_updated: '2023-01-01'
  },
  {
    id: 2,
    paper: 'GS1',
    subject: 'History',
    topic: 'Modern History',
    subtopic: null,
    status: 'Not Started',
    has_notes: 0, // No notes
    last_updated: '2023-01-01'
  }
];

describe('SyllabusTracker', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockTopics
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('lazy loads notes when opening a topic with has_notes=1', async () => {
    render(<SyllabusTracker />);

    // Wait for Subject "History"
    await waitFor(() => expect(screen.getByText('History')).toBeInTheDocument());

    // Click History to expand
    fireEvent.click(screen.getByText('History'));

    // Wait for topics
    await waitFor(() => expect(screen.getByText('Ancient History')).toBeInTheDocument());

    // Setup mock for notes fetch
    (global.fetch as any).mockImplementation((url: string) => {
      if (url.includes('/notes') && url.includes('/1/')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ id: 1, notes: 'Secret Ancient Knowledge' })
        });
      }
      return Promise.resolve({
        ok: true,
        json: async () => mockTopics
      });
    });

    // Find the notes button for the first topic
    // TopicItem buttons have aria-labels or just title
    const notesBtns = screen.getAllByRole('button', { name: /Notes for/i });
    fireEvent.click(notesBtns[0]); // Click first one (Ancient History)

    // Check loading state
    expect(screen.getByDisplayValue('Loading notes...')).toBeInTheDocument();

    // Wait for notes to load
    await waitFor(() => expect(screen.getByDisplayValue('Secret Ancient Knowledge')).toBeInTheDocument());
  });

  it('does not fetch notes if has_notes=0', async () => {
    render(<SyllabusTracker />);

    // Wait for Subject "History"
    await waitFor(() => expect(screen.getByText('History')).toBeInTheDocument());

    // Click History to expand
    fireEvent.click(screen.getByText('History'));

    await waitFor(() => expect(screen.getByText('Modern History')).toBeInTheDocument());

    const fetchSpy = vi.spyOn(global, 'fetch');

    const notesBtns = screen.getAllByRole('button', { name: /Notes for/i });
    fireEvent.click(notesBtns[1]); // Click second one (Modern History)

    // Should open modal with empty notes immediately
    expect(screen.getByRole('textbox')).toHaveValue('');

    // fetch should NOT be called for notes
    expect(fetchSpy).not.toHaveBeenCalledWith(expect.stringContaining('/2/notes'), expect.anything());
  });
});
