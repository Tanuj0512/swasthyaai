import { createClient } from "@supabase/supabase-js";

import { config } from "@/config";

/**
 * Single Supabase client instance. Per docs/ARCHITECTURE.md decision #1,
 * Supabase Auth is the ONLY identity provider used by this platform (no
 * Firebase) — this client is used exclusively for staff/district/admin
 * login. Citizen-facing pages never import this.
 */
export const supabase = createClient(config.supabaseUrl, config.supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
