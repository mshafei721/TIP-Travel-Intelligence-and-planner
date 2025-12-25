'use client';

import { useState } from 'react';
import { FileText, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SectionCard } from './SectionCard';
import { TemplateCard } from './TemplateCard';
import { TemplateModal } from './TemplateModal';
import type { TripTemplate, TripTemplateCreate, TripTemplateUpdate } from '@/types/profile';

export interface SavedTemplatesSectionProps {
  templates: TripTemplate[];
  onTemplateCreate: (template: TripTemplateCreate) => Promise<void>;
  onTemplateEdit: (id: string, template: TripTemplateUpdate) => Promise<void>;
  onTemplateDelete: (id: string) => Promise<void>;
}

/**
 * SavedTemplatesSection - Manage trip templates
 *
 * Features:
 * - Display templates as cards in grid
 * - Create new template
 * - Edit existing template
 * - Delete template with confirmation
 * - Empty state when no templates exist
 */
export function SavedTemplatesSection({
  templates,
  onTemplateCreate,
  onTemplateEdit,
  onTemplateDelete,
}: SavedTemplatesSectionProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<TripTemplate | undefined>();

  const handleCreate = () => {
    setEditingTemplate(undefined);
    setIsModalOpen(true);
  };

  const handleEdit = (template: TripTemplate) => {
    setEditingTemplate(template);
    setIsModalOpen(true);
  };

  const handleSave = async (templateData: TripTemplateCreate) => {
    if (editingTemplate) {
      await onTemplateEdit(editingTemplate.id, templateData);
    } else {
      await onTemplateCreate(templateData);
    }
  };

  return (
    <>
      <SectionCard
        title="Saved Templates"
        description="Quick-start templates for faster trip creation"
        icon={FileText}
      >
        {templates.length === 0 ? (
          /* Empty State */
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="rounded-full bg-slate-100 p-4 dark:bg-slate-800">
              <FileText className="h-8 w-8 text-slate-400" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-slate-50">
              No templates yet
            </h3>
            <p className="mt-2 max-w-sm text-sm text-slate-600 dark:text-slate-400">
              Create a trip template to speed up future trip creation with pre-filled preferences
              and destinations.
            </p>
            <Button onClick={handleCreate} className="mt-6">
              <Plus className="h-4 w-4" />
              Create Your First Template
            </Button>
          </div>
        ) : (
          /* Templates Grid */
          <div className="space-y-4">
            <div>
              <Button onClick={handleCreate}>
                <Plus className="h-4 w-4" />
                Create Template
              </Button>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {templates.map((template) => (
                <TemplateCard
                  key={template.id}
                  template={template}
                  onEdit={handleEdit}
                  onDelete={onTemplateDelete}
                />
              ))}
            </div>
          </div>
        )}
      </SectionCard>

      {/* Template Modal */}
      <TemplateModal
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
        template={editingTemplate}
        onSave={handleSave}
      />
    </>
  );
}
