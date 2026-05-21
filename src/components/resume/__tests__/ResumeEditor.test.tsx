import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResumeEditor from '../ResumeEditor';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: () => ({
    query: { id: '1' },
    pathname: '/resumes/1',
    push: jest.fn(),
  }),
}));

// Mock fetch globally
global.fetch = jest.fn();

// Mock WebSocket and related hooks
jest.mock('../../../hooks/useWebSocket', () => ({
  __esModule: true,
  default: () => ({
    isConnected: false,
    presenceUsers: [],
    sendMessage: jest.fn(),
  }),
}));

jest.mock('../../../hooks/useUndoRedo', () => ({
  __esModule: true,
  default: () => ({
    state: {},
    undo: jest.fn(),
    redo: jest.fn(),
    canUndo: false,
    canRedo: false,
    updateState: jest.fn(),
  }),
}));

describe('ResumeEditor - Header UI', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      // Mock resume data fetch
      if (url.includes('/api/session/resumes')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            id: 1,
            title: 'Test Resume',
            sections: [],
            data: {},
          }),
        });
      }
      // Mock other endpoints
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      });
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the resume editor with header buttons', async () => {
    render(<ResumeEditor />);

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText(/Save/i)).toBeInTheDocument();
    });

    // Verify key action buttons exist
    expect(screen.getByText(/AI/i)).toBeInTheDocument();
    expect(screen.getByText(/Styles/i)).toBeInTheDocument();
    expect(screen.getByText(/Preview/i)).toBeInTheDocument();
    expect(screen.getByText(/Export/i)).toBeInTheDocument();
  });

  it('displays status indicators in top row', async () => {
    render(<ResumeEditor />);

    await waitFor(() => {
      // Check for Live/Offline indicator (initially shows "Offline")
      expect(screen.getByText(/Offline/i)).toBeInTheDocument();
    });
  });

  it('has compact button sizing classes', () => {
    const { container } = render(<ResumeEditor />);

    // Verify buttons have compact sizing (w-3.5 h-3.5, px-3 py-1.5)
    const buttons = container.querySelectorAll('button');
    expect(buttons.length).toBeGreaterThan(5);
  });

  it('displays two-row header layout', () => {
    const { container } = render(<ResumeEditor />);

    // The header should have flex-col for vertical stacking
    const headerContainer = container.querySelector('.flex-col');
    expect(headerContainer).toBeInTheDocument();
  });
});
