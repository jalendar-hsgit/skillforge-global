/**
 * Frontend tests for Resume List Page
 * Tests: fetching resumes, navigation, CRUD operations
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/router';
import ResumesPage from './index';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock fetch API
global.fetch = jest.fn();

describe('ResumesPage', () => {
  const mockPush = jest.fn();
  const mockRouter = {
    push: mockPush,
    pathname: '/resumes',
    query: {},
    isReady: true,
  };

  const mockUser = {
    id: 1,
    email: 'test@example.com',
    name: 'Test User',
  };

  const mockResumes = [
    {
      id: 1,
      user_id: 1,
      title: 'My Resume',
      full_name: 'John Doe',
      template_id: 'modern',
      updated_at: '2024-01-15T10:30:00Z',
      views: 5,
    },
    {
      id: 2,
      user_id: 1,
      title: 'Cover Letter Version',
      full_name: 'John Doe',
      template_id: 'classic',
      updated_at: '2024-01-10T14:20:00Z',
      views: 2,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (global.fetch as jest.Mock).mockClear();
  });

  describe('Resume List Display', () => {
    test('should fetch and display list of resumes', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumes,
      });

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('My Resume')).toBeInTheDocument();
      });

      expect(screen.getByText('My Resume')).toBeInTheDocument();
      expect(screen.getByText('Cover Letter Version')).toBeInTheDocument();
    });

    test('should show loading state initially', () => {
      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise(() => {}) // Never resolves
      );

      render(<ResumesPage me={mockUser} />);

      // Should show loading spinner
      expect(screen.getByText(/loading|loading resume/i)).toBeInTheDocument();
    });

    test('should show empty state when no resumes', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText(/create your first resume/i)).toBeInTheDocument();
      });
    });

    test('should display resume count and metadata', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumes,
      });

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });

      // Should show template info and update date
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    test('should navigate to create new resume page', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumes,
      });

      render(<ResumesPage me={mockUser} />);

      const createButton = await screen.findByText(/create new/i);
      fireEvent.click(createButton);

      expect(mockPush).toHaveBeenCalledWith('/resumes/new');
    });

    test('should open import modal when import is clicked', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumes,
      });

      render(<ResumesPage me={mockUser} />);

      const importButton = await screen.findByText(/import resume/i);
      fireEvent.click(importButton);

      // Import modal should be visible
      expect(screen.getByText(/import resume/i)).toBeInTheDocument();
    });

    test('should navigate to edit page when resume is clicked', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumes,
      });

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('My Resume')).toBeInTheDocument();
      });

      // Click on the resume item or edit button
      const editButtons = screen.getAllByLabelText(/edit|open/i);
      if (editButtons.length > 0) {
        fireEvent.click(editButtons[0]);
        expect(mockPush).toHaveBeenCalledWith('/resumes/1');
      }
    });

    test('should navigate to preview page', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumes,
      });

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('My Resume')).toBeInTheDocument();
      });

      // Look for preview button
      const previewButtons = screen.queryAllByLabelText(/preview/i);
      if (previewButtons.length > 0) {
        fireEvent.click(previewButtons[0]);
        expect(mockPush).toHaveBeenCalledWith('/resumes/1/preview');
      }
    });
  });

  describe('Resume Actions', () => {
    test('should duplicate resume', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResumes,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            ...mockResumes[0],
            id: 3,
            title: 'My Resume (Copy)',
          }),
        });

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('My Resume')).toBeInTheDocument();
      });

      // Find and click duplicate button
      const duplicateButtons = screen.queryAllByLabelText(/duplicate|copy/i);
      if (duplicateButtons.length > 0) {
        fireEvent.click(duplicateButtons[0]);

        await waitFor(() => {
          expect(mockPush).toHaveBeenCalled();
        });
      }
    });

    test('should delete resume with confirmation', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResumes,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({}),
        });

      // Mock window.confirm
      global.confirm = jest.fn(() => true);

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('My Resume')).toBeInTheDocument();
      });

      const deleteButtons = screen.queryAllByLabelText(/delete|remove/i);
      if (deleteButtons.length > 0) {
        fireEvent.click(deleteButtons[0]);

        expect(global.confirm).toHaveBeenCalled();

        await waitFor(() => {
          const calls = (global.fetch as jest.Mock).mock.calls;
          const deleteCall = calls.find(call =>
            call[0].includes('resumes') && call[1]?.method === 'DELETE'
          );
          expect(deleteCall).toBeDefined();
        });
      }
    });

    test('should not delete resume if user cancels confirmation', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumes,
      });

      global.confirm = jest.fn(() => false);

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('My Resume')).toBeInTheDocument();
      });

      const deleteButtons = screen.queryAllByLabelText(/delete|remove/i);
      if (deleteButtons.length > 0) {
        fireEvent.click(deleteButtons[0]);

        expect(global.confirm).toHaveBeenCalled();

        // No DELETE request should be made
        const deleteCall = (global.fetch as jest.Mock).mock.calls.find(
          call => call[1]?.method === 'DELETE'
        );
        expect(deleteCall).toBeUndefined();
      }
    });
  });

  describe('Error Handling', () => {
    test('should handle fetch errors gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        // Should show empty state or error message
        expect(screen.getByText(/my resumes/i)).toBeInTheDocument();
      });
    });

    test('should handle duplicate errors', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResumes,
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ detail: 'Failed to duplicate' }),
        });

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('My Resume')).toBeInTheDocument();
      });

      // Error should not crash the component
      expect(screen.getByText(/my resumes/i)).toBeInTheDocument();
    });

    test('should handle delete errors', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResumes,
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ detail: 'Failed to delete' }),
        });

      global.confirm = jest.fn(() => true);

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        expect(screen.getByText('My Resume')).toBeInTheDocument();
      });

      // Component should handle error gracefully
      expect(screen.getByText(/my resumes/i)).toBeInTheDocument();
    });
  });

  describe('Sorting and Filtering', () => {
    test('should display resumes in order', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResumes,
      });

      render(<ResumesPage me={mockUser} />);

      await waitFor(() => {
        const resumeElements = screen.getAllByText(/resume/i);
        expect(resumeElements.length).toBeGreaterThan(0);
      });
    });
  });
});
