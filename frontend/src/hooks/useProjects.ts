import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { projectsApi } from "../api/endpoints/projects";
import type { ProjectCreate, ProjectListParams, ProjectUpdate } from "../types/project";

export const projectKeys = {
  all: ["projects"] as const,
  lists: () => [...projectKeys.all, "list"] as const,
  list: (params: ProjectListParams) => [...projectKeys.lists(), params] as const,
  detail: (projectId: number) => [...projectKeys.all, "detail", projectId] as const,
  employees: (projectId: number) =>
    [...projectKeys.all, "employees", projectId] as const,
};

export function useProjects(params: ProjectListParams = {}) {
  return useQuery({
    queryKey: projectKeys.list(params),
    queryFn: () => projectsApi.list(params),
  });
}

export function useProject(projectId: number | null) {
  return useQuery({
    enabled: projectId !== null,
    queryKey: projectId === null ? projectKeys.all : projectKeys.detail(projectId),
    queryFn: () => projectsApi.get(projectId as number),
  });
}

export function useProjectEmployees(projectId: number | null) {
  return useQuery({
    enabled: projectId !== null,
    queryKey: projectId === null ? projectKeys.all : projectKeys.employees(projectId),
    queryFn: () => projectsApi.employees(projectId as number),
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectCreate) => projectsApi.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: projectKeys.all }),
  });
}

export function useUpdateProject(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ProjectUpdate) => projectsApi.update(projectId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: projectKeys.all }),
  });
}
