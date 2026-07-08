import { Link } from "react-router-dom";
import { Compass } from "lucide-react";

import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-paper-50 p-6 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary-50">
        <Compass className="h-7 w-7 text-primary-700" />
      </div>
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900">Page not found</h1>
        <p className="mt-1 text-sm text-muted-foreground">The page you're looking for doesn't exist or has moved.</p>
      </div>
      <Button asChild>
        <Link to="/">Go to homepage</Link>
      </Button>
    </div>
  );
}
