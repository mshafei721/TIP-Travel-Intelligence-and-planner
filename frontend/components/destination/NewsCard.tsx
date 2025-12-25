'use client';

import { Newspaper, ExternalLink, TrendingUp } from 'lucide-react';
import IntelligenceCard from './IntelligenceCard';
import type { NewsItem } from '@/types/destination';

interface NewsCardProps {
  data: NewsItem[];
  isExpanded?: boolean;
  isLoading?: boolean;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
  onLinkClick?: (url: string, title: string) => void;
}

const relevanceColors = {
  high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  medium: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
  low: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200',
};

const categoryIcons: Record<string, string> = {
  politics: '🏛️',
  economy: '📈',
  culture: '🎭',
  tourism: '✈️',
  health: '🏥',
  general: '📰',
};

export default function NewsCard({
  data,
  isExpanded,
  isLoading,
  onExpand,
  onCollapse,
  onLinkClick,
}: NewsCardProps) {
  const sortedNews = [...data].sort((a, b) => {
    // Sort by relevance (high > medium > low) then by date (newest first)
    const relevanceOrder = { high: 3, medium: 2, low: 1 };
    const relevanceDiff = relevanceOrder[b.relevance] - relevanceOrder[a.relevance];
    if (relevanceDiff !== 0) return relevanceDiff;
    return new Date(b.date).getTime() - new Date(a.date).getTime();
  });

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <IntelligenceCard
      id="news"
      title="Latest News"
      icon={<Newspaper className="w-6 h-6" />}
      iconColor="text-indigo-600 dark:text-indigo-400"
      isExpanded={isExpanded}
      isLoading={isLoading}
      onExpand={onExpand}
      onCollapse={onCollapse}
      badge={
        <span className="text-xs text-slate-500 dark:text-slate-400">
          {data.length} recent {data.length === 1 ? 'article' : 'articles'}
        </span>
      }
    >
      <div className="space-y-3">
        {sortedNews.length === 0 ? (
          <div className="text-center py-8">
            <Newspaper className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto mb-3" />
            <p className="text-sm text-slate-500 dark:text-slate-400">
              No recent news articles available
            </p>
          </div>
        ) : (
          sortedNews.map((item) => (
            <a
              key={item.id}
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => onLinkClick?.(item.url, item.headline)}
              className="
                block group
                p-4 bg-white dark:bg-slate-900
                border border-slate-200 dark:border-slate-800
                rounded-lg
                hover:shadow-lg hover:border-indigo-300 dark:hover:border-indigo-700
                transition-all duration-200
              "
            >
              <div className="flex items-start gap-3">
                {/* Category icon */}
                <div className="flex-shrink-0 w-10 h-10 bg-indigo-50 dark:bg-indigo-950/30 rounded-lg flex items-center justify-center text-2xl">
                  {categoryIcons[item.category || 'general']}
                </div>

                <div className="flex-1 min-w-0">
                  {/* Headline */}
                  <h4
                    className="
                    text-base font-semibold
                    text-slate-900 dark:text-slate-50
                    group-hover:text-indigo-600 dark:group-hover:text-indigo-400
                    transition-colors
                    line-clamp-2 mb-2
                  "
                  >
                    {item.headline}
                  </h4>

                  {/* Summary */}
                  <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2 mb-3">
                    {item.summary}
                  </p>

                  {/* Meta info */}
                  <div className="flex items-center gap-3 flex-wrap">
                    {/* Source */}
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                      {item.source}
                    </span>

                    {/* Date */}
                    <span className="text-xs text-slate-400 dark:text-slate-500">
                      {formatDate(item.date)}
                    </span>

                    {/* Relevance badge */}
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-medium ${relevanceColors[item.relevance]}`}
                    >
                      {item.relevance === 'high' && '🔥 '}
                      {item.relevance.charAt(0).toUpperCase() + item.relevance.slice(1)} relevance
                    </span>

                    {/* Category badge */}
                    {item.category && (
                      <span className="text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-full font-medium capitalize">
                        {item.category}
                      </span>
                    )}
                  </div>
                </div>

                {/* External link icon */}
                <ExternalLink
                  className="
                  w-5 h-5 flex-shrink-0
                  text-slate-400 dark:text-slate-500
                  group-hover:text-indigo-600 dark:group-hover:text-indigo-400
                  transition-colors
                "
                />
              </div>
            </a>
          ))
        )}

        {/* View more indicator */}
        {data.length > 0 && (
          <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-center gap-2 text-sm text-slate-500 dark:text-slate-400">
              <TrendingUp className="w-4 h-4" />
              <span>Click any article to read more</span>
            </div>
          </div>
        )}
      </div>
    </IntelligenceCard>
  );
}
