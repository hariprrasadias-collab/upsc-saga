import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, type Mock } from 'vitest';
import ChallengeCard from './ChallengeCard';
import React from 'react';

// Mock fetch
global.fetch = vi.fn();

// Mock window.location.reload
const mockReload = vi.fn();
Object.defineProperty(window, 'location', {
  configurable: true,
  value: { reload: mockReload },
});

describe('ChallengeCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders loading state initially', () => {
    (global.fetch as Mock).mockImplementation(() => new Promise(() => {})); // Never resolves
    render(<ChallengeCard />);
    expect(screen.getByText(/Loading today's challenge/i)).toBeInTheDocument();
  });

  test('renders challenge data', async () => {
    const mockChallenge = {
      id: 1,
      title: 'Test Challenge',
      description: 'Do something',
      type: 'test',
      target_value: 10,
      xp_reward: 50,
      completed: false,
      progress: 5,
    };
    const mockStreak = { current_streak: 3 };

    (global.fetch as Mock).mockImplementation((url: string) => {
        if (url.includes('/daily')) {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockChallenge),
            });
        }
        if (url.includes('/streak')) {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockStreak),
            });
        }
        return Promise.reject(new Error('Unknown URL'));
    });

    render(<ChallengeCard />);

    await waitFor(() => {
      expect(screen.getByText('Test Challenge')).toBeInTheDocument();
      expect(screen.getByText('Do something')).toBeInTheDocument();
      expect(screen.getByText('🔥 3 days')).toBeInTheDocument();
      expect(screen.getByText('5 / 10')).toBeInTheDocument();
    });
  });

  test('completes challenge and shows toast', async () => {
     const mockChallenge = {
      id: 1,
      title: 'Test Challenge',
      description: 'Do something',
      type: 'test',
      target_value: 10,
      xp_reward: 50,
      completed: false,
      progress: 5,
    };
     (global.fetch as Mock).mockImplementation((url: string) => {
        if (url.includes('/daily')) {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockChallenge),
            });
        }
        if (url.includes('/streak')) {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ current_streak: 3 }),
            });
        }
        if (url.includes('/complete')) {
             return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ xp_awarded: 50 }),
            });
        }
        return Promise.reject(new Error('Unknown URL'));
    });

    render(<ChallengeCard />);

    await waitFor(() => screen.getByText('Test Challenge'));

    const completeBtn = screen.getByText('Mark Complete');
    fireEvent.click(completeBtn);

    // Button should show loading state
    expect(screen.getByText('Completing...')).toBeInTheDocument();
    expect(completeBtn).toBeDisabled();

    // Toast should appear
    await waitFor(() => {
        expect(screen.getByText('Challenge completed! +50 XP')).toBeInTheDocument();
    });

    // Wait for reload (timeout > 1500ms)
    await waitFor(() => {
        expect(mockReload).toHaveBeenCalled();
    }, { timeout: 3000 });
  });
});
