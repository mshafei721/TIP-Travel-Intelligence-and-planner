'use client';

import {
  UtensilsCrossed,
  ChefHat,
  Leaf,
  Flame,
  DollarSign,
  MapPin,
  AlertTriangle,
  ExternalLink,
  ShoppingBag,
} from 'lucide-react';
import IntelligenceCard from './IntelligenceCard';
import type { FoodInfo, LocalDish, MealPriceRange } from '@/types/destination';

interface FoodCardProps {
  data: FoodInfo;
  isExpanded?: boolean;
  isLoading?: boolean;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
  onLinkClick?: (url: string, title: string) => void;
}

const SpicyIndicator = ({ level }: { level?: 'mild' | 'medium' | 'hot' | 'very-hot' }) => {
  if (!level) return null;

  const spicyConfig = {
    mild: { flames: 1, color: 'text-orange-400' },
    medium: { flames: 2, color: 'text-orange-500' },
    hot: { flames: 3, color: 'text-orange-600' },
    'very-hot': { flames: 4, color: 'text-red-600' },
  };

  const config = spicyConfig[level];

  return (
    <div className="flex items-center gap-0.5" title={`${level} spicy`}>
      {Array.from({ length: config.flames }).map((_, i) => (
        <Flame key={i} className={`w-3 h-3 ${config.color} fill-current`} />
      ))}
    </div>
  );
};

const PriceLevelIndicator = ({ level }: { level: '$' | '$$' | '$$$' | '$$$$' }) => {
  return <span className="text-xs font-bold text-green-600 dark:text-green-400">{level}</span>;
};

const DietaryBadge = ({ label, available }: { label: string; available: boolean }) => {
  return (
    <div
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
        available
          ? 'bg-green-100 dark:bg-green-950/40 text-green-700 dark:text-green-300 border border-green-300 dark:border-green-800'
          : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
      }`}
    >
      {available && <Leaf className="w-3 h-3" />}
      {label}
    </div>
  );
};

const AvailabilityBadge = ({ level }: { level: 'widespread' | 'common' | 'limited' | 'rare' }) => {
  const config = {
    widespread: {
      label: 'Widespread',
      color:
        'bg-green-100 dark:bg-green-950/40 text-green-700 dark:text-green-300 border-green-300 dark:border-green-800',
    },
    common: {
      label: 'Common',
      color:
        'bg-blue-100 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-800',
    },
    limited: {
      label: 'Limited',
      color:
        'bg-amber-100 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-800',
    },
    rare: {
      label: 'Rare',
      color:
        'bg-red-100 dark:bg-red-950/40 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800',
    },
  };

  const { label, color } = config[level];

  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium border ${color}`}>
      {label}
    </span>
  );
};

