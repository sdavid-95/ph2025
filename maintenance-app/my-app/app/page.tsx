'use client';

import { useState, useEffect } from 'react';
import { SpeedBump, BumpStatus } from '@/types';
import { supabase } from '@/lib/supabase';
import { FilterTabs } from '@/components/features/FilterTabs';
import { BumperList } from '@/components/features/BumperList';
import { BumperActionModal } from '@/components/features/BumperActionModal';
import { toast } from 'sonner';

export default function Home() {
  const [activeFilter, setActiveFilter] = useState<'all' | 'damaged' | 'critical'>('all');
  const [selectedBump, setSelectedBump] = useState<SpeedBump | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Auto-refresh every 5 seconds to get updates from Python script
  useEffect(() => {
    const interval = setInterval(() => {
      setRefreshTrigger((prev) => prev + 1);
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleEdit = (bump: SpeedBump) => {
    setSelectedBump(bump);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedBump(null);
  };

  const handleUpdate = async (id: string, health: number) => {
    try {
      // Calculate status based on health
      const getStatusFromHealth = (health: number): BumpStatus => {
        if (health >= 7000) return 'Good';
        if (health >= 3000) return 'Damaged';
        return 'Critical';
      };

      const newStatus = getStatusFromHealth(health);

      const { error } = await supabase
        .from('speed_bumps')
        .update({
          health: health,
          status: newStatus,
          last_updated: new Date().toISOString(),
        })
        .eq('id', id);

      if (error) {
        throw error;
      }

      toast.success('Health Updated!');
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update health';
      toast.error(`Error: ${errorMessage}`);
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Speed Bump Tracker
          </h1>
          <p className="text-lg text-gray-600">
            Track and manage speed bump maintenance status
          </p>
        </header>

        <FilterTabs
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
        />

        <BumperList
          filter={activeFilter}
          onEdit={handleEdit}
          refreshTrigger={refreshTrigger}
        />

        <BumperActionModal
          bump={selectedBump}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onUpdate={handleUpdate}
        />
      </div>
    </div>
  );
}
