export type EmploymentStatus = "active" | "inactive" | "onboarding" | "resigned";

export type Employee = {
  id: number;
  employee_code: string;
  email: string;
  first_name: string;
  last_name: string;
  department: string | null;
  job_title: string | null;
  joining_date: string;
  employment_status: EmploymentStatus;
  project_id: number | null;
  created_at: string;
  updated_at: string;
};

export type EmployeeCreate = {
  employee_code: string;
  email: string;
  first_name: string;
  last_name: string;
  department?: string | null;
  job_title?: string | null;
  joining_date: string;
  employment_status?: EmploymentStatus;
  project_id?: number | null;
};

export type EmployeeUpdate = Partial<EmployeeCreate>;

export type EmployeeListParams = {
  page?: number;
  page_size?: number;
  include_inactive?: boolean;
  name?: string;
  email?: string;
  department?: string;
  status?: EmploymentStatus;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
};

export type EmployeeCsvImportError = {
  row: number;
  employee_code: string | null;
  email: string | null;
  error: string;
};

export type EmployeeCsvImportResponse = {
  created: number;
  failed: number;
  employees: Employee[];
  errors: EmployeeCsvImportError[];
};
