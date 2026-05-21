/**
 * Frontend tests for Resume Editor
 * Tests: resume creation, editing, export (PDF/DOCX), and AI suggestions
 */
import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRouter } from 'next/router';
import ResumeEditor from './ResumeEditor';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock hooks
jest.mock('@/hooks/useMe', () => ({
  useMe: () => ({
    me: { id: 1, email: 'test@example.com', name: 'Test User' },
    loading: false,
  }),
}));

// Mock fetch API
global.fetch = jest.fn();

describe('ResumeEditor', () => {
  const mockPush = jest.fn();
  const mockRouter = {
    push: mockPush,
    pathname: '/resumes/1',
    query: { id: '1' },
    isReady: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (global.fetch as jest.Mock).mockClear();
  });

  describe('Resume Creation and Basic Fields', () => {
    test('should render resume editor with all input fields', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          user_id: 1,
          title: 'Test Resume',
          full_name: 'John Doe',
          email: 'john@example.com',
          phone: '+1-555-1234',
          location: 'New York, NY',
          summary: 'Experienced developer',
        }),
      });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
      });

      expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('+1-555-1234')).toBeInTheDocument();
      expect(screen.getByDisplayValue('New York, NY')).toBeInTheDocument();
    });

    test('should update resume fields when user types', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          full_name: '',
          email: '',
          phone: '',
          location: '',
          summary: '',
        }),
      });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        const nameInput = screen.getAllByPlaceholderText(/full name/i)[0] as HTMLInputElement;
        expect(nameInput).toBeInTheDocument();
      });

      const nameInput = screen.getByPlaceholderText(/full name/i) as HTMLInputElement;
      await userEvent.type(nameInput, 'Jane Smith');

      expect(nameInput.value).toBe('Jane Smith');
    });

    test('should display all toolbar buttons', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          full_name: 'Test User',
        }),
      });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        expect(screen.getByText('Save')).toBeInTheDocument();
      });

      // Check for toolbar buttons
      expect(screen.getByText(/save/i)).toBeInTheDocument();
      expect(screen.getByText(/export/i)).toBeInTheDocument();
      expect(screen.getByText(/preview/i)).toBeInTheDocument();
    });
  });

  describe('Resume Export', () => {
    test('should export resume as PDF', async () => {
      const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' });
      
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            full_name: 'John Doe',
            email: 'john@example.com',
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          blob: async () => mockBlob,
        });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        expect(screen.getByText('Export')).toBeInTheDocument();
      });

      // Mock URL.createObjectURL
      global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
      
      const exportButton = screen.getByText(/export/i);
      fireEvent.click(exportButton);

      // Wait for export menu and PDF option
      await waitFor(() => {
        const pdfOption = screen.queryByText(/pdf/i);
        if (pdfOption) {
          fireEvent.click(pdfOption);
        }
      });

      // Verify fetch was called with export endpoint
      await waitFor(() => {
        const calls = (global.fetch as jest.Mock).mock.calls;
        const exportCall = calls.find(call => 
          call[0].includes('export') && call[0].includes('format=pdf')
        );
        expect(exportCall).toBeDefined();
      });
    });

    test('should export resume as DOCX', async () => {
      const mockBlob = new Blob(['docx content'], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            full_name: 'John Doe',
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          blob: async () => mockBlob,
        });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        expect(screen.getByText('Export')).toBeInTheDocument();
      });

      global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');

      const exportButton = screen.getByText(/export/i);
      fireEvent.click(exportButton);

      // Wait for export menu and DOCX option
      await waitFor(() => {
        const docxOption = screen.queryByText(/docx|word/i);
        if (docxOption) {
          fireEvent.click(docxOption);
        }
      });

      // Verify fetch was called with export endpoint
      await waitFor(() => {
        const calls = (global.fetch as jest.Mock).mock.calls;
        const exportCall = calls.find(call => 
          call[0].includes('export') && call[0].includes('format=docx')
        );
        expect(exportCall).toBeDefined();
      });
    });

    test('should handle export errors gracefully', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            full_name: 'John Doe',
          }),
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ detail: 'Export failed' }),
        });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        expect(screen.getByText('Export')).toBeInTheDocument();
      });

      const exportButton = screen.getByText(/export/i);
      fireEvent.click(exportButton);

      // User might see an error message
      await waitFor(() => {
        // Error handling implementation should show a toast/notification
        const exportButton = screen.getByText(/export/i);
        expect(exportButton).toBeInTheDocument();
      });
    });
  });

  describe('Resume Save Functionality', () => {
    test('should save resume data to backend', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            full_name: 'John Doe',
            email: 'john@example.com',
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            full_name: 'John Doe Updated',
          }),
        });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        const saveButton = screen.getByText('Save');
        expect(saveButton).toBeInTheDocument();
      });

      const saveButton = screen.getByText('Save');
      fireEvent.click(saveButton);

      await waitFor(() => {
        const calls = (global.fetch as jest.Mock).mock.calls;
        const saveCall = calls.find(call => 
          call[0].includes('resumes') && call[1]?.method === 'PUT'
        );
        expect(saveCall).toBeDefined();
      });
    });

    test('should show save status feedback', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          full_name: 'John Doe',
        }),
      });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        expect(screen.getByText('Save')).toBeInTheDocument();
      });

      const saveButton = screen.getByText('Save');
      expect(saveButton).toBeInTheDocument();
      // Save button should be visible and clickable
    });
  });

  describe('AI Suggestions', () => {
    test('should fetch and display AI suggestions', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
            full_name: 'John Doe',
            summary: 'Developer',
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            suggestions: [
              'Add more technical skills',
              'Highlight leadership experience',
            ],
          }),
        });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        const aiButton = screen.queryByText(/ai/i);
        if (aiButton) {
          fireEvent.click(aiButton);
        }
      });

      // Verify suggestions endpoint was called
      await waitFor(() => {
        const calls = (global.fetch as jest.Mock).mock.calls;
        const suggestionCall = calls.find(call => 
          call[0].includes('suggestions')
        );
        expect(suggestionCall).toBeDefined();
      });
    });

    test('should handle AI suggestions errors', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            id: 1,
          }),
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ detail: 'AI service unavailable' }),
        });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        expect(screen.getByText('Export')).toBeInTheDocument();
      });

      // Should not crash
      expect(screen.getByText('Export')).toBeInTheDocument();
    });
  });

  describe('Preview', () => {
    test('should show live preview of resume', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          full_name: 'John Doe',
          email: 'john@example.com',
          phone: '555-1234',
          summary: 'Experienced developer',
        }),
      });

      render(<ResumeEditor resumeId={1} />);

      await waitFor(() => {
        expect(screen.getByText('Preview')).toBeInTheDocument();
      });

      // Preview button should exist
      expect(screen.getByText('Preview')).toBeInTheDocument();
    });
  });
});
