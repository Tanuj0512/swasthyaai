import { AlertTriangle, BedDouble, Pill, Stethoscope, Users } from "lucide-react";

import { useDashboard } from "@/hooks/useDashboard";
import { usePhcSelection } from "@/hooks/usePhcSelection";
import { PageHeader } from "@/components/layout/PageHeader";
import { StatCard } from "@/components/common/StatCard";
import { StatCardSkeleton, CardSkeleton } from "@/components/common/LoadingSkeletons";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { AttentionCard } from "@/components/common/AttentionCard";
import { FootfallTrendChart } from "@/components/charts/FootfallTrendChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AlertSeverity, DoctorAttendanceSummary } from "@/types/api";

const ATTENDANCE_STYLES: Record<DoctorAttendanceSummary["status"], { label: string; variant: "success" | "destructive" | "warning" | "secondary" }> = {
  present: { label: "Present", variant: "success" },
  absent: { label: "Absent", variant: "destructive" },
  leave: { label: "On leave", variant: "warning" },
  not_marked: { label: "Not marked", variant: "secondary" },
};

const ALERT_SEVERITY_MAP: Record<AlertSeverity, "low" | "medium" | "high" | "critical"> = {
  low: "low",
  medium: "medium",
  high: "high",
  critical: "critical",
};

export function DashboardPage() {
  const { phcId, phcs, selectedPhcId, setSelectedPhcId, needsPicker } = usePhcSelection();
  const { data, isLoading, isError, error, refetch } = useDashboard(phcId);

  return (
    <div>
      <PageHeader
        title="PHC Dashboard"
        description={data ? data.phc.name : "Live operational snapshot for your primary health centre"}
        actions={
          needsPicker && phcs ? (
            <Select value={selectedPhcId?.toString()} onValueChange={(v) => setSelectedPhcId(Number(v))}>
              <SelectTrigger className="w-56">
                <SelectValue placeholder="Select a PHC" />
              </SelectTrigger>
              <SelectContent>
                {phcs.map((phc) => (
                  <SelectItem key={phc.id} value={phc.id.toString()}>
                    {phc.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : undefined
        }
      />

      {isLoading && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <StatCardSkeleton key={i} />
            ))}
          </div>
          <CardSkeleton lines={4} />
        </div>
      )}

      {isError && <ErrorState error={error} onRetry={() => refetch()} />}

      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard
              label="Low-stock medicines"
              value={data.medicine_inventory.filter((m) => m.is_low).length}
              icon={Pill}
              tone={data.medicine_inventory.some((m) => m.is_low) ? "warning" : "success"}
            />
            <StatCard
              label="Bed occupancy"
              value={`${Math.round(
                (data.beds.reduce((sum, b) => sum + b.occupied_beds, 0) /
                  Math.max(1, data.beds.reduce((sum, b) => sum + b.total_beds, 0))) *
                  100
              )}%`}
              icon={BedDouble}
              tone="default"
            />
            <StatCard
              label="Doctors present today"
              value={`${data.doctor_attendance_today.filter((d) => d.status === "present").length}/${data.doctor_attendance_today.length}`}
              icon={Stethoscope}
              tone={data.doctor_attendance_today.some((d) => d.status === "absent") ? "warning" : "success"}
            />
            <StatCard
              label="Patients (7 days)"
              value={data.footfall_last_7_days.reduce((sum, f) => sum + f.count, 0)}
              icon={Users}
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Patient footfall — last 7 days</CardTitle>
              </CardHeader>
              <CardContent>
                <FootfallTrendChart footfall={data.footfall_last_7_days} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0">
                <CardTitle>Recent alerts</CardTitle>
                <AlertTriangle className="h-4 w-4 text-marigold-600" />
              </CardHeader>
              <CardContent className="space-y-3">
                {data.recent_alerts.length === 0 ? (
                  <EmptyState title="No open alerts" description="Everything looks normal at this PHC." />
                ) : (
                  data.recent_alerts.map((alert) => (
                    <AttentionCard
                      key={alert.id}
                      severity={ALERT_SEVERITY_MAP[alert.severity]}
                      eyebrow={alert.type.replace("_", " ")}
                      title={alert.message}
                    />
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Bed availability</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {data.beds.map((bed) => (
                  <div key={bed.ward_type}>
                    <div className="mb-1 flex items-center justify-between text-sm">
                      <span className="font-medium text-ink-900">{bed.ward_type}</span>
                      <span className="text-muted-foreground">
                        {bed.occupied_beds}/{bed.total_beds} occupied
                      </span>
                    </div>
                    <Progress
                      value={bed.occupancy_rate * 100}
                      indicatorClassName={bed.occupancy_rate >= 0.85 ? "bg-destructive-600" : undefined}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Doctor attendance today</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {data.doctor_attendance_today.map((doc) => {
                  const style = ATTENDANCE_STYLES[doc.status];
                  return (
                    <div key={doc.doctor_id} className="flex items-center justify-between rounded-md border border-border px-3 py-2">
                      <div>
                        <p className="text-sm font-medium text-ink-900">{doc.doctor_name}</p>
                        <p className="text-xs text-muted-foreground">{doc.specialization}</p>
                      </div>
                      <Badge variant={style.variant}>{style.label}</Badge>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
