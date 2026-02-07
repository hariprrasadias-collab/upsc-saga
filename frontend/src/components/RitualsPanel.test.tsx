import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, Mock } from 'vitest';
import RitualsPanel from './RitualsPanel';
import { useGlobal } from '../contexts/GlobalContext';

// Mock the hook from the module
vi.mock('../contexts/GlobalContext', () => ({
  useGlobal: vi.fn(),
}));

// Mock child components
vi.mock('./StudyTimer', () => ({
  default: () => <div data-testid="study-timer">Timer Mock</div>,
}));

describe('RitualsPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default fetch mock (empty CSV)
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        text: () => Promise.resolve("Date,Day,Week,Time,Subject,Topic,Activity,Resources,Status\n"),
        headers: new Headers(),
        redirected: false,
        status: 200,
        statusText: 'OK',
        type: 'basic',
        url: '',
        clone: vi.fn(),
        body: null,
        bodyUsed: false,
        arrayBuffer: vi.fn(),
        blob: vi.fn(),
        formData: vi.fn(),
        json: vi.fn(),
      } as Response)
    );
  });

  it('renders correctly with tasks', async () => {
    // Setup mock return value
    (useGlobal as Mock).mockReturnValue({
      todayTasks: [
        { id: 1, title: 'Task 1', isCompleted: false, xp_reward: 10 },
        { id: 2, title: 'Task 2', isCompleted: true, xp_reward: 0 }
      ],
      completeTask: vi.fn(),
      setCurrentTab: vi.fn(),
    });

    render(<RitualsPanel />);

    expect(screen.getByText("TODAY'S RITUALS")).toBeInTheDocument();

    await waitFor(() => {
        expect(screen.getByText('Task 1')).toBeInTheDocument();
        expect(screen.getByText('Task 2')).toBeInTheDocument();
    });
  });

  it('displays correct aria-labels for tasks', async () => {
    (useGlobal as Mock).mockReturnValue({
      todayTasks: [
        { id: 1, title: 'Task 1', isCompleted: false, xp_reward: 10 },
        { id: 2, title: 'Task 2', isCompleted: true, xp_reward: 0 }
      ],
      completeTask: vi.fn(),
      setCurrentTab: vi.fn(),
    });

    render(<RitualsPanel />);

    await waitFor(() => {
        expect(screen.getByLabelText('Mark Task 1 as completed')).toBeInTheDocument();
        expect(screen.getByLabelText('Mark Task 2 as completed')).toBeInTheDocument();
    });
  });

  it('renders empty state message when no tasks', async () => {
    (useGlobal as Mock).mockReturnValue({
      todayTasks: [],
      completeTask: vi.fn(),
      setCurrentTab: vi.fn(),
    });

    render(<RitualsPanel />);

    await waitFor(() => {
        expect(screen.getByText('No rituals due today. Forge new ones on the War Map!')).toBeInTheDocument();
    });
  });
});
