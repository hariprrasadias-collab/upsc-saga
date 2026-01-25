import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import LevelUpModal from './LevelUpModal';
import { vi, describe, it, expect } from 'vitest';
import React from 'react';

describe('LevelUpModal', () => {
    const mockOnClose = vi.fn();
    const defaultProps = {
        newLevel: 5,
        lore: "You have ascended.",
        onClose: mockOnClose
    };

    it('should have correct accessibility roles', () => {
        render(<LevelUpModal {...defaultProps} />);
        const dialog = screen.getByRole('dialog');
        expect(dialog).toBeInTheDocument();
        expect(dialog).toHaveAttribute('aria-modal', 'true');
        expect(dialog).toHaveAttribute('aria-labelledby', 'levelup-title');
    });

    it('should show full lore text for screen readers', () => {
        render(<LevelUpModal {...defaultProps} />);
        // The full text should be present immediately via sr-only class
        // We use a regex or exact string match. Since one is hidden and one is typing,
        // we just need to ensure the full text exists in the DOM.
        expect(screen.getByText("You have ascended.")).toBeInTheDocument();
    });

    it('should close on Escape key', () => {
        render(<LevelUpModal {...defaultProps} />);
        fireEvent.keyDown(window, { key: 'Escape' });
        expect(mockOnClose).toHaveBeenCalled();
    });
});
