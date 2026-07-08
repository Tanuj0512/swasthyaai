import { Loader2 } from "lucide-react";

export function LoadingScreen({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-paper-50">
      <Loader2 className="h-8 w-8 animate-spin text-primary-700" aria-hidden />
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  );
}
