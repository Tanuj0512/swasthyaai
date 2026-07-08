import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-client";
import type { DashboardSnapshot, PHCOut } from "@/types/api";

export function usePHCs() {
  return useQuery({
    queryKey: queryKeys.phcs,
    queryFn: () => apiClient.get<PHCOut[]>("/phcs", { auth: false }),
  });
}

export function useDashboard(phcId: number | undefined) {
  return useQuery({
    queryKey: queryKeys.dashboard(phcId ?? -1),
    queryFn: () => apiClient.get<DashboardSnapshot>(`/phcs/${phcId}/dashboard`),
    enabled: phcId !== undefined,
    refetchInterval: 60_000,
  });
}
