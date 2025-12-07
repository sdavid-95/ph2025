'use client';

import { cn } from '@/lib/utils';

type FilterType = 'all' | 'damaged';

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
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
          activeFilter === 'damaged'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
        )}
      >
        Damaged
      </button>
    </div>
  );
}

