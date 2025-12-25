'use client';

import { Heart, HandHeart, Ban, Book, ExternalLink } from 'lucide-react';
import IntelligenceCard from './IntelligenceCard';
import type { CulturalNorms } from '@/types/destination';

interface CultureCardProps {
  data: CulturalNorms;
  isExpanded?: boolean;
  isLoading?: boolean;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
  onLinkClick?: (url: string, title: string) => void;
}

export default function CultureCard({
  data,
  isExpanded,
  isLoading,
  onExpand,
  onCollapse,
  onLinkClick,
}: CultureCardProps) {
  return (
    <IntelligenceCard
      id="culture"
      title="Cultural Norms & Etiquette"
      icon={<Heart className="w-6 h-6" />}
      iconColor="text-pink-600 dark:text-pink-400"
      isExpanded={isExpanded}
      isLoading={isLoading}
      onExpand={onExpand}
      onCollapse={onCollapse}
    >
      <div className="space-y-5">
        {/* Dress code */}
        <div className="p-4 bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-lg">
          <p className="text-xs font-semibold text-purple-700 dark:text-purple-400 uppercase tracking-wide mb-2">
            Dress Code
          </p>
          <p className="text-sm text-purple-900 dark:text-purple-200">{data.dressCode}</p>
        </div>

        {/* Greetings */}
        <div className="p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p className="text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wide mb-2">
            Greetings
          </p>
          <p className="text-sm text-blue-900 dark:text-blue-200">{data.greetings}</p>
        </div>

        {/* Customs */}
        {data.customs.length > 0 && (
          <div className="p-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg">
            <p className="text-xs font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wide mb-3">
              Customs & Traditions
            </p>
            <ul className="space-y-2">
              {data.customs.map((custom, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-1.5 h-1.5 bg-amber-500 rounded-full mt-2" />
                  <span className="text-sm text-amber-900 dark:text-amber-200">{custom}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Do's and Don'ts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Do's */}
          {data.dos.length > 0 && (
            <div className="p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <HandHeart className="w-5 h-5 text-green-600 dark:text-green-400" />
                <p className="text-xs font-semibold text-green-700 dark:text-green-400 uppercase tracking-wide">
                  Do
                </p>
              </div>
              <ul className="space-y-2">
                {data.dos.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="flex-shrink-0 text-green-600 dark:text-green-400 mt-1">✓</span>
                    <span className="text-sm text-green-900 dark:text-green-200">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Don'ts */}
          {data.donts.length > 0 && (
            <div className="p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <Ban className="w-5 h-5 text-red-600 dark:text-red-400" />
                <p className="text-xs font-semibold text-red-700 dark:text-red-400 uppercase tracking-wide">
                  Don&apos;t
                </p>
              </div>
              <ul className="space-y-2">
                {data.donts.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="flex-shrink-0 text-red-600 dark:text-red-400 mt-1">✗</span>
                    <span className="text-sm text-red-900 dark:text-red-200">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Religious considerations */}
        {data.religiousConsiderations && (
          <div className="p-4 bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800 rounded-lg">
            <div className="flex items-start gap-3">
              <Book className="w-5 h-5 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-semibold text-indigo-700 dark:text-indigo-400 uppercase tracking-wide mb-2">
                  Religious Considerations
                </p>
                <p className="text-sm text-indigo-900 dark:text-indigo-200">
                  {data.religiousConsiderations}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Language tips */}
        {data.languageTips && data.languageTips.length > 0 && (
          <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide mb-2">
              Language Tips
            </p>
            <ul className="space-y-1">
              {data.languageTips.map((tip, idx) => (
                <li key={idx} className="text-sm text-slate-700 dark:text-slate-300">
                  • {tip}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Etiquette guides */}
        {data.etiquetteGuides && data.etiquetteGuides.length > 0 && (
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
              Etiquette Guides
            </p>
            <div className="flex flex-wrap gap-2">
              {data.etiquetteGuides.map((link, idx) => (
                <a
                  key={idx}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => onLinkClick?.(link.url, link.title)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-pink-50 dark:bg-pink-950/30 border border-pink-200 dark:border-pink-800 text-pink-700 dark:text-pink-300 text-sm font-medium rounded-lg hover:bg-pink-100 dark:hover:bg-pink-900/50 transition-colors"
                >
                  <span>{link.title}</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </IntelligenceCard>
  );
}
