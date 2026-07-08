import { useState } from "react";
import { toast } from "sonner";
import { ArrowRight, PackageCheck } from "lucide-react";

import { usePhcSelection } from "@/hooks/usePhcSelection";
import { useInventoryForecast, useInventoryRecommendations, useLogConsumption } from "@/hooks/useInventory";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { CardSkeleton, TableSkeleton } from "@/components/common/LoadingSkeletons";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { AIExplanationCard } from "@/components/common/AIExplanationCard";
import { StockLevelChart } from "@/components/charts/StockLevelChart";
import { ConsumptionLogForm } from "@/features/inventory/ConsumptionLogForm";

export function InventoryPage() {
  const { phcId, phcs, selectedPhcId, setSelectedPhcId, needsPicker } = usePhcSelection();
  const forecastQuery = useInventoryForecast(phcId);
  const recommendationsQuery = useInventoryRecommendations(phcId);
  const logConsumption = useLogConsumption(phcId);
  const [logError, setLogError] = useState<string | null>(null);

  async function handleLog(values: { medicine_id: number; quantity_used: number }) {
    setLogError(null);
    try {
      await logConsumption.mutateAsync(values);
      toast.success("Consumption logged", { description: "Stock and forecasts have been updated." });
    } catch (err) {
      setLogError(err instanceof Error ? err.message : "Could not log consumption.");
    }
  }

  return (
    <div>
      <PageHeader
        title="AI Inventory Intelligence"
        description="Stock forecasts, low-stock alerts, and redistribution suggestions"
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

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Stock levels (lowest 10)</CardTitle>
            <CardDescription>Red bars are at or below reorder threshold</CardDescription>
          </CardHeader>
          <CardContent>
            {forecastQuery.isLoading && <CardSkeleton lines={5} />}
            {forecastQuery.isError && <ErrorState error={forecastQuery.error} onRetry={() => forecastQuery.refetch()} />}
            {forecastQuery.data && <StockLevelChart forecasts={forecastQuery.data.forecasts} />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Log medicine usage</CardTitle>
            <CardDescription>Recorded consumption improves forecast accuracy</CardDescription>
          </CardHeader>
          <CardContent>
            {forecastQuery.data && (
              <>
                <ConsumptionLogForm
                  medicines={forecastQuery.data.forecasts}
                  onSubmit={handleLog}
                  isSubmitting={logConsumption.isPending}
                />
                {logError && <p className="mt-3 text-sm text-destructive-600">{logError}</p>}
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>AI Recommendations</CardTitle>
          <CardDescription>Forecasts and redistribution suggestions with a plain-language explanation</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {recommendationsQuery.isLoading && <TableSkeleton rows={4} />}
          {recommendationsQuery.isError && (
            <ErrorState error={recommendationsQuery.error} onRetry={() => recommendationsQuery.refetch()} />
          )}

          {recommendationsQuery.data && (
            <>
              {recommendationsQuery.data.low_stock_forecasts.length === 0 ? (
                <EmptyState
                  icon={PackageCheck}
                  title="All medicines are well stocked"
                  description="No medicine at this PHC is currently below its reorder threshold."
                />
              ) : (
                <div className="overflow-hidden rounded-md border border-border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Medicine</TableHead>
                        <TableHead>In stock</TableHead>
                        <TableHead>Avg. daily use</TableHead>
                        <TableHead>Predicted stockout</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {recommendationsQuery.data.low_stock_forecasts.map((f) => (
                        <TableRow key={f.medicine_id}>
                          <TableCell className="font-medium text-ink-900">{f.medicine_name}</TableCell>
                          <TableCell>{f.current_quantity}</TableCell>
                          <TableCell>{f.avg_daily_consumption}</TableCell>
                          <TableCell>
                            {f.predicted_days_until_stockout !== null ? (
                              <Badge variant={f.predicted_days_until_stockout <= 7 ? "destructive" : "warning"}>
                                {f.predicted_days_until_stockout} days
                              </Badge>
                            ) : (
                              <span className="text-muted-foreground">No recent usage data</span>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}

              {recommendationsQuery.data.redistribution_suggestions.length > 0 && (
                <div>
                  <h3 className="mb-3 font-display text-sm font-semibold text-ink-900">Redistribution suggestions</h3>
                  <div className="space-y-2">
                    {recommendationsQuery.data.redistribution_suggestions.map((s, idx) => (
                      <div key={idx} className="flex flex-wrap items-center gap-2 rounded-md border border-border p-3 text-sm">
                        <Badge variant="info">{s.suggested_quantity} units</Badge>
                        <span className="font-medium text-ink-900">{s.medicine_name}</span>
                        <span className="text-muted-foreground">from</span>
                        <span className="font-medium text-ink-900">{s.from_phc_name}</span>
                        <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                        <span className="font-medium text-ink-900">{s.to_phc_name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <AIExplanationCard explanation={recommendationsQuery.data.explanation} />
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
