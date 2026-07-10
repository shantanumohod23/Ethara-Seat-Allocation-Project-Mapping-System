import { Outlet } from "react-router-dom";

import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 lg:flex">
      <Sidebar />
      <div className="min-w-0 flex-1">
        <Header />
        <Outlet />
      </div>
    </div>
  );
}
