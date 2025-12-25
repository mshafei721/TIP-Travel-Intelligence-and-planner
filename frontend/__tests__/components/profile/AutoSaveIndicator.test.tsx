import { render, screen, waitFor } from '@testing-library/react';
import { AutoSaveIndicator } from '@/components/profile/AutoSaveIndicator';

describe('AutoSaveIndicator', () => {
  it('should not render when saveState is idle', () => {
    const { container } = render(<AutoSaveIndicator saveState="idle" />);
    expect(container.firstChild).toBeNull();
  });

  it('should show saving state with spinner', async () => {
    render(<AutoSaveIndicator saveState="saving" />);

    await waitFor(() => {
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });

    const indicator = screen.getByTestId('auto-save-indicator');
    expect(indicator).toHaveClass('bg-blue-50');
  });

  it('should show saved state with check icon', async () => {
    render(<AutoSaveIndicator saveState="saved" />);

    await waitFor(() => {
      expect(screen.getByText('Saved')).toBeInTheDocument();
    });

    const indicator = screen.getByTestId('auto-save-indicator');
    expect(indicator).toHaveClass('bg-green-50');
  });

  it('should show error state with alert icon', async () => {
    render(<AutoSaveIndicator saveState="error" />);

    await waitFor(() => {
      expect(screen.getByText('Failed to save')).toBeInTheDocument();
    });

    const indicator = screen.getByTestId('auto-save-indicator');
    expect(indicator).toHaveClass('bg-red-50');
  });

  it('should show custom error message', async () => {
    render(<AutoSaveIndicator saveState="error" errorMessage="Network error occurred" />);

    await waitFor(() => {
      expect(screen.getByText('Network error occurred')).toBeInTheDocument();
    });
  });

  it('should auto-hide after saved state', async () => {
    render(<AutoSaveIndicator saveState="saved" savedDuration={500} />);

    // Should initially show
    await waitFor(() => {
      expect(screen.getByText('Saved')).toBeInTheDocument();
    });

    // Wait for auto-hide (500ms duration + 300ms fade out)
    await waitFor(
      () => {
        expect(screen.queryByText('Saved')).not.toBeInTheDocument();
      },
      { timeout: 1000 },
    );
  });

  it('should have proper ARIA attributes', async () => {
    render(<AutoSaveIndicator saveState="saving" />);

    await waitFor(() => {
      const indicator = screen.getByRole('status');
      expect(indicator).toHaveAttribute('aria-live', 'polite');
    });
  });

  it('should transition between states', async () => {
    const { rerender } = render(<AutoSaveIndicator saveState="idle" />);

    // Start saving
    rerender(<AutoSaveIndicator saveState="saving" />);
    await waitFor(() => {
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });

    // Complete save
    rerender(<AutoSaveIndicator saveState="saved" />);
    await waitFor(() => {
      expect(screen.getByText('Saved')).toBeInTheDocument();
    });
  });
});
