import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import LevelUpModal from './LevelUpModal';

describe('LevelUpModal', () => {
  const onCloseMock = vi.fn();
  const defaultProps = {
    newLevel: 5,
    lore: 'You have gained wisdom.',
    onClose: onCloseMock,
  };

  beforeEach(() => {
    onCloseMock.mockClear();
  });

  it('renders correctly with level and lore', async () => {
    render(<LevelUpModal {...defaultProps} />);
    expect(screen.getByText('LEVEL UP')).toBeInTheDocument();
    expect(screen.getByText('YOU ARE NOW LEVEL 5')).toBeInTheDocument();
  });

  it('calls onClose when "CONTINUE THE JOURNEY" is clicked', () => {
    render(<LevelUpModal {...defaultProps} />);
    const button = screen.getByRole('button', { name: /continue the journey/i });
    fireEvent.click(button);
    expect(onCloseMock).toHaveBeenCalled();
  });

  // These tests are expected to fail before accessibility improvements
  it('has correct accessibility attributes', () => {
    render(<LevelUpModal {...defaultProps} />);
    const modal = screen.getByRole('dialog');
    expect(modal).toBeInTheDocument();
    expect(modal).toHaveAttribute('aria-modal', 'true');
    expect(modal).toHaveAttribute('aria-labelledby');
    expect(modal).toHaveAttribute('aria-describedby');
  });

  it('handles Escape key to close', () => {
    render(<LevelUpModal {...defaultProps} />);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onCloseMock).toHaveBeenCalled();
  });
});
