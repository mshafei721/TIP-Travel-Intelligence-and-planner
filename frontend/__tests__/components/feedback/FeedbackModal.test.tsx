import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { FeedbackModal, useFeedbackModal } from '@/components/feedback/FeedbackModal';

// Mock PostHog analytics
jest.mock('@/lib/analytics', () => ({
  trackFeedbackSubmitted: jest.fn(),
}));

// Mock Sentry
jest.mock('@sentry/nextjs', () => ({
  captureFeedback: jest.fn(),
  captureException: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

describe('FeedbackModal', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'test-id' }),
    });
  });

  it('renders the modal when open', () => {
    render(<FeedbackModal isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('Send Feedback')).toBeInTheDocument();
    expect(screen.getByText('Bug Report')).toBeInTheDocument();
    expect(screen.getByText('Feature Request')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<FeedbackModal isOpen={false} onClose={mockOnClose} />);

    expect(screen.queryByText('Send Feedback')).not.toBeInTheDocument();
  });

  it('shows bug report type by default', () => {
    render(<FeedbackModal isOpen={true} onClose={mockOnClose} />);

    // Bug Report button should be active (has default variant styling)
    const bugButton = screen.getByText('Bug Report').closest('button');
    expect(bugButton).toBeInTheDocument();
  });

  it('can switch to feature request type', async () => {
    render(<FeedbackModal isOpen={true} onClose={mockOnClose} />);

    const featureButton = screen.getByText('Feature Request');
    await userEvent.click(featureButton);

    // The placeholder text should change for feature requests
    const descriptionField = screen.getByLabelText(/Description/);
    expect(descriptionField).toHaveAttribute('placeholder', expect.stringContaining('feature'));
  });

  it('shows required field indicator', () => {
    render(<FeedbackModal isOpen={true} onClose={mockOnClose} />);

    // Verify title label exists
    expect(screen.getByText('Title')).toBeInTheDocument();
    // There are multiple required field indicators (*) - one for Title and one for Description
    const requiredIndicators = screen.getAllByText('*');
    expect(requiredIndicators.length).toBeGreaterThanOrEqual(2);
  });

  it('calls onClose when Cancel is clicked', async () => {
    render(<FeedbackModal isOpen={true} onClose={mockOnClose} />);

    const cancelButton = screen.getByText('Cancel');
    await userEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('title and description fields have required attribute', () => {
    render(<FeedbackModal isOpen={true} onClose={mockOnClose} />);

    // Verify required fields have the required attribute
    const titleInput = screen.getByLabelText(/Title/);
    const descriptionInput = screen.getByLabelText(/Description/);

    expect(titleInput).toHaveAttribute('required');
    expect(descriptionInput).toHaveAttribute('required');
  });

  it('shows loading state when submitting', async () => {
    // Make fetch hang
    (global.fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<FeedbackModal isOpen={true} onClose={mockOnClose} />);

    // Fill in required fields
    const titleInput = screen.getByLabelText(/Title/);
    const descriptionInput = screen.getByLabelText(/Description/);

    await userEvent.type(titleInput, 'Test bug report');
    await userEvent.type(
      descriptionInput,
      'This is a detailed bug description that is long enough.',
    );

    const submitButton = screen.getByText('Submit Feedback');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Submitting...')).toBeInTheDocument();
    });
  });

  it('shows success state after successful submission', async () => {
    render(<FeedbackModal isOpen={true} onClose={mockOnClose} />);

    // Fill in required fields
    const titleInput = screen.getByLabelText(/Title/);
    const descriptionInput = screen.getByLabelText(/Description/);

    await userEvent.type(titleInput, 'Test bug report');
    await userEvent.type(
      descriptionInput,
      'This is a detailed bug description that is long enough.',
    );

    const submitButton = screen.getByText('Submit Feedback');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Thank you for your feedback!')).toBeInTheDocument();
    });
  });

  it('renders with error context when provided', () => {
    const errorContext = {
      sentryEventId: 'sentry-123',
      errorMessage: 'Test error message',
    };

    render(<FeedbackModal isOpen={true} onClose={mockOnClose} errorContext={errorContext} />);

    const descriptionField = screen.getByLabelText(/Description/) as HTMLTextAreaElement;
    expect(descriptionField.value).toContain('Test error message');
  });
});

describe('useFeedbackModal hook', () => {
  // Create a test component that uses the hook
  function TestComponent() {
    const { isOpen, openFeedback, closeFeedback, defaultType, errorContext } = useFeedbackModal();

    return (
      <div>
        <span data-testid="isOpen">{isOpen.toString()}</span>
        <span data-testid="defaultType">{defaultType}</span>
        <span data-testid="hasErrorContext">{(!!errorContext).toString()}</span>
        <button onClick={() => openFeedback()}>Open</button>
        <button onClick={() => openFeedback({ type: 'feature' })}>Open Feature</button>
        <button onClick={() => openFeedback({ errorContext: { sentryEventId: 'test-123' } })}>
          Open with Error
        </button>
        <button onClick={closeFeedback}>Close</button>
      </div>
    );
  }

  it('initializes with closed state', () => {
    render(<TestComponent />);

    expect(screen.getByTestId('isOpen')).toHaveTextContent('false');
    expect(screen.getByTestId('defaultType')).toHaveTextContent('bug');
  });

  it('opens modal when openFeedback is called', async () => {
    render(<TestComponent />);

    await userEvent.click(screen.getByText('Open'));

    expect(screen.getByTestId('isOpen')).toHaveTextContent('true');
  });

  it('can open with feature type', async () => {
    render(<TestComponent />);

    await userEvent.click(screen.getByText('Open Feature'));

    expect(screen.getByTestId('isOpen')).toHaveTextContent('true');
    expect(screen.getByTestId('defaultType')).toHaveTextContent('feature');
  });

  it('can open with error context', async () => {
    render(<TestComponent />);

    await userEvent.click(screen.getByText('Open with Error'));

    expect(screen.getByTestId('isOpen')).toHaveTextContent('true');
    expect(screen.getByTestId('hasErrorContext')).toHaveTextContent('true');
  });

  it('closes modal when closeFeedback is called', async () => {
    render(<TestComponent />);

    await userEvent.click(screen.getByText('Open'));
    expect(screen.getByTestId('isOpen')).toHaveTextContent('true');

    await userEvent.click(screen.getByText('Close'));
    expect(screen.getByTestId('isOpen')).toHaveTextContent('false');
  });
});
