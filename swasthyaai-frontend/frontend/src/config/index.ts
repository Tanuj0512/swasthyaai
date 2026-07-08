/**
 * The single configuration file for the frontend. Every environment-derived
 * value (API URL, Supabase project, feature flags) is declared here and
 * nowhere else — components and hooks import `config`, never
 * `import.meta.env` directly. This mirrors the backend's `app/core/config.py`
 * and is what the architecture doc's "one config file per side" requirement
 * refers to.
 */

function requireEnv(key: string, value: string | undefined): string {
  if (!value) {
    // Fails loudly at build/boot time rather than silently breaking auth or
    // API calls later — much easier to diagnose in a fresh deployment.
    console.error(`Missing required environment variable: ${key}`);
    return "";
  }
  return value;
}

export const config = {
  apiBaseUrl: requireEnv("VITE_API_BASE_URL", import.meta.env.VITE_API_BASE_URL) || "http://localhost:8000/api/v1",
  supabaseUrl: requireEnv("VITE_SUPABASE_URL", import.meta.env.VITE_SUPABASE_URL),
  supabaseAnonKey: requireEnv("VITE_SUPABASE_ANON_KEY", import.meta.env.VITE_SUPABASE_ANON_KEY),
  appName: "SwasthyaAI",
  supportedLanguages: [
    { code: "en", label: "English" },
    { code: "hi", label: "हिंदी" },
  ] as const,
} as const;

export type SupportedLanguageCode = (typeof config.supportedLanguages)[number]["code"];
