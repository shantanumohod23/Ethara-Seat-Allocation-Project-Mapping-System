import { apiClient, type PaginatedResponse } from "../client";
import type {
  Project,
  ProjectCreate,
  ProjectEmployee,
  ProjectListParams,
  ProjectUpdate,
} from "../../types/project";

export const projectsApi = {
  async list(params: ProjectListParams = {}) {
    const response = await apiClient.get<PaginatedResponse<Project>>("/projects", {
      params,
    });
    return response.data;
  },

  async create(payload: ProjectCreate) {
    const response = await apiClient.post<Project>("/projects", payload);
    return response.data;
  },

  async get(projectId: number) {
    const response = await apiClient.get<Project>(`/projects/${projectId}`);
    return response.data;
  },

  async update(projectId: number, payload: ProjectUpdate) {
    const response = await apiClient.put<Project>(`/projects/${projectId}`, payload);
    return response.data;
  },

  async employees(projectId: number) {
    const response = await apiClient.get<ProjectEmployee[]>(
      `/projects/${projectId}/employees`,
    );
    return response.data;
  },
};
