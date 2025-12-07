'use client';

import { useState, useEffect } from 'react';
import { SpeedBump, BumpStatus } from '@/types';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BumperActionModalProps {
  bump: SpeedBump | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (id: string, health: number) => Promise<void>;
}

export function BumperActionModal({
  bump,
  isOpen,
  onClose,
  onUpdate,
}: BumperActionModalProps) {
  const getStatusFromHealth = (health: number): BumpStatus => {
    if (health >= 7000) return 'Good';
    if (health >= 3000) return 'Damaged';
    return 'Critical';
  };

  const [healthValue, setHealthValue] = useState<number>(10000);
  const [isUpdating, setIsUpdating] = useState(false);

  // Update health value when bump changes or modal opens
  useEffect(() => {
    if (bump) {
      setHealthValue(bump.health || 10000);
    }
  }, [bump, isOpen]);

  if (!isOpen || !bump) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bump) return;

    // Validate health is between 0 and 10000
    if (healthValue < 0 || healthValue > 10000) {
      alert('Health must be between 0 and 10000');
      return;
    }

    setIsUpdating(true);
    try {
      await onUpdate(bump.id, healthValue);
      onClose();
    } catch (error) {
      console.error('Failed to update:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const currentStatus = getStatusFromHealth(healthValue);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Update Health</h2>
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
          <div className="mt-2 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700">
              <span className="font-semibold">Current Health:</span> {bump.health || 10000}
            </p>
            <p className="text-sm text-gray-700 mt-1">
              <span className="font-semibold">New Status:</span>{' '}
              <span
                className={cn(
                  'font-bold',
                  currentStatus === 'Good'
                    ? 'text-green-600'
                    : currentStatus === 'Damaged'
                    ? 'text-yellow-600'
                    : 'text-red-600'
                )}
              >
                {currentStatus}
              </span>
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-900 mb-3">
              Health Value (0 - 10000)
            </label>
            <Input
              type="number"
              min="0"
              max="10000"
              value={healthValue}
              onChange={(e) => setHealthValue(parseInt(e.target.value) || 0)}
              className="w-full"
              required
            />
            <p className="text-xs text-gray-500 mt-2">
              Health ranges: Good (≥7000), Damaged (3000-6999), Critical (&lt;3000)
            </p>
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
              {isUpdating ? 'Updating...' : 'Update Health'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

