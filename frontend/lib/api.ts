export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export type Run = {
  id: number;
  external_id: string;
  train_number: string;
  carrier: string;
  route_name: string | null;
  service_date: string;
  latest_delay_minutes: number;
};

export type LeaderboardRow = {
  user_id: number;
  username: string;
  balance: number;
};
