import { Sparkles } from "lucide-react";

import type { AIExplanation } from "@/types/api";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";

interface AIExplanationCardProps {
  explanation: AIExplanation;
  className?: string;
}

/**
 * Every AI-generated explanation in the app — inventory recommendations,
 * JanMitra eligibility explanations, district copilot summaries, voice
 * responses — renders through this one component. The consistent tinted
 * panel, icon, and always-visible disclaimer are a deliberate Responsible-AI
 * choice: a citizen or PHC staff member should never be able to mistake
 * generated explanation text for a verified database fact.
 */
export function AIExplanationCard({ explanation, className }: AIExplanationCardProps) {
  return (
    <div className={cn("rounded-lg border border-primary-100 bg-primary-50/70 p-4", className)}>
      <div className="mb-2 flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-primary-700" aria-hidden />
        <span className="text-xs font-semibold uppercase tracking-wide text-primary-700">AI Explanation</span>
        {!explanation.grounded && (
          <span className="rounded-full bg-marigold-100 px-2 py-0.5 text-[10px] font-bold uppercase text-marigold-600">
            Limited data
          </span>
        )}
      </div>
      {/* <p className="whitespace-pre-line text-sm leading-relaxed text-ink-900">{explanation.text}</p> */}
      <div className="prose prose-sm max-w-none text-ink-900 prose-p:my-1 prose-ul:my-1 prose-ol:my-1">
        <ReactMarkdown>{explanation.text}</ReactMarkdown>
      </div>
      <p className="mt-3 text-xs text-muted-foreground">{explanation.disclaimer}</p>
    </div>
  );
}
