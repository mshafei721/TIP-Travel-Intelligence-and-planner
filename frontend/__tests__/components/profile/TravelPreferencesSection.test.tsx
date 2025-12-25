import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TravelPreferencesSection } from '@/components/profile/TravelPreferencesSection';
import type { TravelPreferences } from '@/types/profile';

// Mock useDebounce hook
jest.mock('@/hooks/useDebounce', () => ({
  useDebounce: <T,>(value: T) => value,
}));

describe('TravelPreferencesSection', () => {
  const mockPreferences: TravelPreferences = {
    travelStyle: 'balanced',
    dietaryRestrictions: ['Vegetarian'],
    accessibilityNeeds: 'Wheelchair accessible accommodations',
  };

  const mockOnUpdate = jest.fn(() => Promise.resolve());

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render section header and description', () => {
    render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

    expect(screen.getByText('Travel Preferences')).toBeInTheDocument();
    expect(screen.getByText('Customize your travel style and dietary needs')).toBeInTheDocument();
  });

  describe('Travel Style Selection', () => {
    it('should display all travel style options', () => {
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      expect(screen.getByText('Budget')).toBeInTheDocument();
      expect(screen.getByText('Balanced')).toBeInTheDocument();
      expect(screen.getByText('Luxury')).toBeInTheDocument();
    });

    it('should show selected travel style', () => {
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      // Find the card containing "Balanced" text
      const balancedText = screen.getByText('Balanced');
      const balancedCard = balancedText.closest('[class*="border"]');
      expect(balancedCard).toHaveClass('border-blue-500');
    });

    it('should call onUpdate when travel style is clicked', async () => {
      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      const luxuryOption = screen.getByText('Luxury');
      await user.click(luxuryOption);

      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith(
          expect.objectContaining({
            travelStyle: 'luxury',
          }),
        );
      });
    });

    it('should show descriptions for each travel style', () => {
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      expect(
        screen.getByText(/Cost-effective options, hostels, local transport/i),
      ).toBeInTheDocument();
      expect(screen.getByText(/Mix of comfort and value, mid-range hotels/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Premium experiences, 4-5 star hotels, private transport/i),
      ).toBeInTheDocument();
    });

    it('should highlight only selected travel style', async () => {
      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      // Initially balanced should be highlighted
      const balancedCard = screen.getByText('Balanced').closest('[class*="border"]');
      expect(balancedCard).toHaveClass('border-blue-500');

      // Click luxury
      await user.click(screen.getByText('Luxury'));

      await waitFor(() => {
        const luxuryCard = screen.getByText('Luxury').closest('[class*="border"]');
        expect(luxuryCard).toHaveClass('border-blue-500');

        const balancedCardAfter = screen.getByText('Balanced').closest('[class*="border"]');
        expect(balancedCardAfter).not.toHaveClass('border-blue-500');
      });
    });
  });

  describe('Dietary Restrictions', () => {
    it('should display all dietary restriction options', () => {
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      expect(screen.getByLabelText('Vegetarian')).toBeInTheDocument();
      expect(screen.getByLabelText('Vegan')).toBeInTheDocument();
      expect(screen.getByLabelText('Gluten-free')).toBeInTheDocument();
      expect(screen.getByLabelText('Dairy-free')).toBeInTheDocument();
      expect(screen.getByLabelText('Nut allergy')).toBeInTheDocument();
      expect(screen.getByLabelText('Halal')).toBeInTheDocument();
      expect(screen.getByLabelText('Kosher')).toBeInTheDocument();
    });

    it('should show checked dietary restrictions', () => {
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      const vegetarianCheckbox = screen.getByLabelText('Vegetarian') as HTMLInputElement;
      expect(vegetarianCheckbox).toBeChecked();

      const veganCheckbox = screen.getByLabelText('Vegan') as HTMLInputElement;
      expect(veganCheckbox).not.toBeChecked();
    });

    it('should toggle dietary restrictions when clicked', async () => {
      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      const veganCheckbox = screen.getByLabelText('Vegan');
      await user.click(veganCheckbox);

      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith(
          expect.objectContaining({
            dietaryRestrictions: expect.arrayContaining(['Vegetarian', 'Vegan']),
          }),
        );
      });
    });

    it('should remove dietary restriction when unchecked', async () => {
      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      const vegetarianCheckbox = screen.getByLabelText('Vegetarian');
      await user.click(vegetarianCheckbox);

      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith(
          expect.objectContaining({
            dietaryRestrictions: expect.not.arrayContaining(['Vegetarian']),
          }),
        );
      });
    });

    it('should handle multiple dietary restrictions', async () => {
      const multipleRestrictions: TravelPreferences = {
        travelStyle: 'balanced',
        dietaryRestrictions: ['Vegetarian', 'Gluten-free', 'Halal'],
      };

      render(
        <TravelPreferencesSection preferences={multipleRestrictions} onUpdate={mockOnUpdate} />,
      );

      expect(screen.getByLabelText('Vegetarian')).toBeChecked();
      expect(screen.getByLabelText('Gluten-free')).toBeChecked();
      expect(screen.getByLabelText('Halal')).toBeChecked();
      expect(screen.getByLabelText('Vegan')).not.toBeChecked();
    });
  });

  describe('Accessibility Needs', () => {
    it('should display accessibility needs textarea', () => {
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByLabelText(/Accessibility Needs/i) as HTMLTextAreaElement;
      expect(textarea).toBeInTheDocument();
      expect(textarea.value).toBe('Wheelchair accessible accommodations');
    });

    it('should show placeholder when no accessibility needs', () => {
      const noNeeds: TravelPreferences = {
        travelStyle: 'balanced',
        dietaryRestrictions: [],
      };

      render(<TravelPreferencesSection preferences={noNeeds} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByPlaceholderText(/wheelchair accessible accommodations/i);
      expect(textarea).toBeInTheDocument();
    });

    it('should call onUpdate when accessibility needs change', async () => {
      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByLabelText(/Accessibility Needs/i);
      await user.clear(textarea);
      await user.type(textarea, 'Visual aids and hearing assistance');

      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith(
          expect.objectContaining({
            accessibilityNeeds: 'Visual aids and hearing assistance',
          }),
        );
      });
    });

    it('should indicate accessibility needs field is optional', () => {
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      expect(screen.getByText('(Optional)')).toBeInTheDocument();
    });
  });

  describe('Auto-save functionality', () => {
    it('should show saving indicator when update is in progress', async () => {
      const slowUpdate = jest.fn(
        (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 1000)),
      );

      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={slowUpdate} />);

      const budgetOption = screen.getByText('Budget');
      await user.click(budgetOption);

      await waitFor(() => {
        expect(screen.getByText('Saving...')).toBeInTheDocument();
      });
    });

    it('should show saved indicator after successful update', async () => {
      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      const budgetOption = screen.getByText('Budget');
      await user.click(budgetOption);

      await waitFor(() => {
        expect(screen.getByText('Saved')).toBeInTheDocument();
      });
    });

    it('should show error indicator when update fails', async () => {
      const failingUpdate = jest.fn(
        (): Promise<void> => Promise.reject(new Error('Update failed')),
      );

      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={failingUpdate} />);

      const budgetOption = screen.getByText('Budget');
      await user.click(budgetOption);

      await waitFor(() => {
        expect(screen.getByText('Failed to save')).toBeInTheDocument();
      });
    });

    it('should disable checkboxes when saving', async () => {
      const slowUpdate = jest.fn(
        (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 1000)),
      );

      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={slowUpdate} />);

      const veganCheckbox = screen.getByLabelText('Vegan');
      await user.click(veganCheckbox);

      await waitFor(() => {
        expect(screen.getByLabelText('Vegetarian')).toBeDisabled();
        expect(veganCheckbox).toBeDisabled();
      });
    });

    it('should disable textarea when saving', async () => {
      const slowUpdate = jest.fn(
        (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 1000)),
      );

      const user = userEvent.setup();
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={slowUpdate} />);

      const textarea = screen.getByLabelText(/Accessibility Needs/i);
      await user.type(textarea, ' additional needs');

      await waitFor(() => {
        expect(textarea).toBeDisabled();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels for all form controls', () => {
      render(<TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />);

      expect(screen.getByLabelText('Vegetarian')).toHaveAccessibleName();
      expect(screen.getByLabelText(/Accessibility Needs/i)).toHaveAccessibleName();
    });

    it('should use semantic HTML for dietary restrictions list', () => {
      const { container } = render(
        <TravelPreferencesSection preferences={mockPreferences} onUpdate={mockOnUpdate} />,
      );

      const checkboxes = container.querySelectorAll('input[type="checkbox"]');
      expect(checkboxes.length).toBeGreaterThan(0);

      checkboxes.forEach((checkbox) => {
        expect(checkbox).toHaveAttribute('id');
      });
    });
  });
});
