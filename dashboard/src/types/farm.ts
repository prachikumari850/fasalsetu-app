export interface FarmBoundary {
  id: string;
  farm_id: string;
  coordinates: number[][];
  center_lat: number;
  center_lng: number;
  geojson: string;
}

export interface Farm {
  id: string;
  owner_id: string;
  name: string;
  village: string;
  taluka: string | null;
  district: string;
  state: string;
  area_acres: number;
  crop_type: string;
  season: string;
  khasra_number: string | null;
  is_active: boolean;
  boundary: FarmBoundary | null;
  created_at: string;
}