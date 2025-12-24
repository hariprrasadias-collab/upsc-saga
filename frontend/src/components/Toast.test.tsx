
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import * as matchers from '@testing-library/jest-dom/matchers';
import Toast from './Toast';

expect.extend(matchers);

describe('Toast Component', () => {
    afterEach(() => {
        cleanup();
    });

    it('renders with correct accessibility attributes for info type', () => {
        render(<Toast message="Test Info" onClose={() => {}} type="info" />);

        const toast = screen.getByRole('status');
        expect(toast).toBeInTheDocument();
        expect(toast).toHaveTextContent('Test Info');
        expect(toast).toHaveAttribute('aria-live', 'polite');
    });

    it('renders with correct accessibility attributes for error type', () => {
        render(<Toast message="Test Error" onClose={() => {}} type="error" />);

        const toast = screen.getByRole('alert');
        expect(toast).toBeInTheDocument();
        expect(toast).toHaveTextContent('Test Error');
        expect(toast).toHaveAttribute('aria-live', 'assertive');
    });

    it('close button has aria-label', () => {
        render(<Toast message="Test" onClose={() => {}} />);

        const closeButton = screen.getByLabelText('Close notification');
        expect(closeButton).toBeInTheDocument();
    });

    it('icon is hidden from screen readers', () => {
        const { container } = render(<Toast message="Test" onClose={() => {}} />);
        // Get the icon container - it's the first child of the toast
        const icon = container.querySelector('.toast-icon');
        expect(icon).toHaveAttribute('aria-hidden', 'true');
    });

    it('calls onClose when close button is clicked', async () => {
        const onCloseMock = vi.fn();
        render(<Toast message="Test" onClose={onCloseMock} />);

        const closeButton = screen.getByLabelText('Close notification');
        fireEvent.click(closeButton);

        // Wait for animation delay
        await waitFor(() => {
            expect(onCloseMock).toHaveBeenCalled();
        }, { timeout: 400 });
    });
});
