'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Search, Filter, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PublicTemplateCard } from '@/components/templates/PublicTemplateCard';
import { FeaturedTemplates } from '@/components/templates/FeaturedTemplates';
import { TemplateGrid } from '@/components/templates/TemplateGrid';
import { UseTemplateDialog } from '@/components/templates/UseTemplateDialog';
import {
  listTemplates,
  listPublicTemplates,
  getFeaturedTemplates,
  cloneTemplate,
  deleteTemplate,
} from '@/lib/api/templates';
import type { TripTemplate, PublicTemplate } from '@/types/profile';

// Popular destination filters
const DESTINATION_FILTERS = ['All', 'Europe', 'Asia', 'Americas', 'Africa', 'Oceania'];

// Popular tag filters
const TAG_FILTERS = [
  'weekend',
  'adventure',
  'relaxation',
  'family',
  'budget',
  'luxury',
  'cultural',
  'beach',
];

export default function TemplatesPage() {
  const router = useRouter();

  // State
  const [userTemplates, setUserTemplates] = useState<TripTemplate[]>([]);
  const [publicTemplates, setPublicTemplates] = useState<PublicTemplate[]>([]);
  const [featuredTemplates, setFeaturedTemplates] = useState<PublicTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDestination, setSelectedDestination] = useState('All');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Dialog state
  const [selectedTemplate, setSelectedTemplate] = useState<PublicTemplate | null>(null);
  const [useDialogOpen, setUseDialogOpen] = useState(false);
  const [, setCloning] = useState(false);

  // Fetch templates
  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [userResult, publicResult, featuredResult] = await Promise.allSettled([
        listTemplates(),
        listPublicTemplates({
          destination: selectedDestination !== 'All' ? selectedDestination : undefined,
          tag: selectedTags.length === 1 ? selectedTags[0] : undefined,
          limit: 20,
        }),
        getFeaturedTemplates(6),
      ]);

      if (userResult.status === 'fulfilled') {
        setUserTemplates(userResult.value);
      }
      if (publicResult.status === 'fulfilled') {
        setPublicTemplates(publicResult.value);
      }
      if (featuredResult.status === 'fulfilled') {
        setFeaturedTemplates(featuredResult.value);
      }
    } catch (err) {
      setError('Failed to load templates. Please try again.');
      console.error('Error fetching templates:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedDestination, selectedTags]);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  // Filter templates by search query
  const filteredPublicTemplates = publicTemplates.filter((template) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      template.name.toLowerCase().includes(query) ||
      template.description?.toLowerCase().includes(query) ||
      template.destinations.some(
        (d) => d.country.toLowerCase().includes(query) || d.city?.toLowerCase().includes(query),
      ) ||
      template.tags.some((t) => t.toLowerCase().includes(query))
    );
  });

  // Filter by selected tags
  const tagFilteredTemplates =
    selectedTags.length > 0
      ? filteredPublicTemplates.filter((template) =>
          selectedTags.some((tag) => template.tags.includes(tag)),
        )
      : filteredPublicTemplates;

  // Handle template actions
  const handleUseTemplate = (template: PublicTemplate) => {
    setSelectedTemplate(template);
    setUseDialogOpen(true);
  };

  const handleCloneTemplate = async (template: PublicTemplate) => {
    setCloning(true);
    try {
      await cloneTemplate(template.id);
      // Refresh user templates
      const updated = await listTemplates();
      setUserTemplates(updated);
      // Show success feedback
      alert(`"${template.name}" has been added to your templates!`);
    } catch (err) {
      console.error('Error cloning template:', err);
      alert('Failed to clone template. Please try again.');
    } finally {
      setCloning(false);
    }
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    );
  };

  const handleEditTemplate = (template: TripTemplate) => {
    router.push(`/profile?tab=templates&edit=${template.id}`);
  };

  const handleDeleteTemplate = async (id: string) => {
    try {
      await deleteTemplate(id);
      // Refresh after deletion
      const updated = await listTemplates();
      setUserTemplates(updated);
    } catch (err) {
      console.error('Error deleting template:', err);
      alert('Failed to delete template. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-blue-600" />
          <p className="mt-2 text-sm text-slate-500">Loading templates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
            Template Library
          </h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Browse templates or create your own trip configurations
          </p>
        </div>
        <Button onClick={() => router.push('/profile?tab=templates')}>
          <Plus className="mr-2 h-4 w-4" />
          Create Template
        </Button>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-800 dark:bg-red-950/30 dark:text-red-400">
          {error}
          <Button
            variant="link"
            className="ml-2 text-red-700 dark:text-red-400"
            onClick={fetchTemplates}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Featured Templates */}
      {featuredTemplates.length > 0 && (
        <section>
          <h2 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">
            Featured Templates
          </h2>
          <FeaturedTemplates
            templates={featuredTemplates}
            onUseTemplate={handleUseTemplate}
            onClone={handleCloneTemplate}
          />
        </section>
      )}

      {/* My Templates */}
      {userTemplates.length > 0 && (
        <section>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
              My Templates
            </h2>
            <Button variant="ghost" size="sm" onClick={() => router.push('/profile?tab=templates')}>
              Manage All
            </Button>
          </div>
          <TemplateGrid
            templates={userTemplates}
            onEdit={handleEditTemplate}
            onDelete={handleDeleteTemplate}
            variant="user"
          />
        </section>
      )}

      {/* Explore Public Templates */}
      <section>
        <h2 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">
          Explore Templates
        </h2>

        {/* Search and Filters */}
        <div className="mb-6 space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              placeholder="Search templates by name, destination, or tag..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Destination Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <Filter className="h-4 w-4 text-slate-400" />
            {DESTINATION_FILTERS.map((dest) => (
              <Badge
                key={dest}
                variant={selectedDestination === dest ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => setSelectedDestination(dest)}
              >
                {dest}
              </Badge>
            ))}
          </div>

          {/* Tag Filters */}
          <div className="flex flex-wrap gap-2">
            {TAG_FILTERS.map((tag) => (
              <Badge
                key={tag}
                variant={selectedTags.includes(tag) ? 'default' : 'secondary'}
                className="cursor-pointer"
                onClick={() => handleTagToggle(tag)}
              >
                #{tag}
              </Badge>
            ))}
            {selectedTags.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedTags([])}
                className="text-xs"
              >
                Clear filters
              </Button>
            )}
          </div>
        </div>

        {/* Template Grid */}
        {tagFilteredTemplates.length > 0 ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {tagFilteredTemplates.map((template) => (
              <PublicTemplateCard
                key={template.id}
                template={template}
                onUseTemplate={handleUseTemplate}
                onClone={handleCloneTemplate}
              />
            ))}
          </div>
        ) : (
          <div className="flex min-h-[200px] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 dark:border-slate-700 dark:bg-slate-900">
            <div className="text-center">
              <p className="text-slate-500 dark:text-slate-400">
                No templates found matching your criteria
              </p>
              <Button
                variant="link"
                onClick={() => {
                  setSearchQuery('');
                  setSelectedDestination('All');
                  setSelectedTags([]);
                }}
              >
                Clear all filters
              </Button>
            </div>
          </div>
        )}
      </section>

      {/* Use Template Dialog */}
      <UseTemplateDialog
        template={selectedTemplate}
        open={useDialogOpen}
        onOpenChange={setUseDialogOpen}
      />
    </div>
  );
}
