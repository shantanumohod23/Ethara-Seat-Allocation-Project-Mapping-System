import { useMemo, useState } from "react";
import type { Dispatch, FormEvent, SetStateAction } from "react";

import { useCreateSeat, useSeats, useUpdateSeat } from "../hooks/useSeats";
import type { Seat, SeatCreate, SeatStatus } from "../types/seat";

const emptySeat: SeatCreate = {
  floor: "",
  zone: "",
  bay: "",
  seat_number: "",
  status: "available",
};

export default function SeatsPage() {
  const [status, setStatus] = useState<SeatStatus | "">("");
  const [floor, setFloor] = useState("");
  const [selectedSeat, setSelectedSeat] = useState<Seat | null>(null);
  const [form, setForm] = useState<SeatCreate>(emptySeat);
  const [editForm, setEditForm] = useState<SeatCreate>(emptySeat);

  const params = useMemo(
    () => ({
      page: 1,
      page_size: 40,
      floor: floor || undefined,
      status: status || undefined,
    }),
    [floor, status],
  );
  const seatsQuery = useSeats(params);
  const createSeat = useCreateSeat();
  const updateSeat = useUpdateSeat(selectedSeat?.id ?? 0);
  const seats = seatsQuery.data?.items ?? [];

  function selectSeat(seat: Seat) {
    setSelectedSeat(seat);
    setEditForm({
      floor: seat.floor,
      zone: seat.zone,
      bay: seat.bay,
      seat_number: seat.seat_number,
      status: seat.status,
    });
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await createSeat.mutateAsync(normalizeSeat(form));
    setForm(emptySeat);
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedSeat) {
      return;
    }
    await updateSeat.mutateAsync(normalizeSeat(editForm));
  }

  async function setSelectedStatus(nextStatus: SeatStatus) {
    if (!selectedSeat) {
      return;
    }
    await updateSeat.mutateAsync({ status: nextStatus });
    setSelectedSeat({ ...selectedSeat, status: nextStatus });
    setEditForm((current) => ({ ...current, status: nextStatus }));
  }

  return (
    <main className="mx-auto max-w-7xl px-6 py-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-cyan-700">
            Seat inventory
          </p>
          <h1 className="text-2xl font-semibold text-slate-950">Seats</h1>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            className="input sm:w-32"
            placeholder="Floor"
            value={floor}
            onChange={(event) => setFloor(event.target.value)}
          />
          <select
            className="input sm:w-44"
            value={status}
            onChange={(event) => setStatus(event.target.value as SeatStatus | "")}
          >
            <option value="">All statuses</option>
            <option value="available">Available</option>
            <option value="occupied">Occupied</option>
            <option value="reserved">Reserved</option>
            <option value="maintenance">Maintenance</option>
          </select>
        </div>
      </div>

      <section className="mt-6 grid gap-6 xl:grid-cols-[1.35fr_0.9fr]">
        <div className="panel">
          <div className="flex items-center justify-between">
            <h2 className="section-title">Seat Directory</h2>
            <span className="text-sm text-slate-500">
              {seatsQuery.data?.total ?? 0} seats
            </span>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table>
              <thead>
                <tr>
                  <th>Seat</th>
                  <th>Floor</th>
                  <th>Zone</th>
                  <th>Bay</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {seats.map((seat) => (
                  <tr
                    className="cursor-pointer hover:bg-slate-50"
                    key={seat.id}
                    onClick={() => selectSeat(seat)}
                  >
                    <td>
                      <strong>{seat.seat_number}</strong>
                      <span>ID {seat.id}</span>
                    </td>
                    <td>{seat.floor}</td>
                    <td>{seat.zone}</td>
                    <td>{seat.bay}</td>
                    <td>
                      <span className="status-pill">{seat.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="space-y-6">
          <form className="panel" onSubmit={handleCreate}>
            <h2 className="section-title">Create Seat</h2>
            <SeatFields form={form} setForm={setForm} />
            <button className="primary-button mt-4 w-full" disabled={createSeat.isPending}>
              {createSeat.isPending ? "Creating..." : "Create seat"}
            </button>
          </form>

          <form className="panel" onSubmit={handleUpdate}>
            <div className="flex items-center justify-between">
              <h2 className="section-title">Update Seat</h2>
              {selectedSeat ? (
                <span className="status-pill">{selectedSeat.status}</span>
              ) : null}
            </div>
            {selectedSeat ? (
              <>
                <SeatFields form={editForm} setForm={setEditForm} />
                <button className="primary-button mt-4 w-full" disabled={updateSeat.isPending}>
                  {updateSeat.isPending ? "Saving..." : "Save changes"}
                </button>
                <div className="mt-3 grid gap-2 sm:grid-cols-3">
                  <button
                    className="secondary-button"
                    onClick={() => void setSelectedStatus("reserved")}
                    type="button"
                  >
                    Reserve
                  </button>
                  <button
                    className="secondary-button"
                    onClick={() => void setSelectedStatus("maintenance")}
                    type="button"
                  >
                    Maintenance
                  </button>
                  <button
                    className="secondary-button"
                    onClick={() => void setSelectedStatus("available")}
                    type="button"
                  >
                    Release
                  </button>
                </div>
              </>
            ) : (
              <p className="mt-4 text-sm text-slate-500">
                Select a seat to update, reserve, mark maintenance, or release.
              </p>
            )}
          </form>
        </aside>
      </section>
    </main>
  );
}

function SeatFields({
  form,
  setForm,
}: {
  form: SeatCreate;
  setForm: Dispatch<SetStateAction<SeatCreate>>;
}) {
  return (
    <div className="mt-4 grid gap-3 sm:grid-cols-2">
      <input
        className="input"
        placeholder="Floor"
        required
        value={form.floor}
        onChange={(event) => setForm((current) => ({ ...current, floor: event.target.value }))}
      />
      <input
        className="input"
        placeholder="Zone"
        required
        value={form.zone}
        onChange={(event) => setForm((current) => ({ ...current, zone: event.target.value }))}
      />
      <input
        className="input"
        placeholder="Bay"
        required
        value={form.bay}
        onChange={(event) => setForm((current) => ({ ...current, bay: event.target.value }))}
      />
      <input
        className="input"
        placeholder="Seat number"
        required
        value={form.seat_number}
        onChange={(event) =>
          setForm((current) => ({ ...current, seat_number: event.target.value }))
        }
      />
      <select
        className="input sm:col-span-2"
        value={form.status ?? "available"}
        onChange={(event) =>
          setForm((current) => ({ ...current, status: event.target.value as SeatStatus }))
        }
      >
        <option value="available">Available</option>
        <option value="reserved">Reserved</option>
        <option value="maintenance">Maintenance</option>
        <option value="occupied">Occupied</option>
      </select>
    </div>
  );
}

function normalizeSeat(seat: SeatCreate): SeatCreate {
  return {
    ...seat,
    floor: seat.floor.trim(),
    zone: seat.zone.trim(),
    bay: seat.bay.trim(),
    seat_number: seat.seat_number.trim(),
  };
}
