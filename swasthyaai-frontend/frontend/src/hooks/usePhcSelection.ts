import { useEffect, useState } from "react";

import { useAuth } from "@/features/auth/AuthContext";
import { usePHCs } from "@/hooks/useDashboard";
import type { PHCOut } from "@/types/api";

interface UsePhcSelectionResult {
  phcId: number | undefined;
  /** Only populated (and only relevant) for admins with no fixed PHC. */
  phcs: PHCOut[] | undefined;
  selectedPhcId: number | undefined;
  setSelectedPhcId: (id: number) => void;
  /** Whether a PHC picker should be shown at all — false for phc_staff,
   * who are always scoped to their own PHC. */
  needsPicker: boolean;
}

export function usePhcSelection(): UsePhcSelectionResult {
  const { staff } = useAuth();
  const needsPicker = staff?.role === "admin" && !staff.phc_id;
  const { data: phcs } = usePHCs();
  const [selectedPhcId, setSelectedPhcId] = useState<number | undefined>(staff?.phc_id ?? undefined);

  useEffect(() => {
    if (needsPicker && !selectedPhcId && phcs && phcs.length > 0) {
      setSelectedPhcId(phcs[0].id);
    }
  }, [needsPicker, selectedPhcId, phcs]);

  return {
    phcId: staff?.phc_id ?? selectedPhcId,
    phcs: needsPicker ? phcs : undefined,
    selectedPhcId,
    setSelectedPhcId,
    needsPicker,
  };
}
