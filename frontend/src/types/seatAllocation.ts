import type { Seat } from "./seat";

export type AllocationStatus = "active" | "released" | "cancelled";

export type SeatAllocation = {
  id: number;
  employee_id: number;
  seat_id: number;
  project_id: number;
  status: AllocationStatus;
  allocated_at: string;
  released_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type SeatAllocationCreate = {
  employee_id: number;
  seat_id: number;
  project_id?: number | null;
  notes?: string | null;
};

export type SeatAllocationRelease = {
  allocation_id?: number | null;
  employee_id?: number | null;
  seat_id?: number | null;
  notes?: string | null;
};

export type SeatAllocationListParams = {
  page?: number;
  page_size?: number;
  employee_id?: number;
  seat_id?: number;
  project_id?: number;
  status?: AllocationStatus;
};

export type SeatSuggestion = {
  seat: Pick<Seat, "id" | "floor" | "zone" | "bay" | "seat_number" | "status">;
  score: number;
  reason: string;
};
