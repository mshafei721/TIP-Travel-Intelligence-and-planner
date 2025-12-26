'use client';

import { useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PublicTemplateCard } from './PublicTemplateCard';
import type { PublicTemplate } from '@/types/profile';

export interface FeaturedTemplatesProps {
  templates: PublicTemplate[];
  onUseTemplate: (template: PublicTemplate) => void;
  onClone: (template: PublicTemplate) => void;
}

/**
 * FeaturedTemplates - Horizontally scrollable carousel of featured templates
 */
export function FeaturedTemplates({ templates, onUseTemplate, onClone }: FeaturedTemplatesProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: 'left' | 'right') => {
    if (!scrollContainerRef.current) return;

    const container = scrollContainerRef.current;
    const scrollAmount = container.clientWidth * 0.8;

    container.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth',
    });
  };

  if (templates.length === 0) return null;

  return (
    <div className="relative group">
      {/* Scroll Buttons */}
      <Button
        variant="outline"
        size="icon"
        className="absolute -left-4 top-1/2 z-10 hidden h-10 w-10 -translate-y-1/2 rounded-full bg-white shadow-lg opacity-0 transition-opacity group-hover:opacity-100 md:flex dark:bg-slate-800"
        onClick={() => scroll('left')}
        aria-label="Scroll left"
      >
        <ChevronLeft className="h-5 w-5" />
      </Button>

      <Button
        variant="outline"
        size="icon"
        className="absolute -right-4 top-1/2 z-10 hidden h-10 w-10 -translate-y-1/2 rounded-full bg-white shadow-lg opacity-0 transition-opacity group-hover:opacity-100 md:flex dark:bg-slate-800"
        onClick={() => scroll('right')}
        aria-label="Scroll right"
      >
        <ChevronRight className="h-5 w-5" />
      </Button>

      {/* Scrollable Container */}
      <div
        ref={scrollContainerRef}
        className="flex gap-6 overflow-x-auto pb-4 scrollbar-hide snap-x snap-mandatory"
        style={{
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        }}
      >
        {templates.map((template) => (
          <div key={template.id} className="w-[320px] flex-shrink-0 snap-start">
            <PublicTemplateCard
              template={template}
              onUseTemplate={onUseTemplate}
              onClone={onClone}
            />
          </div>
        ))}
      </div>

      {/* Gradient Overlays */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-8 bg-gradient-to-r from-white to-transparent dark:from-slate-950" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-white to-transparent dark:from-slate-950" />
    </div>
  );
}
