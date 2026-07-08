import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { Mic, Search, ShieldCheck } from "lucide-react";

import { useCitizenQuery } from "@/hooks/useJanMitra";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { AIExplanationCard } from "@/components/common/AIExplanationCard";
import { LanguageToggle } from "@/components/common/LanguageToggle";
import { SchemeCard } from "@/features/janmitra/SchemeCard";
import { VoiceAssistantWidget } from "@/features/voice/VoiceAssistantWidget";
import type { SupportedLanguageCode } from "@/config";

const querySchema = z.object({
  question: z.string().min(3, "Please type a few words about what you need help with."),
});
type QueryFormValues = z.infer<typeof querySchema>;

const EXAMPLE_QUESTIONS = [
  "Are there schemes for pregnant women?",
  "What help is available for senior citizens?",
  "Free treatment schemes in Maharashtra",
];

export function CitizenHomePage() {
  const [language, setLanguage] = useState<SupportedLanguageCode>("en");
  const citizenQuery = useCitizenQuery();

  const form = useForm<QueryFormValues>({
    resolver: zodResolver(querySchema),
    defaultValues: { question: "" },
  });

  function onSubmit(values: QueryFormValues) {
    citizenQuery.mutate({ question: values.question, language });
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
      <div className="mb-10 text-center">
        <div className="mb-4 inline-flex items-center gap-1.5 rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700">
          <ShieldCheck className="h-3.5 w-3.5" />
          Free · Government healthcare information
        </div>
        <h1 className="font-display text-3xl font-semibold text-ink-900 sm:text-4xl">
          Find the healthcare scheme that's right for you
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-base text-muted-foreground">
          Ask a question in your own words — in English or Hindi, by typing or by speaking — and JanMitra will
          show you schemes you may qualify for, in plain language.
        </p>
      </div>

      <Card className="mx-auto max-w-2xl">
        <CardContent className="p-5 sm:p-6">
          <Tabs defaultValue="type">
            <div className="mb-4 flex items-center justify-between">
              <TabsList>
                <TabsTrigger value="type">
                  <Search className="h-4 w-4" />
                  Type a question
                </TabsTrigger>
                <TabsTrigger value="voice">
                  <Mic className="h-4 w-4" />
                  Speak
                </TabsTrigger>
              </TabsList>
              <LanguageToggle value={language} onChange={setLanguage} className="hidden sm:inline-flex" />
            </div>

            <TabsContent value="type" className="mt-0">
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-3">
                <Textarea
                  placeholder="e.g. Are there any schemes for a 65 year old with a BPL card?"
                  rows={3}
                  {...form.register("question")}
                />
                {form.formState.errors.question && (
                  <p className="text-sm text-destructive-600">{form.formState.errors.question.message}</p>
                )}
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      type="button"
                      onClick={() => form.setValue("question", q)}
                      className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground hover:border-primary-700 hover:text-primary-700"
                    >
                      {q}
                    </button>
                  ))}
                </div>
                <Button type="submit" className="w-full sm:w-auto" disabled={citizenQuery.isPending}>
                  <Search className="h-4 w-4" />
                  {citizenQuery.isPending ? "Searching..." : "Find schemes"}
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="voice" className="mt-0">
              <VoiceAssistantWidget mode="citizen_scheme_query" className="border-none shadow-none" />
            </TabsContent>
          </Tabs>

          {citizenQuery.isError && <ErrorState error={citizenQuery.error} className="mt-4" />}

          {citizenQuery.data && (
            <div className="mt-6 space-y-4 border-t border-border pt-6">
              <AIExplanationCard explanation={citizenQuery.data.explanation} />
              {citizenQuery.data.matched_schemes.length === 0 ? (
                <EmptyState title="No matching schemes found" description="Try rephrasing your question, or browse all schemes below." />
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  {citizenQuery.data.matched_schemes.map((scheme) => (
                    <SchemeCard key={scheme.id} scheme={scheme} />
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <p className="mt-8 text-center text-sm text-muted-foreground">
        Prefer to browse everything yourself?{" "}
        <Link to="/schemes" className="font-medium text-primary-700 hover:underline">
          See all healthcare schemes
        </Link>
      </p>
    </div>
  );
}
