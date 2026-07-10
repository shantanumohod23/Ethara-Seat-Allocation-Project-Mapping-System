import { apiClient, type PaginatedResponse } from "../client";
import type {
  Employee,
  EmployeeCreate,
  EmployeeCsvImportResponse,
  EmployeeListParams,
  EmployeeUpdate,
} from "../../types/employee";

export const employeesApi = {
  async list(params: EmployeeListParams = {}) {
    const response = await apiClient.get<PaginatedResponse<Employee>>("/employees", {
      params,
    });
    return response.data;
  },

  async get(employeeId: number) {
    const response = await apiClient.get<Employee>(`/employees/${employeeId}`);
    return response.data;
  },

  async create(payload: EmployeeCreate) {
    const response = await apiClient.post<Employee>("/employees", payload);
    return response.data;
  },

  async update(employeeId: number, payload: EmployeeUpdate) {
    const response = await apiClient.put<Employee>(`/employees/${employeeId}`, payload);
    return response.data;
  },

  async remove(employeeId: number) {
    await apiClient.delete(`/employees/${employeeId}`);
  },

  async uploadCsv(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post<EmployeeCsvImportResponse>(
      "/employees/upload-csv",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return response.data;
  },
};
