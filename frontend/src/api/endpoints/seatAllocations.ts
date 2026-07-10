import { apiClient, type PaginatedResponse } from "../client";
import type {
  SeatAllocation,
  SeatAllocationCreate,
  SeatAllocationListParams,
  SeatAllocationRelease,
  SeatSuggestion,
} from "../../types/seatAllocation";

export const seatAllocationsApi = {
  async list(params: SeatAllocationListParams = {}) {
    const response = await apiClient.get<PaginatedResponse<SeatAllocation>>(
      "/seats/allocations",
      { params },
    );
    return response.data;
  },

  async allocate(payload: SeatAllocationCreate) {
    const response = await apiClient.post<SeatAllocation>("/seats/allocate", payload);
    return response.data;
  },

  async release(payload: SeatAllocationRelease) {
    const response = await apiClient.post<SeatAllocation>("/seats/release", payload);
    return response.data;
  },

  async suggestions(employeeId: number, limit = 5) {
    const response = await apiClient.get<SeatSuggestion[]>(
      `/seats/suggestions/${employeeId}`,
      { params: { limit } },
    );
    return response.data;
  },
};
