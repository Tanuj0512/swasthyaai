import { Link, Outlet, useLocation } from "react-router-dom";
import { HeartPulse } from "lucide-react";


import { cn } from "@/lib/utils";

const PUBLIC_NAV = [
  { to: "/", label: "Home" },
  { to: "/schemes", label: "All Schemes" },
];

export function PublicShell() {
  const location = useLocation();

  return (
    <div className="flex min-h-screen flex-col bg-paper-50">
      <header className="sticky top-0 z-30 border-b border-border bg-card/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg  bg-white text-white">
              <img src="/logo.png" alt="SwasthyaAI" className="h-9 w-9" />
            </div>
            <div>
              <p className="font-display text-base font-semibold leading-none text-ink-900">SwasthyaAI</p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">JanMitra · Public Healthcare Help</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 sm:flex" aria-label="Main navigation">
            {PUBLIC_NAV.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  location.pathname === item.to
                    ? "bg-primary-50 text-primary-700"
                    : "text-muted-foreground hover:text-ink-900"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <Link
            to="/login"
            className="rounded-md border border-border px-3 py-2 text-sm font-medium text-ink-900 hover:bg-secondary"
          >
            Staff Login
          </Link>
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-border bg-card py-6">
        <div className="mx-auto max-w-6xl px-4 text-center text-xs text-muted-foreground sm:px-6">
          <p>
            SwasthyaAI is a decision-support layer over public healthcare data. For medical emergencies, contact
            your nearest PHC or dial 108 (National Ambulance Service).
          </p>
        </div>
      </footer>
    </div>
  );
}
