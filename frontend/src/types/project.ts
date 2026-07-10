export type ProjectStatus = "active" | "inactive" | "completed";

export type Project = {
  id: number;
  project_code: string;
  name: string;
  description: string | null;
  manager_name: string | null;
  status: ProjectStatus;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectCreate = {
  project_code: string;
  name: string;
  description?: string | null;
  manager_name?: string | null;
  status?: ProjectStatus;
  start_date?: string | null;
  end_date?: string | null;
};

export type ProjectUpdate = Partial<ProjectCreate>;

export type ProjectEmployee = {
  id: number;
  employee_code: string;
  name: string;
  email: string;
  department: string | null;
  employment_status: string;
};

export type ProjectListParams = {
  page?: number;
  page_size?: number;
  search?: string;
  status?: ProjectStatus;
  sort_order?: "asc" | "desc";
};
