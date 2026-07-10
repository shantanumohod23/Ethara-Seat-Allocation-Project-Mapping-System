import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { seatAllocationsApi } from "../api/endpoints/seatAllocations";
import { employeeKeys } from "./useEmployees";
import { seatKeys } from "./useSeats";
import type {
  SeatAllocationCreate,
  SeatAllocationListParams,
  SeatAllocationRelease,
} from "../types/seatAllocation";

export const allocationKeys = {
  all: ["allocations"] as const,
  lists: () => [...allocationKeys.all, "list"] as const,
  list: (params: SeatAllocationListParams) => [...allocationKeys.lists(), params] as const,
  suggestions: (employeeId: number, limit: number) =>
    [...allocationKeys.all, "suggestions", employeeId, limit] as const,
};

export function useSeatAllocations(params: SeatAllocationListParams = {}) {
  return useQuery({
    queryKey: allocationKeys.list(params),
    queryFn: () => seatAllocationsApi.list(params),
  });
}

export function useSeatSuggestions(employeeId: number | null, limit = 5) {
  return useQuery({
    enabled: employeeId !== null,
    queryKey:
      employeeId === null
        ? allocationKeys.all
        : allocationKeys.suggestions(employeeId, limit),
    queryFn: () => seatAllocationsApi.suggestions(employeeId as number, limit),
  });
}

function invalidateAllocationData(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: allocationKeys.all });
  void queryClient.invalidateQueries({ queryKey: seatKeys.all });
  void queryClient.invalidateQueries({ queryKey: employeeKeys.all });
}

export function useAllocateSeat() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SeatAllocationCreate) => seatAllocationsApi.allocate(payload),
    onSuccess: () => invalidateAllocationData(queryClient),
  });
}

export function useReleaseSeat() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SeatAllocationRelease) => seatAllocationsApi.release(payload),
    onSuccess: () => invalidateAllocationData(queryClient),
  });
}
