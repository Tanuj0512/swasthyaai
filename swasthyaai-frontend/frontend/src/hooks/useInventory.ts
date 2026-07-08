import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-client";
import type { ConsumptionLogRequest, InventoryForecastResponse, InventoryRecommendationResponse } from "@/types/api";

export function useInventoryForecast(phcId: number | undefined) {
  return useQuery({
    queryKey: queryKeys.inventoryForecast(phcId ?? -1),
    queryFn: () => apiClient.get<InventoryForecastResponse>(`/inventory/${phcId}/forecast`),
    enabled: phcId !== undefined,
  });
}

export function useInventoryRecommendations(phcId: number | undefined) {
  return useQuery({
    queryKey: queryKeys.inventoryRecommendations(phcId ?? -1),
    queryFn: () => apiClient.get<InventoryRecommendationResponse>(`/inventory/${phcId}/recommendations`),
    enabled: phcId !== undefined,
    staleTime: 30_000,
  });
}

export function useLogConsumption(phcId: number | undefined) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ConsumptionLogRequest) => {
      if (phcId === undefined) throw new Error("No PHC selected.");
      return apiClient.post<void>(`/inventory/${phcId}/consumption`, payload);
    },
    onSuccess: () => {
      if (phcId === undefined) return;
      queryClient.invalidateQueries({ queryKey: queryKeys.inventoryForecast(phcId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.inventoryRecommendations(phcId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard(phcId) });
    },
  });
}
