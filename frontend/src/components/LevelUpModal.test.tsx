import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import LevelUpModal from './LevelUpModal';

describe('LevelUpModal', () => {
    const mockOnClose = vi.fn();
    const defaultProps = {
        newLevel: 5,
        lore: 'You have ascended.',
        onClose: mockOnClose
    };

    it('renders with dialog role and accessible attributes', () => {
        render(<LevelUpModal {...defaultProps} />);

        const dialog = screen.getByRole('dialog');
        expect(dialog).toBeInTheDocument();
        expect(dialog).toHaveAttribute('aria-modal', 'true');
        expect(dialog).toHaveAttribute('aria-labelledby', 'levelup-title');

        const title = screen.getByText('LEVEL UP');
        expect(title).toHaveAttribute('id', 'levelup-title');
    });

    it('focuses the dialog container on mount', () => {
        render(<LevelUpModal {...defaultProps} />);
        const dialog = screen.getByRole('dialog');
        expect(document.activeElement).toBe(dialog);
    });

    it('calls onClose when Escape key is pressed', () => {
        render(<LevelUpModal {...defaultProps} />);

        fireEvent.keyDown(window, { key: 'Escape', code: 'Escape' });

        expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
});
