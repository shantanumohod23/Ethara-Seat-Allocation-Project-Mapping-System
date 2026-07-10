import { Route, Routes } from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import AllocationsPage from "../pages/AllocationsPage";
import DashboardPage from "../pages/DashboardPage";
import EmployeesPage from "../pages/EmployeesPage";
import ProjectsPage from "../pages/ProjectsPage";
import SeatsPage from "../pages/SeatsPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="/employees" element={<EmployeesPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/seats" element={<SeatsPage />} />
        <Route path="/allocation" element={<AllocationsPage />} />
        <Route path="/assistant" element={<DashboardPage assistantOnly />} />
      </Route>
    </Routes>
  );
}
