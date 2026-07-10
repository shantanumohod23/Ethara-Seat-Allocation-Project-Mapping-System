import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { seatsApi } from "../api/endpoints/seats";
import type { SeatCreate, SeatListParams, SeatUpdate } from "../types/seat";

export const seatKeys = {
  all: ["seats"] as const,
  lists: () => [...seatKeys.all, "list"] as const,
  list: (params: SeatListParams) => [...seatKeys.lists(), params] as const,
  available: (params: Pick<SeatListParams, "floor" | "zone"> & { limit?: number }) =>
    [...seatKeys.all, "available", params] as const,
  detail: (seatId: number) => [...seatKeys.all, "detail", seatId] as const,
};

export function useSeats(params: SeatListParams = {}) {
  return useQuery({
    queryKey: seatKeys.list(params),
    queryFn: () => seatsApi.list(params),
  });
}

export function useAvailableSeats(
  params: Pick<SeatListParams, "floor" | "zone"> & { limit?: number } = {},
) {
  return useQuery({
    queryKey: seatKeys.available(params),
    queryFn: () => seatsApi.available(params),
  });
}

export function useSeat(seatId: number | null) {
  return useQuery({
    enabled: seatId !== null,
    queryKey: seatId === null ? seatKeys.all : seatKeys.detail(seatId),
    queryFn: () => seatsApi.get(seatId as number),
  });
}

export function useCreateSeat() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SeatCreate) => seatsApi.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: seatKeys.all }),
  });
}

export function useUpdateSeat(seatId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SeatUpdate) => seatsApi.update(seatId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: seatKeys.all }),
  });
}
