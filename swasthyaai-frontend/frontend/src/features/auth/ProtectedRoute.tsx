import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "@/features/auth/AuthContext";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { ErrorState } from "@/components/common/ErrorState";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { session, staff, isLoading, profileError } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingScreen label="Checking your session..." />;
  }

  if (!session) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (profileError) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-paper-50 p-6">
        <ErrorState
          title="Account not linked"
          description={profileError}
          className="max-w-md"
        />
      </div>
    );
  }

  if (!staff) {
    return <LoadingScreen label="Loading your profile..." />;
  }

  return <>{children}</>;
}
