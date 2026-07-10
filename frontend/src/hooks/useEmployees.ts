import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { employeesApi } from "../api/endpoints/employees";
import type {
  EmployeeCreate,
  EmployeeListParams,
  EmployeeUpdate,
} from "../types/employee";

export const employeeKeys = {
  all: ["employees"] as const,
  lists: () => [...employeeKeys.all, "list"] as const,
  list: (params: EmployeeListParams) => [...employeeKeys.lists(), params] as const,
  detail: (employeeId: number) => [...employeeKeys.all, "detail", employeeId] as const,
};

export function useEmployees(params: EmployeeListParams = {}) {
  return useQuery({
    queryKey: employeeKeys.list(params),
    queryFn: () => employeesApi.list(params),
  });
}

export function useEmployee(employeeId: number | null) {
  return useQuery({
    enabled: employeeId !== null,
    queryKey: employeeId === null ? employeeKeys.all : employeeKeys.detail(employeeId),
    queryFn: () => employeesApi.get(employeeId as number),
  });
}

export function useCreateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: EmployeeCreate) => employeesApi.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: employeeKeys.all }),
  });
}

export function useUpdateEmployee(employeeId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: EmployeeUpdate) => employeesApi.update(employeeId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: employeeKeys.all }),
  });
}

export function useDeleteEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (employeeId: number) => employeesApi.remove(employeeId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: employeeKeys.all }),
  });
}

export function useUploadEmployeesCsv() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => employeesApi.uploadCsv(file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: employeeKeys.all }),
  });
}
