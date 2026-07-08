import { useState } from "react";
import { Building2, MessageCircleQuestion, Send } from "lucide-react";

import { useDistrictSelection } from "@/hooks/useDistrictSelection";
import { useCopilotQuery, useDistrictSummary } from "@/hooks/useDistrict";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/common/StatCard";
import { CardSkeleton, StatCardSkeleton } from "@/components/common/LoadingSkeletons";
import { ErrorState } from "@/components/common/ErrorState";
import { AttentionCard } from "@/components/common/AttentionCard";
import { AIExplanationCard } from "@/components/common/AIExplanationCard";
import { AttentionScoreChart } from "@/components/charts/AttentionScoreChart";
import type { PHCStatusSummary } from "@/types/api";

const EXAMPLE_QUESTIONS = [
  "Which PHCs need attention today?",
  "Where are doctors most frequently absent?",
  "Which PHCs are close to running out of medicines?",
];

function severityFor(status: PHCStatusSummary): "critical" | "high" | "medium" | "low" {
  if (status.attention_score >= 15) return "critical";
  if (status.attention_score >= 8) return "high";
  if (status.attention_score >= 3) return "medium";
  return "low";
}

export function DistrictCopilotPage() {
  const { districtId, districts, selectedDistrictId, setSelectedDistrictId, needsPicker } = useDistrictSelection();
  const summaryQuery = useDistrictSummary(districtId);
  const copilotQuery = useCopilotQuery(districtId);
  const [question, setQuestion] = useState("");

  function handleAsk(q: string) {
    if (!q.trim()) return;
    copilotQuery.mutate({ question: q });
  }

  return (
    <div>
      <PageHeader
        title="District AI Copilot"
        description={summaryQuery.data ? summaryQuery.data.district_name : "District-wide operational intelligence"}
        actions={
          needsPicker && districts ? (
            <Select value={selectedDistrictId?.toString()} onValueChange={(v) => setSelectedDistrictId(Number(v))}>
              <SelectTrigger className="w-56">
                <SelectValue placeholder="Select a district" />
              </SelectTrigger>
              <SelectContent>
                {districts.map((d) => (
                  <SelectItem key={d.id} value={d.id.toString()}>
                    {d.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : undefined
        }
      />

      {summaryQuery.isLoading && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <StatCardSkeleton key={i} />
            ))}
          </div>
          <CardSkeleton lines={5} />
        </div>
      )}

      {summaryQuery.isError && <ErrorState error={summaryQuery.error} onRetry={() => summaryQuery.refetch()} />}

      {summaryQuery.data && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard
              label="PHCs monitored"
              value={summaryQuery.data.phc_statuses.length}
              icon={Building2}
            />
            <StatCard
              label="Needing urgent attention"
              value={summaryQuery.data.phc_statuses.filter((p) => p.attention_score >= 15).length}
              tone="destructive"
            />
            <StatCard
              label="Total open alerts"
              value={summaryQuery.data.phc_statuses.reduce((sum, p) => sum + p.open_alert_count, 0)}
              tone="warning"
            />
            <StatCard
              label="Patients (7 days, district-wide)"
              value={summaryQuery.data.phc_statuses.reduce((sum, p) => sum + p.footfall_7day_total, 0)}
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>PHCs ranked by attention score</CardTitle>
                <CardDescription>Higher score means more urgent combined operational issues</CardDescription>
              </CardHeader>
              <CardContent>
                <AttentionScoreChart statuses={summaryQuery.data.phc_statuses} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>
                  <span className="flex items-center gap-2">
                    <MessageCircleQuestion className="h-4 w-4 text-primary-700" />
                    Ask the copilot
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Textarea
                  rows={3}
                  placeholder="e.g. Which PHCs need attention today?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                />
                <div className="flex flex-wrap gap-1.5">
                  {EXAMPLE_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      type="button"
                      onClick={() => setQuestion(q)}
                      className="rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground hover:border-primary-700 hover:text-primary-700"
                    >
                      {q}
                    </button>
                  ))}
                </div>
                <Button onClick={() => handleAsk(question)} disabled={copilotQuery.isPending} className="w-full">
                  <Send className="h-4 w-4" />
                  {copilotQuery.isPending ? "Thinking..." : "Ask"}
                </Button>

                {copilotQuery.isError && <ErrorState error={copilotQuery.error} />}
                {copilotQuery.data && <AIExplanationCard explanation={copilotQuery.data.explanation} />}
              </CardContent>
            </Card>
          </div>

          <div>
            <h3 className="mb-3 font-display text-sm font-semibold text-ink-900">All PHCs in this district</h3>
            <div className="space-y-2">
              {summaryQuery.data.phc_statuses.map((status) => (
                <AttentionCard
                  key={status.phc_id}
                  severity={severityFor(status)}
                  eyebrow={`Score ${status.attention_score}`}
                  title={status.phc_name}
                  description={
                    <span>
                      {status.low_stock_medicine_count} medicines low ·{" "}
                      {Math.round(status.doctor_absence_rate * 100)}% doctor absence ·{" "}
                      {Math.round(status.bed_occupancy_rate * 100)}% bed occupancy ·{" "}
                      {status.open_alert_count} open alerts
                    </span>
                  }
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
