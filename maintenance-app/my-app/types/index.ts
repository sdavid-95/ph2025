export type BumpStatus = 'Good' | 'Damaged' | 'Critical';

export interface SpeedBump {
  id: string;
  street_name: string;
  exact_location: string;
  status: BumpStatus;
  last_updated: string;
  car_count: number;
}

