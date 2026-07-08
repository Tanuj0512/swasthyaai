import { useState } from "react";
import { Sparkles } from "lucide-react";

import { usePhcSelection } from "@/hooks/usePhcSelection";
import { useEligibilityCheck, useExtractProfile } from "@/hooks/useJanMitra";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ErrorState } from "@/components/common/ErrorState";
import { AIExplanationCard } from "@/components/common/AIExplanationCard";
import { PatientProfileForm } from "@/features/janmitra/PatientProfileForm";
import { SchemeCard } from "@/features/janmitra/SchemeCard";
import type { PatientProfile } from "@/types/api";

export function StaffEligibilityPage() {
  const { phcId } = usePhcSelection();
  const [freeText, setFreeText] = useState("");
  const [extractedProfile, setExtractedProfile] = useState<PatientProfile | undefined>();

  const extractProfile = useExtractProfile();
  const eligibilityCheck = useEligibilityCheck();

  async function handleExtract() {
    const result = await extractProfile.mutateAsync({ free_text: freeText });
    setExtractedProfile(result.profile);
  }

  function handleCheck(profile: PatientProfile) {
    eligibilityCheck.mutate({ profile, phc_id: phcId });
  }

  return (
    <div>
      <PageHeader
        title="JanMitra — Eligibility Checker"
        description="Extract a patient profile from a description, verify it, then check eligibility against the deterministic rule engine"
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Step 1 — Patient profile</CardTitle>
            <CardDescription>
              Describe the patient in your own words and let AI pre-fill the form, or enter details manually. Either
              way, you confirm every field before checking eligibility.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="describe">
              <TabsList className="mb-4">
                <TabsTrigger value="describe">
                  <Sparkles className="h-4 w-4" />
                  Describe patient
                </TabsTrigger>
                <TabsTrigger value="manual">Manual entry</TabsTrigger>
              </TabsList>

              <TabsContent value="describe" className="mt-0 space-y-3">
                <Textarea
                  rows={4}
                  placeholder="e.g. 45 year old woman, pregnant, BPL card holder, OBC category, income around 90000, from Maharashtra"
                  value={freeText}
                  onChange={(e) => setFreeText(e.target.value)}
                />
                <Button onClick={handleExtract} disabled={freeText.trim().length < 5 || extractProfile.isPending}>
                  <Sparkles className="h-4 w-4" />
                  {extractProfile.isPending ? "Extracting..." : "Extract profile"}
                </Button>
                {extractProfile.isError && <ErrorState error={extractProfile.error} className="mt-2" />}
                {extractProfile.data && (
                  <Alert variant="info">
                    <Sparkles className="h-4 w-4" />
                    <AlertTitle>Please verify before continuing</AlertTitle>
                    <AlertDescription>{extractProfile.data.extraction_confidence_note}</AlertDescription>
                  </Alert>
                )}
              </TabsContent>

              <TabsContent value="manual" className="mt-0">
                <p className="text-sm text-muted-foreground">Fill in the form below directly, then submit.</p>
              </TabsContent>
            </Tabs>

            <div className="mt-5 border-t border-border pt-5">
              <PatientProfileForm
                key={extractedProfile ? JSON.stringify(extractedProfile) : "manual"}
                defaultValues={extractedProfile}
                onSubmit={handleCheck}
                isSubmitting={eligibilityCheck.isPending}
              />
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Step 2 — Results</CardTitle>
              <CardDescription>Eligibility is decided only by the backend rule engine — the AI only explains it.</CardDescription>
            </CardHeader>
            <CardContent>
              {eligibilityCheck.isError && <ErrorState error={eligibilityCheck.error} />}
              {!eligibilityCheck.data && !eligibilityCheck.isPending && !eligibilityCheck.isError && (
                <p className="text-sm text-muted-foreground">Results will appear here once you check eligibility.</p>
              )}
              {eligibilityCheck.data && <AIExplanationCard explanation={eligibilityCheck.data.explanation} />}
            </CardContent>
          </Card>

          {eligibilityCheck.data && (
            <div className="space-y-3">
              {eligibilityCheck.data.results
                .slice()
                .sort((a, b) => Number(b.is_eligible) - Number(a.is_eligible))
                .map((result) => (
                  <SchemeCard
                    key={result.scheme.id}
                    scheme={result.scheme}
                    eligibility={{ isEligible: result.is_eligible }}
                  />
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
