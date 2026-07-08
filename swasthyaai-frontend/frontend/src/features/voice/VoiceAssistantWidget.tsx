import { useState } from "react";
import { Mic, Square, RotateCcw, Send, Volume2 } from "lucide-react";

import { useMediaRecorder } from "@/hooks/useMediaRecorder";
import { useVoiceQuery } from "@/hooks/useVoiceQuery";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AIExplanationCard } from "@/components/common/AIExplanationCard";
import { ErrorState } from "@/components/common/ErrorState";
import { LanguageToggle } from "@/components/common/LanguageToggle";
import { cn } from "@/lib/utils";
import type { SupportedLanguageCode } from "@/config";
import type { VoiceMode } from "@/types/api";

interface VoiceAssistantWidgetProps {
  mode: VoiceMode;
  phcId?: number;
  className?: string;
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function VoiceAssistantWidget({ mode, phcId, className }: VoiceAssistantWidgetProps) {
  const [language, setLanguage] = useState<SupportedLanguageCode>("en");
  const recorder = useMediaRecorder();
  const voiceQuery = useVoiceQuery();

  const handleSend = () => {
    if (!recorder.audioBlob) return;
    voiceQuery.mutate({ audioBlob: recorder.audioBlob, language, mode, phcId });
  };

  const handleReset = () => {
    recorder.reset();
    voiceQuery.reset();
  };

  if (!recorder.isSupported) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <ErrorState
            title="Voice input isn't available in this browser"
            description="Try opening this page in Chrome or Edge to use voice. You can still type your question above."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardContent className="flex flex-col items-center gap-5 p-6">
        <div className="flex w-full items-center justify-between">
          <p className="text-sm font-medium text-ink-900">
            {mode === "citizen_scheme_query" ? "Ask about schemes by voice" : "Ask about inventory by voice"}
          </p>
          <LanguageToggle value={language} onChange={setLanguage} />
        </div>

        {!recorder.audioUrl && (
          <div className="flex flex-col items-center gap-3 py-4">
            <button
              type="button"
              onClick={recorder.status === "recording" ? recorder.stop : recorder.start}
              aria-label={recorder.status === "recording" ? "Stop recording" : "Start recording"}
              className={cn(
                "relative flex h-20 w-20 items-center justify-center rounded-full text-white shadow-md transition-colors",
                recorder.status === "recording" ? "bg-destructive-600" : "bg-primary-700 hover:bg-primary-600"
              )}
            >
              {recorder.status === "recording" && (
                <span className="absolute inset-0 animate-pulse-ring rounded-full bg-destructive-600/40" />
              )}
              {recorder.status === "recording" ? <Square className="h-7 w-7" /> : <Mic className="h-7 w-7" />}
            </button>
            <p className="text-sm text-muted-foreground">
              {recorder.status === "recording" ? formatDuration(recorder.durationSeconds) : "Tap to speak"}
            </p>
          </div>
        )}

        {recorder.error && <ErrorState title="Recording problem" description={recorder.error} />}

        {recorder.audioUrl && !voiceQuery.data && (
          <div className="flex w-full flex-col items-center gap-3">
            <audio controls src={recorder.audioUrl} className="w-full" />
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleReset}>
                <RotateCcw className="h-4 w-4" />
                Re-record
              </Button>
              <Button onClick={handleSend} disabled={voiceQuery.isPending}>
                <Send className="h-4 w-4" />
                {voiceQuery.isPending ? "Processing..." : "Send"}
              </Button>
            </div>
          </div>
        )}

        {voiceQuery.isError && (
          <ErrorState error={voiceQuery.error} onRetry={handleSend} className="w-full" />
        )}

        {voiceQuery.data && (
          <div className="w-full space-y-4 text-left">
            <div className="rounded-md bg-secondary p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">You said</p>
              <p className="mt-1 text-sm italic text-ink-900">&ldquo;{voiceQuery.data.transcript}&rdquo;</p>
            </div>

            <AIExplanationCard explanation={voiceQuery.data.explanation} />

            {voiceQuery.data.audio_base64 && (
              <div className="flex items-center gap-2 rounded-md border border-border p-3">
                <Volume2 className="h-4 w-4 shrink-0 text-primary-700" />
                <audio
                  controls
                  autoPlay
                  className="w-full"
                  src={`data:${voiceQuery.data.audio_content_type};base64,${voiceQuery.data.audio_base64}`}
                />
              </div>
            )}

            <Button variant="outline" onClick={handleReset} className="w-full">
              <RotateCcw className="h-4 w-4" />
              Ask another question
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
