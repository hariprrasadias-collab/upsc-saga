import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import RitualsPanel from './RitualsPanel';
import React from 'react';

// Mock GlobalContext
const mockCompleteTask = vi.fn();
const mockSetCurrentTab = vi.fn();

vi.mock('../contexts/GlobalContext', () => ({
  useGlobal: () => ({
    todayTasks: [
      { id: 1, title: 'Backend Task 1', isCompleted: false, xp_reward: 10 }
    ],
    completeTask: mockCompleteTask,
    setCurrentTab: mockSetCurrentTab,
  }),
}));

// Mock StudyTimer
vi.mock('./StudyTimer', () => ({
  default: () => <div data-testid="study-timer-mock">Timer</div>
}));

// Mock fetch to return empty CSV to avoid errors
global.fetch = vi.fn(() => Promise.resolve({
    ok: true,
    text: () => Promise.resolve('Date,Day,Week,Time,Subject,Topic,Activity,Resources\n')
} as Response));

describe('RitualsPanel', () => {
  it('renders tasks with accessible checkboxes', () => {
    render(<RitualsPanel />);

    // Check Backend Task
    // This expects to fail before the fix because there is no aria-label
    // The visual text is in a sibling div, so getByLabelText should fail unless aria-label is present
    const backendCheckbox = screen.getByLabelText('Complete Backend Task 1');
    expect(backendCheckbox).toBeInTheDocument();
  });
});
