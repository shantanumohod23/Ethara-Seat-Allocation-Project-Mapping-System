export type SeatStatus = "available" | "occupied" | "reserved" | "maintenance";

export type Seat = {
  id: number;
  floor: string;
  zone: string;
  bay: string;
  seat_number: string;
  status: SeatStatus;
  created_at: string;
  updated_at: string;
};

export type SeatCreate = {
  floor: string;
  zone: string;
  bay: string;
  seat_number: string;
  status?: SeatStatus;
};

export type SeatUpdate = Partial<SeatCreate>;

export type SeatListParams = {
  page?: number;
  page_size?: number;
  floor?: string;
  zone?: string;
  bay?: string;
  status?: SeatStatus;
  sort_order?: "asc" | "desc";
};
