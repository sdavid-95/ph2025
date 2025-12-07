import { SpeedBump } from '@/types';

// Mutable store for mock data (for testing purposes)
let mockSpeedBumpsStore: SpeedBump[] = [
  {
    id: '1',
    street_name: 'Main Street',
    exact_location: 'Between 1st and 2nd Avenue, near the intersection',
    status: 'Good',
    last_updated: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
  },
  {
    id: '2',
    street_name: 'Oak Avenue',
    exact_location: 'In front of City Park entrance',
    status: 'Damaged',
    last_updated: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
  },
  {
    id: '3',
    street_name: 'Elm Street',
    exact_location: 'Near the school zone, 200 meters from crosswalk',
    status: 'Critical',
    last_updated: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
  },
  {
    id: '4',
    street_name: 'Park Boulevard',
    exact_location: 'Adjacent to the shopping center parking lot',
    status: 'Good',
    last_updated: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
  },
  {
    id: '5',
    street_name: 'Cedar Lane',
    exact_location: 'Between Maple Drive and Pine Street',
    status: 'Damaged',
    last_updated: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
  },
  {
    id: '6',
    street_name: 'River Road',
    exact_location: 'Near the bridge approach, west side',
    status: 'Good',
    last_updated: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), // 10 days ago
  },
  {
    id: '7',
    street_name: 'Hill Street',
    exact_location: 'At the bottom of the hill, residential area',
    status: 'Critical',
    last_updated: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
  },
  {
    id: '8',
    street_name: 'Sunset Drive',
    exact_location: 'Near the community center',
    status: 'Good',
    last_updated: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1 hour ago
  },
];

export function getMockSpeedBumps(): SpeedBump[] {
  return [...mockSpeedBumpsStore];
}

export function updateMockSpeedBump(id: string, status: SpeedBump['status']): void {
  mockSpeedBumpsStore = mockSpeedBumpsStore.map((bump) =>
    bump.id === id
      ? { ...bump, status, last_updated: new Date().toISOString() }
      : bump
  );
}

