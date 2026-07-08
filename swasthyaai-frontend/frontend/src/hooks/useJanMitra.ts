import { useMutation, useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-client";
import type {
  CitizenQueryRequest,
  CitizenQueryResponse,
  EligibilityCheckRequest,
  EligibilityCheckResponse,
  ExtractProfileRequest,
  ExtractProfileResponse,
  SchemeOut,
} from "@/types/api";

export function useSchemes() {
  return useQuery({
    queryKey: queryKeys.schemes,
    queryFn: () => apiClient.get<SchemeOut[]>("/schemes", { auth: false }),
    staleTime: 5 * 60_000,
  });
}

export function useCitizenQuery() {
  return useMutation({
    mutationFn: (payload: CitizenQueryRequest) =>
      apiClient.post<CitizenQueryResponse>("/janmitra/citizen/query", payload, { auth: false }),
  });
}

export function useExtractProfile() {
  return useMutation({
    mutationFn: (payload: ExtractProfileRequest) =>
      apiClient.post<ExtractProfileResponse>("/janmitra/eligibility/extract", payload),
  });
}

export function useEligibilityCheck() {
  return useMutation({
    mutationFn: (payload: EligibilityCheckRequest) =>
      apiClient.post<EligibilityCheckResponse>("/janmitra/eligibility/check", payload),
  });
}
