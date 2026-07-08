import { AlertTriangle, RefreshCw, WifiOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ApiError } from "@/lib/api-client";

interface ErrorStateProps {
  title?: string;
  description?: string;
  error?: unknown;
  onRetry?: () => void;
  className?: string;
}

/** Turns a caught error (ApiError, network TypeError, or anything else)
 * into a plain-language title/description a non-technical user — staff or
 * citizen — can actually act on. */
function describeError(error: unknown): { title: string; description: string; isOffline: boolean } {
  if (error instanceof ApiError) {
    if (error.code === "RATE_LIMITED") {
      return { title: "Too many requests", description: error.message, isOffline: false };
    }
    if (error.status === 401) {
      return { title: "Sign-in required", description: "Please sign in again to continue.", isOffline: false };
    }
    if (error.status === 403) {
      return { title: "Not authorized", description: error.message, isOffline: false };
    }
    if (error.status === 404) {
      return { title: "Not found", description: error.message, isOffline: false };
    }
    if (error.status >= 500) {
      return { title: "Server error", description: "Something went wrong on our end. Please try again shortly.", isOffline: false };
    }
    return { title: "Something went wrong", description: error.message, isOffline: false };
  }
  if (error instanceof TypeError) {
    return { title: "Connection problem", description: "Could not reach the server. Check your internet connection.", isOffline: true };
  }
  return { title: "Something went wrong", description: "Please try again.", isOffline: false };
}

export function ErrorState({ title, description, error, onRetry, className }: ErrorStateProps) {
  const derived = error ? describeError(error) : null;
  const finalTitle = title ?? derived?.title ?? "Something went wrong";
  const finalDescription = description ?? derived?.description ?? "Please try again.";
  const Icon = derived?.isOffline ? WifiOff : AlertTriangle;

  return (
    <div
      role="alert"
      className={cn(
        "flex flex-col items-center gap-3 rounded-lg border border-destructive-50 bg-destructive-50/60 p-6 text-center",
        className
      )}
    >
      <Icon className="h-8 w-8 text-destructive-600" aria-hidden />
      <div>
        <p className="font-display font-semibold text-ink-900">{finalTitle}</p>
        <p className="mt-1 text-sm text-muted-foreground">{finalDescription}</p>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} className="mt-1">
          <RefreshCw className="h-4 w-4" />
          Try again
        </Button>
      )}
    </div>
  );
}
