import { useCallback, useEffect, useRef, useState } from "react";

const PREFERRED_MIME_TYPES = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"];

function pickSupportedMimeType(): string | null {
  if (typeof MediaRecorder === "undefined") return null;
  return PREFERRED_MIME_TYPES.find((type) => MediaRecorder.isTypeSupported(type)) ?? null;
}

export type RecorderStatus = "idle" | "recording" | "stopped" | "error";

interface UseMediaRecorderResult {
  isSupported: boolean;
  status: RecorderStatus;
  audioBlob: Blob | null;
  audioUrl: string | null;
  durationSeconds: number;
  error: string | null;
  start: () => Promise<void>;
  stop: () => void;
  reset: () => void;
}

/**
 * Wraps the browser MediaRecorder API. Deliberately does NOT attempt to
 * transcode to a specific PCM format client-side — it records in whatever
 * format the browser supports natively (WebM/Opus in Chrome, Edge, Firefox;
 * MP4/AAC in Safari) and lets the backend's Speech-to-Text configuration
 * handle that container directly. See backend `voice_service.py` — it's
 * configured to accept WEBM_OPUS to match what this hook actually produces.
 */
export function useMediaRecorder(): UseMediaRecorderResult {
  const [isSupported, setIsSupported] = useState(false);
  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [durationSeconds, setDurationSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mimeTypeRef = useRef<string>("audio/webm");

  useEffect(() => {
    const supported =
      typeof navigator !== "undefined" &&
      !!navigator.mediaDevices?.getUserMedia &&
      typeof MediaRecorder !== "undefined" &&
      pickSupportedMimeType() !== null;
    setIsSupported(supported);

    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const start = useCallback(async () => {
    setError(null);
    setAudioBlob(null);
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setDurationSeconds(0);

    const mimeType = pickSupportedMimeType();
    if (!mimeType) {
      setError("Voice recording isn't supported in this browser. Try Chrome or Edge, or use the text option instead.");
      setStatus("error");
      return;
    }
    mimeTypeRef.current = mimeType;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];

      const recorder = new MediaRecorder(stream, { mimeType });
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeTypeRef.current });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setStatus("recording");

      let elapsed = 0;
      timerRef.current = setInterval(() => {
        elapsed += 1;
        setDurationSeconds(elapsed);
      }, 1000);
    } catch (err) {
      setError(
        err instanceof DOMException && err.name === "NotAllowedError"
          ? "Microphone access was denied. Please allow microphone access and try again."
          : "Could not access the microphone."
      );
      setStatus("error");
    }
  }, [audioUrl]);

  const stop = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    mediaRecorderRef.current?.stop();
    setStatus("stopped");
  }, []);

  const reset = useCallback(() => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioBlob(null);
    setAudioUrl(null);
    setDurationSeconds(0);
    setError(null);
    setStatus("idle");
  }, [audioUrl]);

  return { isSupported, status, audioBlob, audioUrl, durationSeconds, error, start, stop, reset };
}
