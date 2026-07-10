import { useMemo, useState } from "react";
import type { ChangeEvent, Dispatch, FormEvent, SetStateAction } from "react";

import {
  useCreateEmployee,
  useDeleteEmployee,
  useEmployees,
  useUpdateEmployee,
  useUploadEmployeesCsv,
} from "../hooks/useEmployees";
import { useProjects } from "../hooks/useProjects";
import type {
  Employee,
  EmployeeCreate,
  EmploymentStatus,
} from "../types/employee";

const today = new Date().toISOString().slice(0, 10);

const emptyEmployee: EmployeeCreate = {
  employee_code: "",
  email: "",
  first_name: "",
  last_name: "",
  department: "",
  job_title: "",
  joining_date: today,
  employment_status: "active",
  project_id: null,
};

export default function EmployeesPage() {
  const [search, setSearch] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [form, setForm] = useState<EmployeeCreate>(emptyEmployee);
  const [editForm, setEditForm] = useState<EmployeeCreate>(emptyEmployee);

  const employeeParams = useMemo(
    () => ({
      page: 1,
      page_size: 30,
      search: search || undefined,
      include_inactive: true,
      sort_by: "employee_code",
    }),
    [search],
  );
  const employeesQuery = useEmployees(employeeParams);
  const projectsQuery = useProjects({ page_size: 100, status: "active" });
  const createEmployee = useCreateEmployee();
  const updateEmployee = useUpdateEmployee(selectedEmployee?.id ?? 0);
  const deleteEmployee = useDeleteEmployee();
  const uploadEmployeesCsv = useUploadEmployeesCsv();

  const employees = employeesQuery.data?.items ?? [];
  const projects = projectsQuery.data?.items ?? [];

  function selectEmployee(employee: Employee) {
    setSelectedEmployee(employee);
    setEditForm({
      employee_code: employee.employee_code,
      email: employee.email,
      first_name: employee.first_name,
      last_name: employee.last_name,
      department: employee.department ?? "",
      job_title: employee.job_title ?? "",
      joining_date: employee.joining_date,
      employment_status: employee.employment_status,
      project_id: employee.project_id,
    });
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await createEmployee.mutateAsync(normalizeEmployee(form));
    setForm(emptyEmployee);
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedEmployee) {
      return;
    }
    await updateEmployee.mutateAsync(normalizeEmployee(editForm));
  }

  async function handleDelete() {
    if (!selectedEmployee) {
      return;
    }
    await deleteEmployee.mutateAsync(selectedEmployee.id);
    setSelectedEmployee(null);
  }

  async function handleCsvUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    await uploadEmployeesCsv.mutateAsync(file);
    event.target.value = "";
  }

  return (
    <main className="mx-auto max-w-7xl px-6 py-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-cyan-700">
            People directory
          </p>
          <h1 className="text-2xl font-semibold text-slate-950">Employees</h1>
        </div>
        <input
          className="input md:max-w-sm"
          placeholder="Search employees"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      <section className="mt-6 grid gap-6 xl:grid-cols-[1.25fr_0.95fr]">
        <div className="panel">
          <div className="flex items-center justify-between">
            <h2 className="section-title">Employee Directory</h2>
            <span className="text-sm text-slate-500">
              {employeesQuery.data?.total ?? 0} employees
            </span>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Email</th>
                  <th>Department</th>
                  <th>Project</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((employee) => (
                  <tr
                    className="cursor-pointer hover:bg-slate-50"
                    key={employee.id}
                    onClick={() => selectEmployee(employee)}
                  >
                    <td>
                      <strong>
                        {employee.first_name} {employee.last_name}
                      </strong>
                      <span>{employee.employee_code}</span>
                    </td>
                    <td>{employee.email}</td>
                    <td>{employee.department ?? "Unassigned"}</td>
                    <td>{projectName(employee.project_id, projects)}</td>
                    <td>
                      <span className="status-pill">{employee.employment_status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="space-y-6">
          <form className="panel" onSubmit={handleCreate}>
            <h2 className="section-title">Add Employee</h2>
            <EmployeeFields
              form={form}
              projects={projects}
              setForm={setForm}
            />
            <button className="primary-button mt-4 w-full" disabled={createEmployee.isPending}>
              {createEmployee.isPending ? "Adding..." : "Add employee"}
            </button>
          </form>

          <div className="panel">
            <h2 className="section-title">Upload Employees CSV</h2>
            <p className="mt-2 text-sm text-slate-500">
              Import employee_code, email, first_name, last_name, joining_date,
              department, job_title, employment_status, and project_id.
            </p>
            <input
              accept=".csv,text/csv"
              className="input mt-4"
              disabled={uploadEmployeesCsv.isPending}
              onChange={(event) => void handleCsvUpload(event)}
              type="file"
            />
            {uploadEmployeesCsv.data ? (
              <div className="mt-3 rounded border border-slate-200 bg-slate-50 p-3 text-sm">
                <strong>{uploadEmployeesCsv.data.created} created</strong>
                <span className="block text-slate-600">
                  {uploadEmployeesCsv.data.failed} failed
                </span>
                {uploadEmployeesCsv.data.errors.slice(0, 3).map((error) => (
                  <span className="mt-2 block text-red-700" key={error.row}>
                    Row {error.row}: {error.error}
                  </span>
                ))}
              </div>
            ) : null}
          </div>

          <form className="panel" onSubmit={handleUpdate}>
            <div className="flex items-center justify-between gap-3">
              <h2 className="section-title">View / Edit Employee</h2>
              {selectedEmployee ? (
                <span className="status-pill">{selectedEmployee.employee_code}</span>
              ) : null}
            </div>
            {selectedEmployee ? (
              <>
                <EmployeeFields
                  form={editForm}
                  projects={projects}
                  setForm={setEditForm}
                />
                <div className="mt-4 grid gap-2 sm:grid-cols-2">
                  <button className="primary-button" disabled={updateEmployee.isPending}>
                    {updateEmployee.isPending ? "Saving..." : "Save changes"}
                  </button>
                  <button
                    className="secondary-button"
                    disabled={deleteEmployee.isPending}
                    onClick={handleDelete}
                    type="button"
                  >
                    {deleteEmployee.isPending ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </>
            ) : (
              <p className="mt-4 text-sm text-slate-500">
                Select an employee to view, edit, or deactivate the record.
              </p>
            )}
          </form>
        </aside>
      </section>
    </main>
  );
}

function EmployeeFields({
  form,
  projects,
  setForm,
}: {
  form: EmployeeCreate;
  projects: { id: number; name: string }[];
  setForm: Dispatch<SetStateAction<EmployeeCreate>>;
}) {
  return (
    <div className="mt-4 grid gap-3 sm:grid-cols-2">
      <input
        className="input"
        placeholder="Employee code"
        required
        value={form.employee_code}
        onChange={(event) =>
          setForm((current) => ({ ...current, employee_code: event.target.value }))
        }
      />
      <input
        className="input"
        placeholder="Email"
        required
        type="email"
        value={form.email}
        onChange={(event) =>
          setForm((current) => ({ ...current, email: event.target.value }))
        }
      />
      <input
        className="input"
        placeholder="First name"
        required
        value={form.first_name}
        onChange={(event) =>
          setForm((current) => ({ ...current, first_name: event.target.value }))
        }
      />
      <input
        className="input"
        placeholder="Last name"
        required
        value={form.last_name}
        onChange={(event) =>
          setForm((current) => ({ ...current, last_name: event.target.value }))
        }
      />
      <input
        className="input"
        placeholder="Department"
        value={form.department ?? ""}
        onChange={(event) =>
          setForm((current) => ({ ...current, department: event.target.value }))
        }
      />
      <input
        className="input"
        placeholder="Job title"
        value={form.job_title ?? ""}
        onChange={(event) =>
          setForm((current) => ({ ...current, job_title: event.target.value }))
        }
      />
      <input
        className="input"
        required
        type="date"
        value={form.joining_date}
        onChange={(event) =>
          setForm((current) => ({ ...current, joining_date: event.target.value }))
        }
      />
      <select
        className="input"
        value={form.employment_status ?? "active"}
        onChange={(event) =>
          setForm((current) => ({
            ...current,
            employment_status: event.target.value as EmploymentStatus,
          }))
        }
      >
        <option value="active">Active</option>
        <option value="onboarding">Onboarding</option>
        <option value="inactive">Inactive</option>
        <option value="resigned">Resigned</option>
      </select>
      <select
        className="input sm:col-span-2"
        value={form.project_id ?? ""}
        onChange={(event) =>
          setForm((current) => ({
            ...current,
            project_id: event.target.value ? Number(event.target.value) : null,
          }))
        }
      >
        <option value="">No project</option>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>
            {project.name}
          </option>
        ))}
      </select>
    </div>
  );
}

function normalizeEmployee(employee: EmployeeCreate): EmployeeCreate {
  return {
    ...employee,
    employee_code: employee.employee_code.trim(),
    email: employee.email.trim(),
    first_name: employee.first_name.trim(),
    last_name: employee.last_name.trim(),
    department: employee.department?.trim() || null,
    job_title: employee.job_title?.trim() || null,
    project_id: employee.project_id || null,
  };
}

function projectName(projectId: number | null, projects: { id: number; name: string }[]) {
  if (!projectId) {
    return "Unassigned";
  }
  return projects.find((project) => project.id === projectId)?.name ?? `Project ${projectId}`;
}
