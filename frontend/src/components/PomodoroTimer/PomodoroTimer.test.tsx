import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, type Mock } from 'vitest';
import PomodoroTimer from './PomodoroTimer';
import { usePomodoro } from '../../contexts/PomodoroContext';

// Mock the context hook
vi.mock('../../contexts/PomodoroContext', () => ({
  usePomodoro: vi.fn(),
}));

describe('PomodoroTimer', () => {
  const mockContext = {
    mode: 'work',
    timeLeft: 1500,
    isRunning: false,
    sessionsCompleted: 0,
    totalStudyTime: 0,
    currentTask: null,
    settings: {
      autoStartBreaks: false,
      autoStartPomodoros: false,
      autoStartDelay: 5,
      notifications: true,
      sound: true,
      activePresetId: 'classic'
    },
    presets: [
        { id: 'classic', name: 'Classic', icon: '🍅', workDuration: 25, shortBreakDuration: 5, longBreakDuration: 15, sessionsUntilLongBreak: 4 }
    ],
    activePreset: { id: 'classic', name: 'Classic', icon: '🍅', workDuration: 25, shortBreakDuration: 5, longBreakDuration: 15, sessionsUntilLongBreak: 4 },
    toggleTimer: vi.fn(),
    resetTimer: vi.fn(),
    switchMode: vi.fn(),
    setTimeLeft: vi.fn(),
    updateSettings: vi.fn(),
    setActivePreset: vi.fn(),
  };

  it('renders minimized state with accessible button', () => {
    (usePomodoro as Mock).mockReturnValue(mockContext);

    render(<PomodoroTimer />);

    const expandButton = screen.getByRole('button', { name: /expand pomodoro timer/i });
    expect(expandButton).toBeInTheDocument();
    expect(expandButton).toHaveAttribute('aria-expanded', 'false');
  });

  it('renders icon-only buttons with accessible names when expanded', () => {
    (usePomodoro as Mock).mockReturnValue(mockContext);
    render(<PomodoroTimer />);

    const expandButton = screen.getByRole('button', { name: /expand pomodoro timer/i });
    fireEvent.click(expandButton);

    // Now check for internal buttons
    expect(screen.getByRole('button', { name: /minimize/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /history/i })).toBeInTheDocument();
  });
});
