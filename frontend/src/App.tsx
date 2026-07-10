import { useEffect, useMemo, useState } from "react";

import { apiClient, type PaginatedResponse } from "./api/client";

type Summary = {
  total_employees: number;
  total_seats: number;
  occupied_seats: number;
  available_seats: number;
  reserved_seats: number;
  new_joiners_pending_allocation: number;
};

type Employee = {
  id: number;
  employee_code: string;
  email: string;
  first_name: string;
  last_name: string;
  department: string | null;
  job_title: string | null;
  employment_status: string;
  project_id: number | null;
};

type Seat = {
  id: number;
  floor: string;
  zone: string;
  bay: string;
  seat_number: string;
  status: string;
};

type ProjectUtilization = {
  project_id: number;
  project_name: string;
  occupied_seats: number;
};

type FloorUtilization = {
  floor: string;
  total_seats: number;
  occupied_seats: number;
  available_seats: number;
  reserved_seats: number;
  occupancy_percent: number;
};

const formatNumber = (value: number | undefined) =>
  new Intl.NumberFormat("en").format(value ?? 0);

export default function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [availableSeats, setAvailableSeats] = useState<Seat[]>([]);
  const [projectUtilization, setProjectUtilization] = useState<ProjectUtilization[]>([]);
  const [floorUtilization, setFloorUtilization] = useState<FloorUtilization[]>([]);
  const [search, setSearch] = useState("");
  const [assistantQuery, setAssistantQuery] = useState(
    "Where is employee Employee00001 seated?",
  );
  const [assistantAnswer, setAssistantAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true);
    setError(null);
    try {
      const [summaryResponse, employeeResponse, seatsResponse, projectResponse, floorResponse] =
        await Promise.all([
          apiClient.get<Summary>("/dashboard/summary"),
          apiClient.get<PaginatedResponse<Employee>>("/employees", {
            params: { page_size: 8, sort_by: "employee_code" },
          }),
          apiClient.get<Seat[]>("/seats/available", { params: { limit: 8 } }),
          apiClient.get<ProjectUtilization[]>("/dashboard/project-utilization"),
          apiClient.get<FloorUtilization[]>("/dashboard/floor-utilization"),
        ]);
      setSummary(summaryResponse.data);
      setEmployees(employeeResponse.data.items);
      setAvailableSeats(seatsResponse.data);
      setProjectUtilization(projectResponse.data.slice(0, 6));
      setFloorUtilization(floorResponse.data);
    } catch (caught) {
      setError("Unable to load dashboard data. Confirm the FastAPI backend is running.");
    } finally {
      setLoading(false);
    }
  }

  async function searchEmployees() {
    setError(null);
    try {
      const response = await apiClient.get<PaginatedResponse<Employee>>("/employees", {
        params: { search, page_size: 20 },
      });
      setEmployees(response.data.items);
    } catch {
      setError("Employee search failed.");
    }
  }

  async function askAssistant() {
    setAssistantAnswer("Thinking...");
    try {
      const response = await apiClient.post<{ answer: string; intent: string }>("/ai/query", {
        query: assistantQuery,
      });
      setAssistantAnswer(response.data.answer);
    } catch {
      setAssistantAnswer("Assistant request failed. Check the backend and try again.");
    }
  }

  const cards = useMemo(
    () => [
      ["Employees", summary?.total_employees],
      ["Total seats", summary?.total_seats],
      ["Occupied", summary?.occupied_seats],
      ["Available", summary?.available_seats],
      ["Reserved", summary?.reserved_seats],
      ["Pending new joiners", summary?.new_joiners_pending_allocation],
    ],
    [summary],
  );

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-cyan-700">
              Ethara workspace operations
            </p>
            <h1 className="mt-1 text-3xl font-semibold">
              Seat Allocation & Project Mapping
            </h1>
          </div>
          <button className="primary-button" onClick={loadDashboard}>
            Refresh data
          </button>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-6 py-6">
        {error ? <div className="mb-5 rounded border border-red-200 bg-red-50 p-3 text-red-800">{error}</div> : null}
        {loading ? <div className="mb-5 rounded border border-slate-200 bg-white p-4">Loading dashboard...</div> : null}

        <section className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
          {cards.map(([label, value]) => (
            <article className="metric-card" key={label}>
              <p className="text-sm text-slate-500">{label}</p>
              <p className="mt-2 text-2xl font-semibold">{formatNumber(value as number)}</p>
            </article>
          ))}
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-[1.4fr_1fr]">
          <div className="panel">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <h2 className="section-title">Employee Search</h2>
              <div className="flex gap-2">
                <input
                  className="input"
                  placeholder="Name, email, ID, department"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
                <button className="primary-button" onClick={searchEmployees}>
                  Search
                </button>
              </div>
            </div>
            <div className="mt-4 overflow-x-auto">
              <table>
                <thead>
                  <tr>
                    <th>Employee</th>
                    <th>Email</th>
                    <th>Department</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.map((employee) => (
                    <tr key={employee.id}>
                      <td>
                        <strong>{employee.first_name} {employee.last_name}</strong>
                        <span>{employee.employee_code}</span>
                      </td>
                      <td>{employee.email}</td>
                      <td>{employee.department ?? "Unassigned"}</td>
                      <td><span className="status-pill">{employee.employment_status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="panel">
            <h2 className="section-title">Assistant</h2>
            <textarea
              className="input mt-4 min-h-28"
              value={assistantQuery}
              onChange={(event) => setAssistantQuery(event.target.value)}
            />
            <button className="primary-button mt-3 w-full" onClick={askAssistant}>
              Ask
            </button>
            <p className="mt-4 rounded bg-slate-100 p-3 text-sm leading-6">
              {assistantAnswer || "Ask about employee seats, available seats, or project utilization."}
            </p>
          </div>
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <div className="panel">
            <h2 className="section-title">Available Seats</h2>
            <div className="mt-4 space-y-3">
              {availableSeats.map((seat) => (
                <div className="row-card" key={seat.id}>
                  <strong>Floor {seat.floor}, {seat.zone}</strong>
                  <span>{seat.bay} · Seat {seat.seat_number}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <h2 className="section-title">Project Allocation</h2>
            <div className="mt-4 space-y-3">
              {projectUtilization.map((project) => (
                <div className="row-card" key={project.project_id}>
                  <strong>{project.project_name}</strong>
                  <span>{formatNumber(project.occupied_seats)} occupied seats</span>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <h2 className="section-title">Floor Occupancy</h2>
            <div className="mt-4 space-y-3">
              {floorUtilization.map((floor) => (
                <div className="row-card" key={floor.floor}>
                  <strong>Floor {floor.floor}</strong>
                  <span>{floor.occupancy_percent}% occupied · {floor.available_seats} open</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
