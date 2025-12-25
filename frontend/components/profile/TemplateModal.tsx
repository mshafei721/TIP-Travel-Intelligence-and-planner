'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import type { TripTemplate, TripTemplateCreate, TravelStyle } from '@/types/profile';

const TRAVEL_STYLES: TravelStyle[] = ['budget', 'balanced', 'luxury'];
const DIETARY_OPTIONS = [
  'Vegetarian',
  'Vegan',
  'Gluten-free',
  'Dairy-free',
  'Nut allergy',
  'Halal',
  'Kosher',
];

export interface TemplateModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  template?: TripTemplate;
  onSave: (template: TripTemplateCreate) => Promise<void>;
}

/**
 * TemplateModal - Create or edit trip template
 *
 * Form fields:
 * - Template name
 * - Destinations (semicolon-separated)
 * - Date pattern
 * - Travel style
 * - Dietary restrictions
 */
export function TemplateModal({ open, onOpenChange, template, onSave }: TemplateModalProps) {
  const isEditing = !!template;

  const [formData, setFormData] = useState({
    name: '',
    destinations: '',
    description: '',
    travelStyle: 'balanced' as TravelStyle,
    dietaryRestrictions: [] as string[],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset form when template changes or modal opens
  useEffect(() => {
    if (open) {
      if (template) {
        setFormData({
          name: template.name,
          destinations: template.destinations
            .map((destination) =>
              destination.city ? `${destination.city}, ${destination.country}` : destination.country,
            )
            .join('; '),
          description: template.description || '',
          travelStyle: template.preferences?.travel_style || 'balanced',
          dietaryRestrictions: template.preferences?.dietary_restrictions || [],
        });
      } else {
        setFormData({
          name: '',
          destinations: '',
          description: '',
          travelStyle: 'balanced',
          dietaryRestrictions: [],
        });
      }
    }
  }, [open, template]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const destinationInputs = formData.destinations
        .split(/[;\n]/)
        .map((destination) => destination.trim())
        .filter(Boolean);

      const destinations = destinationInputs.map((destination) => {
        const [city, ...rest] = destination
          .split(',')
          .map((part) => part.trim())
          .filter(Boolean);
        if (rest.length > 0) {
          return { city, country: rest.join(', ') };
        }
        return { country: city };
      });

      const templateData: TripTemplateCreate = {
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        destinations,
        preferences: {
          travel_style: formData.travelStyle,
          dietary_restrictions: formData.dietaryRestrictions,
        },
      };

      await onSave(templateData);
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to save template:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleDietaryRestriction = (restriction: string) => {
    setFormData((prev) => ({
      ...prev,
      dietaryRestrictions: prev.dietaryRestrictions.includes(restriction)
        ? prev.dietaryRestrictions.filter((r) => r !== restriction)
        : [...prev.dietaryRestrictions, restriction],
    }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Template' : 'Create Template'}</DialogTitle>
          <DialogDescription>
            Save common trip details to speed up future trip creation
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Template Name */}
          <div className="space-y-2">
            <Label htmlFor="template-name">Template Name *</Label>
            <Input
              id="template-name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="E.g., Weekend Getaway, Business Trip"
              required
              disabled={isSubmitting}
            />
          </div>

          {/* Destinations */}
          <div className="space-y-2">
            <Label htmlFor="destinations">Destinations *</Label>
            <Input
              id="destinations"
              value={formData.destinations}
              onChange={(e) => setFormData({ ...formData, destinations: e.target.value })}
              placeholder="E.g., Paris, France; London, UK"
              required
              disabled={isSubmitting}
            />
            <p className="text-xs text-slate-500">Separate multiple destinations with semicolons</p>
          </div>

          {/* Date Pattern */}
          <div className="space-y-2">
            <Label htmlFor="date-pattern">Date Pattern *</Label>
            <Input
              id="date-pattern"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="E.g., Weekend, 1 week, 2 weeks"
              required
              disabled={isSubmitting}
            />
          </div>

          {/* Travel Style */}
          <div className="space-y-2">
            <Label>Travel Style *</Label>
            <div className="grid grid-cols-2 gap-2">
              {TRAVEL_STYLES.map((style) => (
                <button
                  key={style}
                  type="button"
                  onClick={() => setFormData({ ...formData, travelStyle: style })}
                  disabled={isSubmitting}
                  className={`rounded-lg border p-3 text-sm font-medium transition-all ${
                    formData.travelStyle === style
                      ? 'border-blue-500 bg-blue-50 text-blue-900 dark:border-blue-400 dark:bg-blue-950/20 dark:text-blue-100'
                      : 'border-slate-200 hover:border-slate-300 dark:border-slate-800 dark:hover:border-slate-700'
                  }`}
                >
                  {style
                    .split('-')
                    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Dietary Restrictions */}
          <div className="space-y-2">
            <Label>Dietary Restrictions (Optional)</Label>
            <div className="grid grid-cols-2 gap-2">
              {DIETARY_OPTIONS.map((option) => (
                <div key={option} className="flex items-center space-x-2">
                  <Checkbox
                    id={`template-${option}`}
                    checked={formData.dietaryRestrictions.includes(option)}
                    onChange={() => toggleDietaryRestriction(option)}
                    disabled={isSubmitting}
                  />
                  <label htmlFor={`template-${option}`} className="text-sm font-medium">
                    {option}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Template'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
