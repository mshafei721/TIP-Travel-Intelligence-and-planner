import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TravelerDetailsSection } from '@/components/profile/TravelerDetailsSection';
import type { TravelerDetails } from '@/types/profile';

// Mock useDebounce hook
jest.mock('@/hooks/useDebounce', () => ({
  useDebounce: <T,>(value: T) => value,
}));

describe('TravelerDetailsSection', () => {
  const mockTravelerDetails: TravelerDetails = {
    nationality: 'US',
    residenceCountry: 'US',
    residencyStatus: 'citizen',
    dateOfBirth: '1990-01-15',
  };

  const mockOnUpdate = jest.fn(() => Promise.resolve());

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render all form fields with initial values', () => {
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    // Check section title
    expect(screen.getByText('Default Traveler Details')).toBeInTheDocument();
    expect(screen.getByText('Pre-fill trip creation with your common details')).toBeInTheDocument();

    // Check all fields exist
    expect(screen.getByLabelText('Nationality')).toBeInTheDocument();
    expect(screen.getByLabelText('Residence Country')).toBeInTheDocument();
    expect(screen.getByLabelText('Residency Status')).toBeInTheDocument();
    expect(screen.getByLabelText('Date of Birth')).toBeInTheDocument();
  });

  it('should display selected nationality', () => {
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const nationalitySelect = screen.getByLabelText('Nationality') as HTMLSelectElement;
    expect(nationalitySelect.value).toBe('US');
  });

  it('should display selected residence country', () => {
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const residenceSelect = screen.getByLabelText('Residence Country') as HTMLSelectElement;
    expect(residenceSelect.value).toBe('US');
  });

  it('should display selected residency status', () => {
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const statusSelect = screen.getByLabelText('Residency Status') as HTMLSelectElement;
    expect(statusSelect.value).toBe('citizen');
  });

  it('should display date of birth', () => {
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const dobInput = screen.getByLabelText('Date of Birth') as HTMLInputElement;
    expect(dobInput.value).toBe('1990-01-15');
  });

  it('should have popular countries in optgroup', () => {
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const nationalitySelect = screen.getByLabelText('Nationality') as HTMLSelectElement;
    const optgroups = nationalitySelect.querySelectorAll('optgroup');

    expect(optgroups).toHaveLength(2);
    expect(optgroups[0]).toHaveAttribute('label', 'Popular Countries');
    expect(optgroups[1]).toHaveAttribute('label', 'All Countries');
  });

  it('should call onUpdate when nationality changes', async () => {
    const user = userEvent.setup();
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const nationalitySelect = screen.getByLabelText('Nationality');
    await user.selectOptions(nationalitySelect, 'GB');

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalledWith(
        expect.objectContaining({
          nationality: 'GB',
          residenceCountry: 'US',
          residencyStatus: 'citizen',
          dateOfBirth: '1990-01-15',
        }),
      );
    });
  });

  it('should call onUpdate when residence country changes', async () => {
    const user = userEvent.setup();
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const residenceSelect = screen.getByLabelText('Residence Country');
    await user.selectOptions(residenceSelect, 'CA');

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalledWith(
        expect.objectContaining({
          residenceCountry: 'CA',
        }),
      );
    });
  });

  it('should call onUpdate when residency status changes', async () => {
    const user = userEvent.setup();
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const statusSelect = screen.getByLabelText('Residency Status');
    await user.selectOptions(statusSelect, 'permanent_resident');

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalledWith(
        expect.objectContaining({
          residencyStatus: 'permanent_resident',
        }),
      );
    });
  });

  it('should call onUpdate when date of birth changes', async () => {
    const user = userEvent.setup();
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const dobInput = screen.getByLabelText('Date of Birth');
    await user.clear(dobInput);
    await user.type(dobInput, '1995-06-20');

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalledWith(
        expect.objectContaining({
          dateOfBirth: '1995-06-20',
        }),
      );
    });
  });

  it('should show saving indicator when save is in progress', async () => {
    const slowUpdate = jest.fn(
      (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 1000)),
    );

    const user = userEvent.setup();
    render(<TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={slowUpdate} />);

    const nationalitySelect = screen.getByLabelText('Nationality');
    await user.selectOptions(nationalitySelect, 'GB');

    // Should show saving state
    await waitFor(() => {
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });
  });

  it('should show saved indicator after successful save', async () => {
    const user = userEvent.setup();
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const nationalitySelect = screen.getByLabelText('Nationality');
    await user.selectOptions(nationalitySelect, 'GB');

    await waitFor(() => {
      expect(screen.getByText('Saved')).toBeInTheDocument();
    });
  });

  it('should show error indicator when save fails', async () => {
    const failingUpdate = jest.fn(() => Promise.reject(new Error('Save failed')));

    const user = userEvent.setup();
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={failingUpdate} />,
    );

    const nationalitySelect = screen.getByLabelText('Nationality');
    await user.selectOptions(nationalitySelect, 'GB');

    await waitFor(() => {
      expect(screen.getByText('Failed to save')).toBeInTheDocument();
    });
  });

  it('should disable fields when saving', async () => {
    const slowUpdate = jest.fn(
      (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 1000)),
    );

    const user = userEvent.setup();
    render(<TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={slowUpdate} />);

    const nationalitySelect = screen.getByLabelText('Nationality');
    await user.selectOptions(nationalitySelect, 'GB');

    // Fields should be disabled while saving
    await waitFor(() => {
      expect(nationalitySelect).toBeDisabled();
      expect(screen.getByLabelText('Residence Country')).toBeDisabled();
      expect(screen.getByLabelText('Residency Status')).toBeDisabled();
      expect(screen.getByLabelText('Date of Birth')).toBeDisabled();
    });
  });

  it('should include comprehensive country list', () => {
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const nationalitySelect = screen.getByLabelText('Nationality') as HTMLSelectElement;
    const options = Array.from(nationalitySelect.options).filter((opt) => opt.value !== '');

    // Should have 200+ countries
    expect(options.length).toBeGreaterThan(190);

    // Check some specific countries exist
    expect(options.some((opt) => opt.value === 'US')).toBe(true);
    expect(options.some((opt) => opt.value === 'GB')).toBe(true);
    expect(options.some((opt) => opt.value === 'JP')).toBe(true);
    expect(options.some((opt) => opt.value === 'BR')).toBe(true);
    expect(options.some((opt) => opt.value === 'IN')).toBe(true);
  });

  it('should have accessible form controls', () => {
    render(
      <TravelerDetailsSection travelerDetails={mockTravelerDetails} onUpdate={mockOnUpdate} />,
    );

    const nationalitySelect = screen.getByLabelText('Nationality');
    const residenceSelect = screen.getByLabelText('Residence Country');
    const statusSelect = screen.getByLabelText('Residency Status');
    const dobInput = screen.getByLabelText('Date of Birth');

    expect(nationalitySelect).toHaveAccessibleName();
    expect(residenceSelect).toHaveAccessibleName();
    expect(statusSelect).toHaveAccessibleName();
    expect(dobInput).toHaveAccessibleName();
  });
});
