import { useMutation } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { LanguageCode, VoiceMode, VoiceQueryResponse } from "@/types/api";

interface VoiceQueryInput {
  audioBlob: Blob;
  language: LanguageCode;
  mode: VoiceMode;
  phcId?: number;
}

function extensionFor(mimeType: string): string {
  if (mimeType.includes("mp4")) return "mp4";
  return "webm";
}

export function useVoiceQuery() {
  return useMutation({
    mutationFn: async ({ audioBlob, language, mode, phcId }: VoiceQueryInput) => {
      const formData = new FormData();
      formData.append("audio", audioBlob, `recording.${extensionFor(audioBlob.type)}`);
      formData.append("language", language);

      if (mode === "citizen_scheme_query") {
        return apiClient.postForm<VoiceQueryResponse>("/voice/citizen-query", formData, { auth: false });
      }
      if (!phcId) throw new Error("A PHC must be selected for an inventory voice query.");
      return apiClient.postForm<VoiceQueryResponse>(`/voice/inventory-query/${phcId}`, formData);
    },
  });
}
