'use client';

import { useState } from 'react';
import { SpeedBump, BumpStatus } from '@/types';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BumperActionModalProps {
  bump: SpeedBump | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (id: string, status: BumpStatus) => Promise<void>;
}

export function BumperActionModal({
  bump,
  isOpen,
  onClose,
  onUpdate,
}: BumperActionModalProps) {
  const [selectedStatus, setSelectedStatus] = useState<BumpStatus>(
    bump?.status || 'Good'
  );
  const [isUpdating, setIsUpdating] = useState(false);

  if (!isOpen || !bump) return null;

  const statusOptions: BumpStatus[] = ['Good', 'Damaged', 'Critical'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bump) return;

    setIsUpdating(true);
    try {
      await onUpdate(bump.id, selectedStatus);
      onClose();
    } catch (error) {
      console.error('Failed to update:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Update Status</h2>
          <button
            onClick={onClose}
            className={cn(
              'min-h-[60px] min-w-[60px] flex items-center justify-center rounded-lg',
              'bg-gray-100 hover:bg-gray-200 transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-blue-500'
            )}
            aria-label="Close modal"
          >
            <X className="w-6 h-6 text-gray-700" />
          </button>
        </div>

        <div className="mb-6">
          <p className="text-lg font-bold text-gray-900 mb-1">
            {bump.street_name}
          </p>
          {bump.exact_location && (
            <p className="text-sm text-gray-500 mb-2">{bump.exact_location}</p>
          )}
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-700">
              Cars Passed: {bump.car_count || 0}
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-900 mb-3">
              Status
            </label>
            <div className="space-y-2">
              {statusOptions.map((status) => (
                <button
                  key={status}
                  type="button"
                  onClick={() => setSelectedStatus(status)}
                  className={cn(
                    'w-full min-h-[60px] px-4 py-3 rounded-lg font-semibold text-lg transition-colors',
                    'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
                    selectedStatus === status
                      ? status === 'Good'
                        ? 'bg-green-500 text-white'
                        : status === 'Damaged'
                        ? 'bg-yellow-500 text-black'
                        : 'bg-red-600 text-white'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  )}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              className="flex-1"
              disabled={isUpdating}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={isUpdating}
            >
              {isUpdating ? 'Updating...' : 'Update Status'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

