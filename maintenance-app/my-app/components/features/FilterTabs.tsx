'use client';

import { cn } from '@/lib/utils';

type FilterType = 'all' | 'damaged' | 'critical';

interface FilterTabsProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
}

export function FilterTabs({ activeFilter, onFilterChange }: FilterTabsProps) {
  return (
    <div className="flex gap-2 mb-6">
      <button
        onClick={() => onFilterChange('all')}
        className={cn(
          'min-h-[60px] px-6 py-4 rounded-lg font-semibold text-lg transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
          activeFilter === 'all'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
        )}
      >
        All
      </button>
      <button
        onClick={() => onFilterChange('damaged')}
        className={cn(
          'min-h-[60px] px-6 py-4 rounded-lg font-semibold text-lg transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500',
          activeFilter === 'damaged'
            ? 'bg-yellow-500 text-black'
            : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
        )}
      >
        Damaged
      </button>
      <button
        onClick={() => onFilterChange('critical')}
        className={cn(
          'min-h-[60px] px-6 py-4 rounded-lg font-semibold text-lg transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500',
          activeFilter === 'critical'
            ? 'bg-red-600 text-white'
            : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
        )}
      >
        Critical
      </button>
    </div>
  );
}

