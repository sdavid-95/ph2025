'use client';

import { useEffect, useState } from 'react';
import { SpeedBump, BumpStatus } from '@/types';
import { supabase } from '@/lib/supabase';
import { BumperCard } from './BumperCard';
import { Loader2 } from 'lucide-react';

interface BumperListProps {
  filter: 'all' | 'damaged';
  onEdit: (bump: SpeedBump) => void;
  refreshTrigger: number;
}

export function BumperList({
  filter,
  onEdit,
  refreshTrigger,
}: BumperListProps) {
  const [bumps, setBumps] = useState<SpeedBump[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBumps = async () => {
      setLoading(true);
      setError(null);

      try {
        let query = supabase
          .from('speed_bumps')
          .select('*')
          .order('last_updated', { ascending: false });

        if (filter === 'damaged') {
          query = query.in('status', ['Damaged', 'Critical']);
        }

        const { data, error: fetchError } = await query;

        if (fetchError) {
          throw fetchError;
        }

        setBumps(data || []);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to fetch speed bumps'
        );
        console.error('Error fetching bumps:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchBumps();
  }, [filter, refreshTrigger]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-lg text-gray-600">Loading...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 font-semibold">Error: {error}</p>
      </div>
    );
  }

  if (bumps.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-gray-600">
          {filter === 'damaged'
            ? 'No damaged speed bumps found.'
            : 'No speed bumps found.'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {bumps.map((bump) => (
        <BumperCard key={bump.id} bump={bump} onEdit={onEdit} />
      ))}
    </div>
  );
}

