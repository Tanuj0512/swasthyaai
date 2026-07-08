import { QueryClient } from "@tanstack/react-query";

import { ApiError } from "@/lib/api-client";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        // Don't retry client errors (bad request, auth, not found) — only
        // retry transient network/server errors, and only a couple of times.
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
          return false;
        }
        return failureCount < 2;
      },
      staleTime: 15_000,
      refetchOnWindowFocus: false,
    },
  },
});

/**
 * Centralized query keys so cache invalidation after a mutation (e.g.
 * logging medicine consumption) can target exactly the right queries
 * without every feature re-inventing its own key shape.
 */
export const queryKeys = {
  phcs: ["phcs"] as const,
  dashboard: (phcId: number) => ["dashboard", phcId] as const,
  inventoryForecast: (phcId: number) => ["inventory", "forecast", phcId] as const,
  inventoryRecommendations: (phcId: number) => ["inventory", "recommendations", phcId] as const,
  schemes: ["schemes"] as const,
  districtSummary: (districtId: number) => ["district", "summary", districtId] as const,
  currentStaff: ["auth", "currentStaff"] as const,
};
