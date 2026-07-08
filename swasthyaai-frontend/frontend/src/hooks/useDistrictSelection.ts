import { useEffect, useState } from "react";

import { useAuth } from "@/features/auth/AuthContext";
import { useDistricts } from "@/hooks/useDistrict";
import type { DistrictOut } from "@/types/api";

interface UseDistrictSelectionResult {
  districtId: number | undefined;
  districts: DistrictOut[] | undefined;
  selectedDistrictId: number | undefined;
  setSelectedDistrictId: (id: number) => void;
  needsPicker: boolean;
}

export function useDistrictSelection(): UseDistrictSelectionResult {
  const { staff } = useAuth();
  const needsPicker = staff?.role === "admin" && !staff.district_id;
  const { data: districts } = useDistricts();
  const [selectedDistrictId, setSelectedDistrictId] = useState<number | undefined>(staff?.district_id ?? undefined);

  useEffect(() => {
    if (needsPicker && !selectedDistrictId && districts && districts.length > 0) {
      setSelectedDistrictId(districts[0].id);
    }
  }, [needsPicker, selectedDistrictId, districts]);

  return {
    districtId: staff?.district_id ?? selectedDistrictId,
    districts: needsPicker ? districts : undefined,
    selectedDistrictId,
    setSelectedDistrictId,
    needsPicker,
  };
}
