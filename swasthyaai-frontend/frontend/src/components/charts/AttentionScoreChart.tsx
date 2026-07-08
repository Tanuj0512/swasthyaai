import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { PHCStatusSummary } from "@/types/api";

interface AttentionScoreChartProps {
  statuses: PHCStatusSummary[];
}

function colorForScore(score: number): string {
  if (score >= 15) return "#C1382E";
  if (score >= 8) return "#E0930F";
  return "#127069";
}

export function AttentionScoreChart({ statuses }: AttentionScoreChartProps) {
  const data = statuses.map((s) => ({
    name: s.phc_name.length > 16 ? `${s.phc_name.slice(0, 16)}…` : s.phc_name,
    score: s.attention_score,
  }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(240, data.length * 36)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 12 }} />
        <Tooltip
          formatter={(value: number) => [value, "Attention score"]}
          contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: "hsl(var(--border))" }}
        />
        <Bar dataKey="score" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell key={index} fill={colorForScore(entry.score)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
