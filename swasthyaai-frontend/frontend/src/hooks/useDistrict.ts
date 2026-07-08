import { useMutation, useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-client";
import type { CopilotQueryRequest, CopilotQueryResponse, DistrictOut, DistrictSummaryResponse } from "@/types/api";

export function useDistricts() {
  return useQuery({
    queryKey: ["districts"] as const,
    queryFn: () => apiClient.get<DistrictOut[]>("/district", { auth: false }),
    staleTime: 5 * 60_000,
  });
}

export function useDistrictSummary(districtId: number | undefined) {
  return useQuery({
    queryKey: queryKeys.districtSummary(districtId ?? -1),
    queryFn: () => apiClient.get<DistrictSummaryResponse>(`/district/${districtId}/summary`),
    enabled: districtId !== undefined,
    refetchInterval: 60_000,
  });
}

export function useCopilotQuery(districtId: number | undefined) {
  return useMutation({
    mutationFn: (payload: CopilotQueryRequest) => {
      if (districtId === undefined) throw new Error("No district selected.");
      return apiClient.post<CopilotQueryResponse>(`/district/${districtId}/copilot/query`, payload);
    },
  });
}
