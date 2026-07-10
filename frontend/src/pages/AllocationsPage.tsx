import { useMemo, useState } from "react";

import {
  useAllocateSeat,
  useReleaseSeat,
  useSeatAllocations,
  useSeatSuggestions,
} from "../hooks/useSeatAllocations";
import { useEmployees } from "../hooks/useEmployees";
import { useProjects } from "../hooks/useProjects";
import { useAvailableSeats, useSeats } from "../hooks/useSeats";
import type { Employee } from "../types/employee";

export default function AllocationsPage() {
  const [search, setSearch] = useState("");
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null);
  const [selectedSeatId, setSelectedSeatId] = useState<number | null>(null);
  const [preferredFloor, setPreferredFloor] = useState("");
  const [notes, setNotes] = useState("");

  const employeesQuery = useEmployees({
    page_size: 50,
    search: search || undefined,
    status: undefined,
    sort_by: "employee_code",
  });
  const projectsQuery = useProjects({ page_size: 100 });
  const availableSeatsQuery = useAvailableSeats({
    floor: preferredFloor || undefined,
    limit: 50,
  });
  const seatsQuery = useSeats({ page_size: 100 });
  const suggestionsQuery = useSeatSuggestions(selectedEmployeeId, 5);
  const allocationsQuery = useSeatAllocations({
    page_size: 20,
    status: "active",
  });
  const allocateSeat = useAllocateSeat();
  const releaseSeat = useReleaseSeat();

  const employees = employeesQuery.data?.items ?? [];
  const projects = projectsQuery.data?.items ?? [];
  const availableSeats = availableSeatsQuery.data ?? [];
  const seats = seatsQuery.data?.items ?? [];
  const allocations = allocationsQuery.data?.items ?? [];
  const selectedEmployee = useMemo(
    () => employees.find((employee) => employee.id === selectedEmployeeId) ?? null,
    [employees, selectedEmployeeId],
  );

  async function allocateSelected() {
    if (!selectedEmployeeId || !selectedSeatId) {
      return;
    }
    await allocateSeat.mutateAsync({
      employee_id: selectedEmployeeId,
      seat_id: selectedSeatId,
      project_id: selectedEmployee?.project_id ?? null,
      notes: notes || "Allocated from allocation screen.",
    });
    setSelectedSeatId(null);
    setNotes("");
  }

  async function releaseAllocation(allocationId: number) {
    await releaseSeat.mutateAsync({
      allocation_id: allocationId,
      notes: "Released from allocation screen.",
    });
  }

  return (
    <main className="mx-auto max-w-7xl px-6 py-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-cyan-700">
            Seat assignment
          </p>
          <h1 className="text-2xl font-semibold text-slate-950">
            Allocation & New Joiners
          </h1>
        </div>
        <input
          className="input md:max-w-sm"
          placeholder="Search employee or new joiner"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      <section className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <div className="panel">
          <h2 className="section-title">Employee</h2>
          <div className="mt-4 grid gap-3">
            {employees.slice(0, 10).map((employee) => (
              <button
                className={[
                  "row-card text-left",
                  selectedEmployeeId === employee.id ? "border-cyan-600 bg-cyan-50" : "",
                ].join(" ")}
                key={employee.id}
                onClick={() => setSelectedEmployeeId(employee.id)}
                type="button"
              >
                <strong>
                  {employee.first_name} {employee.last_name}
                </strong>
                <span>
                  {employee.employee_code} - {employee.employment_status} -{" "}
                  {projectName(employee, projects)}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2 className="section-title">Suggested Seats</h2>
          {selectedEmployee ? (
            <p className="mt-2 text-sm text-slate-500">
              Suggestions for {selectedEmployee.first_name} {selectedEmployee.last_name}.
            </p>
          ) : (
            <p className="mt-2 text-sm text-slate-500">
              Select an employee to get project-aware recommendations.
            </p>
          )}
          <div className="mt-4 grid gap-3">
            {(suggestionsQuery.data ?? []).map((suggestion) => (
              <button
                className={[
                  "row-card text-left",
                  selectedSeatId === suggestion.seat.id ? "border-cyan-600 bg-cyan-50" : "",
                ].join(" ")}
                key={suggestion.seat.id}
                onClick={() => setSelectedSeatId(suggestion.seat.id)}
                type="button"
              >
                <strong>
                  Floor {suggestion.seat.floor}, {suggestion.seat.zone},{" "}
                  {suggestion.seat.bay}, Seat {suggestion.seat.seat_number}
                </strong>
                <span>
                  Score {suggestion.score} - {suggestion.reason}
                </span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="panel">
          <h2 className="section-title">Allocate</h2>
          <div className="mt-4 space-y-3">
            <input
              className="input"
              placeholder="Preferred floor"
              value={preferredFloor}
              onChange={(event) => setPreferredFloor(event.target.value)}
            />
            <select
              className="input"
              value={selectedSeatId ?? ""}
              onChange={(event) =>
                setSelectedSeatId(event.target.value ? Number(event.target.value) : null)
              }
            >
              <option value="">Choose available seat</option>
              {availableSeats.map((seat) => (
                <option key={seat.id} value={seat.id}>
                  Floor {seat.floor}, {seat.zone}, {seat.bay}, {seat.seat_number}
                </option>
              ))}
            </select>
            <textarea
              className="input min-h-24"
              placeholder="Notes"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
            <button
              className="primary-button w-full disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={!selectedEmployeeId || !selectedSeatId || allocateSeat.isPending}
              onClick={() => void allocateSelected()}
              type="button"
            >
              {allocateSeat.isPending ? "Allocating..." : "Allocate"}
            </button>
          </div>
        </div>

        <div className="panel">
          <h2 className="section-title">Active Allocations</h2>
          <div className="mt-4 overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Allocation</th>
                  <th>Employee</th>
                  <th>Seat</th>
                  <th>Project</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {allocations.map((allocation) => (
                  <tr key={allocation.id}>
                    <td>
                      <strong>#{allocation.id}</strong>
                      <span>{new Date(allocation.allocated_at).toLocaleDateString()}</span>
                    </td>
                    <td>{employeeLabel(allocation.employee_id, employees)}</td>
                    <td>{seatLabel(allocation.seat_id, seats)}</td>
                    <td>{projects.find((project) => project.id === allocation.project_id)?.name ?? allocation.project_id}</td>
                    <td>
                      <button
                        className="secondary-button"
                        onClick={() => void releaseAllocation(allocation.id)}
                        type="button"
                      >
                        Release
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}

function projectName(employee: Employee, projects: { id: number; name: string }[]) {
  return (
    projects.find((project) => project.id === employee.project_id)?.name ??
    "No project"
  );
}

function employeeLabel(employeeId: number, employees: Employee[]) {
  const employee = employees.find((item) => item.id === employeeId);
  if (!employee) {
    return `Employee ${employeeId}`;
  }
  return `${employee.first_name} ${employee.last_name}`;
}

function seatLabel(
  seatId: number,
  seats: { id: number; floor: string; zone: string; bay: string; seat_number: string }[],
) {
  const seat = seats.find((item) => item.id === seatId);
  if (!seat) {
    return `Seat ${seatId}`;
  }
  return `F${seat.floor} ${seat.zone} ${seat.bay} ${seat.seat_number}`;
}
