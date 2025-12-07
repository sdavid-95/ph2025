import { BumpStatus } from '@/types';
import { cn } from '@/lib/utils';

const STATUS_CONFIG = {
  Good: 'bg-green-500 text-white',
  Damaged: 'bg-yellow-500 text-black',
  Critical: 'bg-red-600 text-white',
};

interface StatusBadgeProps {
  status: BumpStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'px-4 py-2 rounded-full font-semibold text-sm',
        STATUS_CONFIG[status],
        className
      )}
    >
      {status}
    </span>
  );
}

