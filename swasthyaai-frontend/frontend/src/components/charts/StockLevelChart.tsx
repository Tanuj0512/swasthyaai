import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { MedicineForecast } from "@/types/api";
import { EmptyState } from "@/components/common/EmptyState";
import { PackageSearch } from "lucide-react";

interface StockLevelChartProps {
  forecasts: MedicineForecast[];
}

export function StockLevelChart({ forecasts }: StockLevelChartProps) {
  if (forecasts.length === 0) {
    return <EmptyState icon={PackageSearch} title="No stock data yet" description="Medicine stock records will appear here once entered." />;
  }

  const data = [...forecasts]
    .sort((a, b) => a.current_quantity - b.current_quantity)
    .slice(0, 10)
    .map((f) => ({
      name: f.medicine_name.length > 18 ? `${f.medicine_name.slice(0, 18)}…` : f.medicine_name,
      quantity: f.current_quantity,
      threshold: f.reorder_threshold,
      isLow: f.is_low_stock,
    }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
        <XAxis type="number" tick={{ fontSize: 12 }} allowDecimals={false} />
        <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 12 }} />
        <Tooltip
          formatter={(value: number, name: string) => [value, name === "quantity" ? "In stock" : "Reorder threshold"]}
          contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: "hsl(var(--border))" }}
        />
        <Bar dataKey="quantity" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.isLow ? "#C1382E" : "#127069"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