const SafetyRatingBadge = ({ rating }: { rating: 'excellent' | 'good' | 'fair' | 'poor' }) => {
  const config = {
    excellent: {
      label: 'Excellent',
      color:
        'bg-green-100 dark:bg-green-950/40 text-green-700 dark:text-green-300 border-green-300 dark:border-green-800',
    },
    good: {
      label: 'Good',
      color:
        'bg-blue-100 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-800',
    },
    fair: {
      label: 'Fair',
      color:
        'bg-amber-100 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-800',
    },
    poor: {
      label: 'Poor',
      color:
        'bg-red-100 dark:bg-red-950/40 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800',
    },
  };

  const { label, color } = config[rating];

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border ${color}`}
    >
      {label}
    </span>
  );
};

export default function FoodCard({
  data,
  isExpanded,
  isLoading,
  onExpand,
  onCollapse,
  onLinkClick,
}: FoodCardProps) {
  const renderDish = (dish: LocalDish, index: number) => {
    const dishTypeColors = {
      main: 'border-orange-300 dark:border-orange-800 bg-orange-50 dark:bg-orange-950/20',
      appetizer: 'border-amber-300 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/20',
      dessert: 'border-pink-300 dark:border-pink-800 bg-pink-50 dark:bg-pink-950/20',
      beverage: 'border-blue-300 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/20',
      snack: 'border-purple-300 dark:border-purple-800 bg-purple-50 dark:bg-purple-950/20',
    };

    return (
      <div key={index} className={`p-4 border rounded-lg ${dishTypeColors[dish.type]}`}>
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex-1">
            <h4 className="font-semibold text-slate-900 dark:text-slate-50 mb-1">{dish.name}</h4>
            <p className="text-sm text-slate-600 dark:text-slate-400 capitalize">{dish.type}</p>
          </div>
          <div className="flex flex-col items-end gap-1">
            {dish.spicyLevel && <SpicyIndicator level={dish.spicyLevel} />}
            <div className="flex gap-1">
              {dish.isVegetarian && <DietaryBadge label="Veg" available={true} />}
              {dish.isVegan && <DietaryBadge label="Vegan" available={true} />}
            </div>
          </div>
        </div>
        <p className="text-sm text-slate-700 dark:text-slate-300 mb-2">{dish.description}</p>
        {dish.commonIngredients && dish.commonIngredients.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {dish.commonIngredients.map((ingredient, i) => (
              <span
                key={i}
                className="px-2 py-0.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full text-xs text-slate-600 dark:text-slate-400"
              >
                {ingredient}
              </span>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderPriceRange = (range: MealPriceRange, index: number) => {
    const typeLabels = {
      'street-food': 'Street Food',
      'casual-dining': 'Casual Dining',
      'mid-range': 'Mid-Range',
      'fine-dining': 'Fine Dining',
    };

    return (
      <div
        key={index}
        className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
      >
        <div className="flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-green-600 dark:text-green-400" />
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            {typeLabels[range.mealType]}
          </span>
        </div>
        <div className="text-right">
          <div className="text-sm font-bold text-slate-900 dark:text-slate-50">
            {range.priceRange.currency} {range.priceRange.min} - {range.priceRange.max}
          </div>
          {range.description && (
            <div className="text-xs text-slate-500 dark:text-slate-400">{range.description}</div>
          )}
        </div>
      </div>
    );
  };

  return (
    <IntelligenceCard
      id="food"
      title="Food & Dining"
      icon={<UtensilsCrossed className="w-6 h-6" />}
      iconColor="text-orange-600 dark:text-orange-400"
      isExpanded={isExpanded}
      isLoading={isLoading}
      onExpand={onExpand}
      onCollapse={onCollapse}
    >
      <div className="space-y-6">
        {/* Must-try dishes */}
        {data.mustTryDishes.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <ChefHat className="w-5 h-5 text-orange-600 dark:text-orange-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-50 uppercase tracking-wide">
                Must-Try Local Dishes
              </h3>
            </div>
            <div className="grid grid-cols-1 gap-3">{data.mustTryDishes.map(renderDish)}</div>
          </div>
        )}

        {/* Street food */}
        {data.streetFood.popular.length > 0 && (
          <div className="p-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <ShoppingBag className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                <h3 className="text-sm font-semibold text-amber-900 dark:text-amber-100 uppercase tracking-wide">
                  Street Food
                </h3>
              </div>
              <SafetyRatingBadge rating={data.streetFood.safetyRating} />
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-xs font-medium text-amber-700 dark:text-amber-300 mb-2">
                  Popular items:
                </p>
                <ul className="space-y-1">
                  {data.streetFood.popular.map((item, idx) => (
                    <li
                      key={idx}
                      className="flex items-start gap-2 text-sm text-amber-900 dark:text-amber-100"
                    >
                      <span className="flex-shrink-0 w-1.5 h-1.5 bg-amber-500 rounded-full mt-2" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              {data.streetFood.bestLocations && data.streetFood.bestLocations.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-amber-700 dark:text-amber-300 mb-2">
                    Best locations:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {data.streetFood.bestLocations.map((location, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-amber-100 dark:bg-amber-900/50 border border-amber-300 dark:border-amber-700 rounded-lg text-xs text-amber-900 dark:text-amber-100"
                      >
                        <MapPin className="w-3 h-3" />
                        {location}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {data.streetFood.tips.length > 0 && (
                <div className="pt-2 border-t border-amber-200 dark:border-amber-800">
                  <p className="text-xs font-medium text-amber-700 dark:text-amber-300 mb-1">
                    Tips:
                  </p>
                  <ul className="space-y-1">
                    {data.streetFood.tips.map((tip, idx) => (
                      <li key={idx} className="text-xs text-amber-800 dark:text-amber-200">
                        • {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Dining etiquette */}
        {data.diningEtiquette.length > 0 && (
          <div className="p-4 bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-lg">
            <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100 uppercase tracking-wide mb-3">
              Dining Etiquette
            </h3>
            <ul className="space-y-2">
              {data.diningEtiquette.map((rule, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-2 text-sm text-purple-900 dark:text-purple-100"
                >
                  <span className="flex-shrink-0 w-1.5 h-1.5 bg-purple-500 rounded-full mt-2" />
                  {rule}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Dietary options */}
        <div className="p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <Leaf className="w-5 h-5 text-green-600 dark:text-green-400" />
            <h3 className="text-sm font-semibold text-green-900 dark:text-green-100 uppercase tracking-wide">
              Dietary Options
            </h3>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div>
              <p className="text-xs text-green-700 dark:text-green-300 mb-1">Vegetarian</p>
              <AvailabilityBadge level={data.dietaryOptions.vegetarian} />
            </div>
            <div>
              <p className="text-xs text-green-700 dark:text-green-300 mb-1">Vegan</p>
              <AvailabilityBadge level={data.dietaryOptions.vegan} />
            </div>
            <div>
              <p className="text-xs text-green-700 dark:text-green-300 mb-1">Halal</p>
              <AvailabilityBadge level={data.dietaryOptions.halal} />
            </div>
            <div>
              <p className="text-xs text-green-700 dark:text-green-300 mb-1">Kosher</p>
              <AvailabilityBadge level={data.dietaryOptions.kosher} />
            </div>
            <div>
              <p className="text-xs text-green-700 dark:text-green-300 mb-1">Gluten-Free</p>
              <AvailabilityBadge level={data.dietaryOptions.glutenFree} />
            </div>
          </div>
          {data.dietaryOptions.notes && (
            <p className="mt-3 pt-3 border-t border-green-200 dark:border-green-800 text-xs text-green-800 dark:text-green-200">
              {data.dietaryOptions.notes}
            </p>
          )}
        </div>

        {/* Price ranges */}
        {data.priceRanges.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-50 uppercase tracking-wide mb-3">
              Price Ranges
            </h3>
            <div className="space-y-2">{data.priceRanges.map(renderPriceRange)}</div>
          </div>
        )}

        {/* Recommendations */}
        {data.recommendations.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-50 uppercase tracking-wide mb-3">
              Recommended Places
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {data.recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-lg"
                >
                  <div className="flex items-start justify-between mb-1">
                    <h4 className="font-semibold text-sm text-slate-900 dark:text-slate-50">
                      {rec.name}
                    </h4>
                    <PriceLevelIndicator level={rec.priceLevel} />
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 capitalize mb-1">
                    {rec.type}
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mb-2">{rec.specialty}</p>
                  {rec.location && (
                    <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                      <MapPin className="w-3 h-3" />
                      {rec.location}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Safety tips */}
        {data.safetyTips.length > 0 && (
          <div className="p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
              <h3 className="text-sm font-semibold text-red-900 dark:text-red-100 uppercase tracking-wide">
                Food Safety Tips
              </h3>
            </div>
            <ul className="space-y-2">
              {data.safetyTips.map((tip, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-2 text-sm text-red-900 dark:text-red-100"
                >
                  <span className="flex-shrink-0 text-red-600 dark:text-red-400 mt-0.5">⚠</span>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Food guides */}
        {data.foodGuides && data.foodGuides.length > 0 && (
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
              Food Guides
            </p>
            <div className="flex flex-wrap gap-2">
              {data.foodGuides.map((link, idx) => (
                <a
                  key={idx}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => onLinkClick?.(link.url, link.title)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-800 text-orange-700 dark:text-orange-300 text-sm font-medium rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/50 transition-colors"
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
