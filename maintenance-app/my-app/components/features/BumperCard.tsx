'use client';

import { SpeedBump } from '@/types';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Card } from '@/components/ui/Card';
import { Edit } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BumperCardProps {
  bump: SpeedBump;
  onEdit: (bump: SpeedBump) => void;
}

export function BumperCard({ bump, onEdit }: BumperCardProps) {
  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  // Automatically determine status based on health
  const getStatusFromHealth = (health: number): 'Good' | 'Damaged' | 'Critical' => {
    if (health >= 7000) return 'Good';
    if (health >= 3000) return 'Damaged';
    return 'Critical';
  };

  const currentHealth = bump.health || 10000;
  const currentStatus = getStatusFromHealth(currentHealth);

  return (
    <Card className="min-h-[60px] py-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-gray-900 mb-1">
            {bump.street_name}
          </h3>
          {bump.exact_location && (
            <p className="text-sm text-gray-500 mb-2">{bump.exact_location}</p>
          )}
          <div className="flex items-center gap-2 flex-wrap">
            <StatusBadge status={currentStatus} />
            <span className="text-sm font-semibold text-gray-700">
              Health: {Math.round(currentHealth)}
            </span>
            <span className="text-xs text-gray-400">
              Updated: {formatDateTime(bump.last_updated)}
            </span>
          </div>
          {/* Health bar visualization */}
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                currentHealth >= 7000
                  ? 'bg-green-500'
                  : currentHealth >= 3000
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${Math.max(0, Math.min(100, (currentHealth / 10000) * 100))}%` }}
            />
          </div>
        </div>
        <button
          onClick={() => onEdit(bump)}
          className={cn(
            'min-h-[60px] min-w-[60px] flex items-center justify-center rounded-lg',
            'bg-gray-100 hover:bg-gray-200 transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          )}
          aria-label="Edit speed bump"
        >
          <Edit className="w-6 h-6 text-gray-700" />
        </button>
      </div>
    </Card>
  );
}

