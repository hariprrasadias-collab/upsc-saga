import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Sidebar from './Sidebar';
import { BrowserRouter } from 'react-router-dom';

// Mock the useGlobal hook
vi.mock('../contexts/GlobalContext', () => ({
  useGlobal: () => ({
    currentTab: 'dashboard',
    setCurrentTab: vi.fn(),
    isSidebarOpen: true,
    toggleSidebar: vi.fn(),
    toggleMimir: vi.fn(),
  }),
}));

describe('Sidebar', () => {
  it('renders correctly', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );
    expect(screen.getByText('UPSC SAGA')).toBeInTheDocument();
  });
});
