export type BumpStatus = 'Good' | 'Damaged' | 'Critical';

export interface SpeedBump {
  id: string;
  street_name: string;
  exact_location: string;
  status: BumpStatus;
  last_updated: string;
  health: number;  // Health points (0-10000)
}

