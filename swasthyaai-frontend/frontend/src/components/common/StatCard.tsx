import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: LucideIcon;
  tone?: "default" | "warning" | "destructive" | "success";
  hint?: string;
  className?: string;
}

const toneStyles: Record<NonNullable<StatCardProps["tone"]>, string> = {
  default: "text-primary-700 bg-primary-50",
  warning: "text-marigold-600 bg-marigold-50",
  destructive: "text-destructive-600 bg-destructive-50",
  success: "text-success-600 bg-success-50",
};

export function StatCard({ label, value, icon: Icon, tone = "default", hint, className }: StatCardProps) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardContent className="flex items-start justify-between gap-3 p-5">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{label}</p>
          <p className="mt-1.5 font-display text-2xl font-semibold tabular-nums text-ink-900 sm:text-3xl">{value}</p>
          {hint && <p className="mt-1 truncate text-xs text-muted-foreground">{hint}</p>}
        </div>
        {Icon && (
          <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-full", toneStyles[tone])}>
            <Icon className="h-5 w-5" aria-hidden />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
