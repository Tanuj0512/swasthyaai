import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";

import { queryClient } from "@/lib/query-client";
import { AuthProvider } from "@/features/auth/AuthContext";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";
import { RoleGuard } from "@/features/auth/RoleGuard";
import { LoginPage } from "@/features/auth/LoginPage";
import { AppIndexRedirect } from "@/features/auth/AppIndexRedirect";
import { PublicShell } from "@/components/layout/PublicShell";
import { StaffShell } from "@/components/layout/StaffShell";
import { CitizenHomePage } from "@/features/janmitra/CitizenHomePage";
import { SchemesPage } from "@/features/janmitra/SchemesPage";
import { StaffEligibilityPage } from "@/features/janmitra/StaffEligibilityPage";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { InventoryPage } from "@/features/inventory/InventoryPage";
import { DistrictCopilotPage } from "@/features/district/DistrictCopilotPage";
import { NotFoundPage } from "@/features/NotFoundPage";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public / citizen-facing */}
            <Route element={<PublicShell />}>
              <Route path="/" element={<CitizenHomePage />} />
              <Route path="/schemes" element={<SchemesPage />} />
            </Route>

            <Route path="/login" element={<LoginPage />} />

            {/* Staff / district / admin — requires Supabase auth */}
            <Route
              path="/app"
              element={
                <ProtectedRoute>
                  <StaffShell />
                </ProtectedRoute>
              }
            >
              <Route index element={<AppIndexRedirect />} />
              <Route
                path="dashboard"
                element={
                  <RoleGuard allow={["phc_staff", "admin"]}>
                    <DashboardPage />
                  </RoleGuard>
                }
              />
              <Route
                path="inventory"
                element={
                  <RoleGuard allow={["phc_staff", "admin"]}>
                    <InventoryPage />
                  </RoleGuard>
                }
              />
              <Route
                path="janmitra"
                element={
                  <RoleGuard allow={["phc_staff", "district_officer", "admin"]}>
                    <StaffEligibilityPage />
                  </RoleGuard>
                }
              />
              <Route
                path="district"
                element={
                  <RoleGuard allow={["district_officer", "admin"]}>
                    <DistrictCopilotPage />
                  </RoleGuard>
                }
              />
            </Route>

            <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </BrowserRouter>
        <Toaster richColors position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  );
}
