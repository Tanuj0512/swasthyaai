import type { ReactNode } from "react";

import { useAuth } from "@/features/auth/AuthContext";
import { ErrorState } from "@/components/common/ErrorState";
import type { StaffRole } from "@/types/api";

export function RoleGuard({ allow, children }: { allow: StaffRole[]; children: ReactNode }) {
  const { staff } = useAuth();

  if (!staff || !allow.includes(staff.role)) {
    return (
      <div className="flex flex-1 items-center justify-center p-6">
        <ErrorState
          title="You don't have access to this page"
          description="This section is restricted to specific staff roles. If you believe this is a mistake, contact your district administrator."
          className="max-w-md"
        />
      </div>
    );
  }

  return <>{children}</>;
}
