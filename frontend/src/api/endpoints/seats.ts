import { apiClient, type PaginatedResponse } from "../client";
import type { Seat, SeatCreate, SeatListParams, SeatUpdate } from "../../types/seat";

export const seatsApi = {
  async list(params: SeatListParams = {}) {
    const response = await apiClient.get<PaginatedResponse<Seat>>("/seats", {
      params,
    });
    return response.data;
  },

  async available(params: Pick<SeatListParams, "floor" | "zone"> & { limit?: number } = {}) {
    const response = await apiClient.get<Seat[]>("/seats/available", { params });
    return response.data;
  },

  async get(seatId: number) {
    const response = await apiClient.get<Seat>(`/seats/${seatId}`);
    return response.data;
  },

  async create(payload: SeatCreate) {
    const response = await apiClient.post<Seat>("/seats", payload);
    return response.data;
  },

  async update(seatId: number, payload: SeatUpdate) {
    const response = await apiClient.put<Seat>(`/seats/${seatId}`, payload);
    return response.data;
  },
};
