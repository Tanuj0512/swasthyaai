import { useMemo } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { LineChart as LineChartIcon } from "lucide-react";

import type { FootfallSummary } from "@/types/api";
import { EmptyState } from "@/components/common/EmptyState";

interface FootfallTrendChartProps {
  footfall: FootfallSummary[];
}

export function FootfallTrendChart({ footfall }: FootfallTrendChartProps) {
  const data = useMemo(() => {
    const totalsByDate = new Map<string, number>();
    for (const entry of footfall) {
      totalsByDate.set(entry.date, (totalsByDate.get(entry.date) ?? 0) + entry.count);
    }
    return Array.from(totalsByDate.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, total]) => ({
        date: new Date(date).toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
        total,
      }));
  }, [footfall]);

  if (data.length === 0) {
    return (
      <EmptyState
        icon={LineChartIcon}
        title="No footfall data yet"
        description="Patient footfall will appear here once recorded."
      />
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ left: 0, right: 16, top: 8 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
        <Tooltip
          formatter={(value: number) => [value, "Patients"]}
          contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: "hsl(var(--border))" }}
        />
        <Line type="monotone" dataKey="total" stroke="#0E5A56" strokeWidth={2.5} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
