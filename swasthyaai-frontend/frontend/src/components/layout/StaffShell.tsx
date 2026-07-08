import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import {
  Building2,
  HeartPulse,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquareHeart,
  Package,
  X,
} from "lucide-react";

import { useAuth } from "@/features/auth/AuthContext";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { StaffRole } from "@/types/api";

interface NavItem {
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  allow: StaffRole[];
}

const NAV_ITEMS: NavItem[] = [
  { to: "/app/dashboard", label: "PHC Dashboard", icon: LayoutDashboard, allow: ["phc_staff", "admin"] },
  { to: "/app/inventory", label: "Inventory Intelligence", icon: Package, allow: ["phc_staff", "admin"] },
  { to: "/app/janmitra", label: "JanMitra — Eligibility Tool", icon: MessageSquareHeart, allow: ["phc_staff", "district_officer", "admin"] },
  { to: "/app/district", label: "District Copilot", icon: Building2, allow: ["district_officer", "admin"] },
];

const ROLE_LABELS: Record<StaffRole, string> = {
  phc_staff: "PHC Staff",
  district_officer: "District Officer",
  admin: "Administrator",
};

function initialsFor(name: string) {
  return name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const { staff } = useAuth();
  const visibleItems = NAV_ITEMS.filter((item) => staff && item.allow.includes(staff.role));

  return (
    <div className="flex h-full flex-col bg-primary-900 text-white">
      <div className="flex items-center gap-2 px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white">
          <img src="/logo.png" alt="SwasthyaAI" className="h-9 w-9" />
        </div>
        <div>
          <p className="font-display text-base font-semibold leading-none">SwasthyaAI</p>
          <p className="mt-0.5 text-xs text-white/60">Staff Portal</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-2" aria-label="Main navigation">
        {visibleItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
                isActive ? "bg-white/15 text-white" : "text-white/70 hover:bg-white/10 hover:text-white"
              )
            }
          >
            <item.icon className="h-4 w-4 shrink-0" aria-hidden />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 p-4">
        <p className="text-xs text-white/50">
          This platform surfaces decision support only — it does not replace clinical or administrative
          judgement.
        </p>
      </div>
    </div>
  );
}

export function StaffShell() {
  const { staff, signOut } = useAuth();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-paper-50">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 md:block">
        <div className="fixed h-screen w-64">
          <SidebarContent />
        </div>
      </aside>

      {/* Mobile sidebar drawer */}
      {mobileNavOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setMobileNavOpen(false)} aria-hidden />
          <div className="absolute inset-y-0 left-0 w-64 animate-in slide-in-from-left">
            <div className="relative h-full">
              <button
                onClick={() => setMobileNavOpen(false)}
                className="absolute right-3 top-4 z-10 text-white/80 hover:text-white"
                aria-label="Close menu"
              >
                <X className="h-5 w-5" />
              </button>
              <SidebarContent onNavigate={() => setMobileNavOpen(false)} />
            </div>
          </div>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-card px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              className="rounded-md p-2 text-ink-900 hover:bg-secondary md:hidden"
              onClick={() => setMobileNavOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            {staff && (
              <Badge variant="info" className="hidden sm:inline-flex">
                {ROLE_LABELS[staff.role]}
              </Badge>
            )}
          </div>

          {staff && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 rounded-full p-1 pr-3 hover:bg-secondary">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>{initialsFor(staff.full_name)}</AvatarFallback>
                  </Avatar>
                  <span className="hidden text-sm font-medium text-ink-900 sm:inline">{staff.full_name}</span>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>
                  <div>
                    <p className="text-sm font-medium">{staff.full_name}</p>
                    <p className="text-xs font-normal text-muted-foreground">{staff.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => signOut()} className="text-destructive-600 focus:text-destructive-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
