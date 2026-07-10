import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/employees", label: "Employees" },
  { to: "/projects", label: "Projects" },
  { to: "/seats", label: "Seats" },
  { to: "/allocation", label: "Allocation" },
  { to: "/assistant", label: "AI Assistant" },
];

export function Sidebar() {
  return (
    <aside className="border-b border-slate-200 bg-white lg:min-h-screen lg:w-64 lg:border-b-0 lg:border-r">
      <div className="px-5 py-5">
        <p className="text-xs font-bold uppercase tracking-wide text-cyan-700">
          Ethara
        </p>
        <h1 className="mt-1 text-lg font-semibold text-slate-950">
          Seat Allocation
        </h1>
      </div>
      <nav className="flex gap-1 overflow-x-auto px-3 pb-3 lg:flex-col lg:overflow-visible">
        {navItems.map((item) => (
          <NavLink
            className={({ isActive }) =>
              [
                "whitespace-nowrap rounded-md px-3 py-2 text-sm font-semibold",
                isActive
                  ? "bg-cyan-700 text-white"
                  : "text-slate-700 hover:bg-slate-100",
              ].join(" ")
            }
            end={item.to === "/"}
            key={item.to}
            to={item.to}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
