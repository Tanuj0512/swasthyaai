import { ExternalLink, FileText } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SchemeOut } from "@/types/api";

interface SchemeCardProps {
  scheme: SchemeOut;
  /** Optional eligibility annotation — used only on the staff eligibility results page. */
  eligibility?: { isEligible: boolean };
}

export function SchemeCard({ scheme, eligibility }: SchemeCardProps) {
  return (
    <Card className={eligibility ? (eligibility.isEligible ? "border-l-4 border-l-success-500" : "border-l-4 border-l-border opacity-75") : undefined}>
      <CardHeader>
        <div className="flex flex-wrap items-start justify-between gap-2">
          <CardTitle className="text-base">{scheme.name}</CardTitle>
          <div className="flex shrink-0 gap-1.5">
            <Badge variant={scheme.level === "central" ? "info" : "secondary"}>
              {scheme.level === "central" ? "Central" : "State"}
            </Badge>
            {eligibility && (
              <Badge variant={eligibility.isEligible ? "success" : "outline"}>
                {eligibility.isEligible ? "Eligible" : "Not eligible"}
              </Badge>
            )}
          </div>
        </div>
        <p className="text-xs text-muted-foreground">{scheme.authority}</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-ink-900">{scheme.description}</p>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Benefits</p>
          <p className="mt-0.5 text-sm text-ink-900">{scheme.benefits_summary}</p>
        </div>
        {scheme.documents.length > 0 && (
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Required documents</p>
            <ul className="space-y-1">
              {scheme.documents.map((doc) => (
                <li key={doc.document_name} className="flex items-center gap-1.5 text-sm text-ink-900">
                  <FileText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  {doc.document_name}
                  {!doc.mandatory && <span className="text-xs text-muted-foreground">(optional)</span>}
                </li>
              ))}
            </ul>
          </div>
        )}
        {scheme.official_url && (
          <a
            href={scheme.official_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-sm font-medium text-primary-700 hover:underline"
          >
            Official website
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        )}
      </CardContent>
    </Card>
  );
}
