import { Navigate } from "react-router-dom";

import { useAuth } from "@/features/auth/AuthContext";

/** Sends a freshly logged-in staff member to the most relevant page for
 * their role, rather than forcing everyone through the same default. */
export function AppIndexRedirect() {
  const { staff } = useAuth();

  if (!staff) return null;

  if (staff.role === "district_officer") {
    return <Navigate to="/app/district" replace />;
  }
  return <Navigate to="/app/dashboard" replace />;
}
