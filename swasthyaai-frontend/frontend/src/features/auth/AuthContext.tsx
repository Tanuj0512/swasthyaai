import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { Session } from "@supabase/supabase-js";

import { apiClient, ApiError } from "@/lib/api-client";
import { supabase } from "@/lib/supabase-client";
import type { CurrentStaff } from "@/types/api";

interface AuthContextValue {
  session: Session | null;
  staff: CurrentStaff | null;
  /** True while the initial session/staff-profile lookup is in flight. */
  isLoading: boolean;
  /** Set when a session exists but no matching staff_profiles row was found
   * — a real, actionable state (contact an admin), distinct from "not
   * logged in" or "still loading". */
  profileError: string | null;
  signInWithPassword: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  refetchStaff: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [staff, setStaff] = useState<CurrentStaff | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [profileError, setProfileError] = useState<string | null>(null);

  async function loadStaffProfile() {
    try {
      const { data } = await supabase.auth.getUser();
      if (!data.user) {
        setStaff(null);
        return;
      }
      // The JWT alone only proves identity — role and PHC/district scope
      // live in Postgres (`staff_profiles`), so we ask the backend who this
      // token belongs to rather than guessing anything client-side.
      const profile = await apiClient.get<CurrentStaff>(`/staff/me`);
      setStaff(profile);
      setProfileError(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setStaff(null);
        setProfileError("No staff profile is linked to this account yet. Contact your PHC or district administrator.");
      } else {
        setProfileError("Could not load your staff profile. Please try again.");
      }
    }
  }

  useEffect(() => {
    let mounted = true;

    supabase.auth.getSession().then(async ({ data }) => {
      if (!mounted) return;
      setSession(data.session);
      if (data.session) {
        await loadStaffProfile();
      }
      setIsLoading(false);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange(async (_event, newSession) => {
      setSession(newSession);
      if (newSession) {
        await loadStaffProfile();
      } else {
        setStaff(null);
        setProfileError(null);
      }
    });

    return () => {
      mounted = false;
      subscription.subscription.unsubscribe();
    };
  }, []);

  async function signInWithPassword(email: string, password: string) {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return { error: error?.message ?? null };
  }

  async function signOut() {
    await supabase.auth.signOut();
    setStaff(null);
    setSession(null);
  }

  return (
    <AuthContext.Provider
      value={{ session, staff, isLoading, profileError, signInWithPassword, signOut, refetchStaff: loadStaffProfile }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
