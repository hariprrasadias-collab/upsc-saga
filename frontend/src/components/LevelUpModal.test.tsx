import { render, screen, fireEvent } from '@testing-library/react';
import LevelUpModal from './LevelUpModal';
import { vi, describe, it, expect } from 'vitest';
import React from 'react';

describe('LevelUpModal', () => {
    const defaultProps = {
        newLevel: 5,
        lore: "You have ascended.",
        onClose: vi.fn(),
    };

    it('renders with correct accessibility roles', () => {
        render(<LevelUpModal {...defaultProps} />);

        // Should have dialog role
        const dialog = screen.getByRole('dialog');
        expect(dialog).toBeInTheDocument();
        expect(dialog).toHaveAttribute('aria-modal', 'true');
        // We expect the title to be the label
        expect(dialog).toHaveAttribute('aria-labelledby', 'levelup-heading');
    });

    it('closes on Escape key', () => {
        render(<LevelUpModal {...defaultProps} />);

        fireEvent.keyDown(window, { key: 'Escape' });
        expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('focuses the continue button on mount', () => {
        render(<LevelUpModal {...defaultProps} />);

        const button = screen.getByRole('button', { name: /continue/i });
        expect(document.activeElement).toBe(button);
    });
});
