import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export type Severity = "low" | "medium" | "high" | "critical" | "info" | "success";

const severityConfig: Record<Severity, { border: string; badge: string; label: string }> = {
  critical: { border: "border-l-destructive-600", badge: "bg-destructive-50 text-destructive-600", label: "Critical" },
  high: { border: "border-l-destructive-500", badge: "bg-destructive-50 text-destructive-600", label: "High" },
  medium: { border: "border-l-marigold-500", badge: "bg-marigold-100 text-marigold-600", label: "Medium" },
  low: { border: "border-l-primary-100", badge: "bg-secondary text-muted-foreground", label: "Low" },
  info: { border: "border-l-primary-600", badge: "bg-primary-50 text-primary-700", label: "Info" },
  success: { border: "border-l-success-500", badge: "bg-success-50 text-success-600", label: "Good" },
};

interface AttentionCardProps {
  severity: Severity;
  eyebrow?: string;
  title: string;
  description?: ReactNode;
  action?: ReactNode;
  className?: string;
}

/**
 * This left-border + eyebrow-label pattern is used everywhere in the app
 * that surfaces "something needing attention": dashboard alerts, low-stock
 * medicines, and PHCs ranked by the District Copilot's attention score. One
 * consistent visual grammar for the product's core job — triage.
 */
export function AttentionCard({ severity, eyebrow, title, description, action, className }: AttentionCardProps) {
  const cfg = severityConfig[severity];
  return (
    <div
      className={cn(
        "flex items-start justify-between gap-3 rounded-md border border-l-4 border-border bg-card p-4 shadow-sm",
        cfg.border,
        className
      )}
    >
      <div className="min-w-0">
        <div className="mb-1 flex items-center gap-2">
          <span className={cn("inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide", cfg.badge)}>
            {eyebrow ?? cfg.label}
          </span>
        </div>
        <p className="font-medium text-ink-900">{title}</p>
        {description && <div className="mt-0.5 text-sm text-muted-foreground">{description}</div>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
