import { useMemo, useState } from "react";
import type { FormEvent } from "react";

import {
  useCreateProject,
  useProjectEmployees,
  useProjects,
  useUpdateProject,
} from "../hooks/useProjects";
import type {
  Project,
  ProjectCreate,
  ProjectStatus,
  ProjectUpdate,
} from "../types/project";

const emptyProject: ProjectCreate = {
  project_code: "",
  name: "",
  description: "",
  manager_name: "",
  status: "active",
  start_date: null,
  end_date: null,
};

export default function ProjectsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<ProjectStatus | "">("");
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [form, setForm] = useState<ProjectCreate>(emptyProject);
  const [editForm, setEditForm] = useState<ProjectUpdate>({});

  const params = useMemo(
    () => ({
      page: 1,
      page_size: 25,
      search: search || undefined,
      status: status || undefined,
      sort_order: "asc" as const,
    }),
    [search, status],
  );

  const projectsQuery = useProjects(params);
  const employeesQuery = useProjectEmployees(selectedProjectId);
  const createProject = useCreateProject();
  const updateProject = useUpdateProject(selectedProjectId ?? 0);

  const projects = projectsQuery.data?.items ?? [];
  const selectedProject =
    projects.find((project) => project.id === selectedProjectId) ?? null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload: ProjectCreate = {
      ...form,
      project_code: form.project_code.trim(),
      name: form.name.trim(),
      description: form.description?.trim() || null,
      manager_name: form.manager_name?.trim() || null,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
    };
    await createProject.mutateAsync(payload);
    setForm(emptyProject);
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedProjectId) {
      return;
    }
    await updateProject.mutateAsync(normalizeProjectPayload(editForm));
  }

  function selectProject(project: Project) {
    setSelectedProjectId(project.id);
    setEditForm({
      project_code: project.project_code,
      name: project.name,
      description: project.description ?? "",
      manager_name: project.manager_name ?? "",
      status: project.status,
      start_date: project.start_date,
      end_date: project.end_date,
    });
  }

  return (
    <main className="mx-auto max-w-7xl px-6 py-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-cyan-700">
            Project mapping
          </p>
          <h1 className="text-2xl font-semibold text-slate-950">Projects</h1>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            className="input"
            placeholder="Search project, code, manager"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <select
            className="input sm:w-44"
            value={status}
            onChange={(event) => setStatus(event.target.value as ProjectStatus | "")}
          >
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      <section className="mt-6 grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
        <div className="panel">
          <div className="flex items-center justify-between">
            <h2 className="section-title">Project Directory</h2>
            <span className="text-sm text-slate-500">
              {projectsQuery.data?.total ?? 0} projects
            </span>
          </div>

          {projectsQuery.isLoading ? (
            <p className="mt-4 text-sm text-slate-500">Loading projects...</p>
          ) : null}
          {projectsQuery.isError ? (
            <p className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800">
              Project list could not be loaded.
            </p>
          ) : null}

          <div className="mt-4 overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Manager</th>
                  <th>Status</th>
                  <th>Dates</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project) => (
                  <tr
                    className="cursor-pointer hover:bg-slate-50"
                    key={project.id}
                    onClick={() => selectProject(project)}
                  >
                    <td>
                      <strong>{project.name}</strong>
                      <span>{project.project_code}</span>
                    </td>
                    <td>{project.manager_name ?? "Unassigned"}</td>
                    <td>
                      <span className="status-pill">{project.status}</span>
                    </td>
                    <td>{formatDates(project)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="space-y-6">
          <form className="panel" onSubmit={handleUpdate}>
            <div className="flex items-center justify-between gap-3">
              <h2 className="section-title">Edit Project</h2>
              {selectedProject ? (
                <span className="status-pill">{selectedProject.status}</span>
              ) : null}
            </div>
            {selectedProject ? (
              <div className="mt-4 space-y-3">
                <input
                  className="input"
                  placeholder="Project code"
                  required
                  value={editForm.project_code ?? ""}
                  onChange={(event) =>
                    setEditForm((current) => ({
                      ...current,
                      project_code: event.target.value,
                    }))
                  }
                />
                <input
                  className="input"
                  placeholder="Project name"
                  required
                  value={editForm.name ?? ""}
                  onChange={(event) =>
                    setEditForm((current) => ({
                      ...current,
                      name: event.target.value,
                    }))
                  }
                />
                <input
                  className="input"
                  placeholder="Manager name"
                  value={editForm.manager_name ?? ""}
                  onChange={(event) =>
                    setEditForm((current) => ({
                      ...current,
                      manager_name: event.target.value,
                    }))
                  }
                />
                <select
                  className="input"
                  value={editForm.status ?? "active"}
                  onChange={(event) =>
                    setEditForm((current) => ({
                      ...current,
                      status: event.target.value as ProjectStatus,
                    }))
                  }
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="completed">Completed</option>
                </select>
                <textarea
                  className="input min-h-24"
                  placeholder="Description"
                  value={editForm.description ?? ""}
                  onChange={(event) =>
                    setEditForm((current) => ({
                      ...current,
                      description: event.target.value,
                    }))
                  }
                />
                <button
                  className="primary-button w-full disabled:cursor-not-allowed disabled:bg-slate-300"
                  disabled={updateProject.isPending}
                  type="submit"
                >
                  {updateProject.isPending ? "Saving..." : "Save changes"}
                </button>
                {updateProject.isError ? (
                  <p className="text-sm text-red-700">Project update failed.</p>
                ) : null}
              </div>
            ) : (
              <p className="mt-4 text-sm text-slate-500">
                Select a project from the directory to edit its details.
              </p>
            )}
          </form>

          <form className="panel" onSubmit={handleSubmit}>
            <h2 className="section-title">Create Project</h2>
            <div className="mt-4 space-y-3">
              <input
                className="input"
                placeholder="Project code"
                required
                value={form.project_code}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    project_code: event.target.value,
                  }))
                }
              />
              <input
                className="input"
                placeholder="Project name"
                required
                value={form.name}
                onChange={(event) =>
                  setForm((current) => ({ ...current, name: event.target.value }))
                }
              />
              <input
                className="input"
                placeholder="Manager name"
                value={form.manager_name ?? ""}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    manager_name: event.target.value,
                  }))
                }
              />
              <textarea
                className="input min-h-24"
                placeholder="Description"
                value={form.description ?? ""}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    description: event.target.value,
                  }))
                }
              />
              <button
                className="primary-button w-full disabled:cursor-not-allowed disabled:bg-slate-300"
                disabled={createProject.isPending}
                type="submit"
              >
                {createProject.isPending ? "Creating..." : "Create project"}
              </button>
              {createProject.isError ? (
                <p className="text-sm text-red-700">Project creation failed.</p>
              ) : null}
            </div>
          </form>

          <div className="panel">
            <h2 className="section-title">Project Employees</h2>
            {selectedProject ? (
              <p className="mt-2 text-sm text-slate-500">
                Showing employees mapped to {selectedProject.name}.
              </p>
            ) : (
              <p className="mt-2 text-sm text-slate-500">
                Select a project to preview mapped employees.
              </p>
            )}
            <div className="mt-4 space-y-3">
              {(employeesQuery.data ?? []).slice(0, 8).map((employee) => (
                <div className="row-card" key={employee.id}>
                  <strong>{employee.name}</strong>
                  <span>
                    {employee.employee_code} - {employee.email}
                  </span>
                </div>
              ))}
              {employeesQuery.isLoading ? (
                <p className="text-sm text-slate-500">Loading employees...</p>
              ) : null}
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}

function normalizeProjectPayload(project: ProjectUpdate): ProjectUpdate {
  return {
    ...project,
    project_code: project.project_code?.trim(),
    name: project.name?.trim(),
    description: project.description?.trim() || null,
    manager_name: project.manager_name?.trim() || null,
    start_date: project.start_date || null,
    end_date: project.end_date || null,
  };
}

function formatDates(project: Project) {
  if (!project.start_date && !project.end_date) {
    return "Not set";
  }
  return `${project.start_date ?? "TBD"} - ${project.end_date ?? "Present"}`;
}
