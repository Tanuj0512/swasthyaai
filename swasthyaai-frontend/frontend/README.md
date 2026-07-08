# SwasthyaAI Frontend

React + Vite + TypeScript + Tailwind + shadcn/ui. See `/docs/ARCHITECTURE.md`
at the repo root for the full system design.

## Setup

```bash
npm install
cp .env.example .env.local
# Edit .env.local: VITE_API_BASE_URL (the backend), VITE_SUPABASE_URL,
# VITE_SUPABASE_ANON_KEY (same Supabase project the backend uses).

npm run dev
```

Opens at `http://localhost:5173`. The citizen-facing pages (`/`, `/schemes`)
need no login. The staff portal (`/login` → `/app/...`) needs a Supabase
Auth user with a matching row in the backend's `staff_profiles` table — see
the backend README for how to create one for local testing.

## Structure

```
src/
├── config/          The ONE frontend config file — reads import.meta.env
├── lib/             API client, Supabase client, TanStack Query client, cn()
├── types/           TypeScript types mirroring the backend's Pydantic schemas
├── components/
│   ├── ui/          shadcn-style primitives (button, card, form, table...)
│   ├── layout/       StaffShell (sidebar+topbar), PublicShell, PageHeader
│   ├── common/        Cross-feature reusables: ErrorState, EmptyState,
│   │                  StatCard, AttentionCard (severity pattern),
│   │                  AIExplanationCard, LanguageToggle, loading skeletons
│   └── charts/        recharts wrappers: stock levels, attention scores,
│                       footfall trend
├── features/
│   ├── auth/          AuthContext, ProtectedRoute, RoleGuard, LoginPage
│   ├── dashboard/      Module 1 — PHC Dashboard
│   ├── inventory/      Module 2 — AI Inventory Intelligence
│   ├── janmitra/       Module 3 — Citizen home, scheme browser, staff
│   │                    eligibility checker
│   ├── district/       Module 4 — District AI Copilot
│   └── voice/          Module 5 — VoiceAssistantWidget (reused by both
│                        citizen and staff contexts)
├── hooks/             One file per module's TanStack Query hooks, plus
│                        usePhcSelection / useDistrictSelection (shared
│                        "own scope vs admin picker" logic) and
│                        useMediaRecorder (browser audio recording)
├── App.tsx            Routing — public shell, staff shell, role guards
└── main.tsx
```

## Design decisions worth knowing

- **TanStack Query, not hand-rolled `useEffect`+`useState`.** Every server
  request goes through a typed hook in `hooks/`, giving consistent loading/
  error/retry/cache behavior for free, and automatic invalidation after
  mutations (e.g. logging medicine consumption refreshes the forecast).
- **shadcn/ui components are hand-authored, not CLI-generated**, because
  this build environment can't reach the shadcn registry. The files are
  the same either way — plain source built on Radix primitives — so
  `npx shadcn add <component>` will work normally in your own environment
  going forward if you want to add more.
- **Voice recording uses the browser's native format** (WebM/Opus in
  Chrome/Edge/Firefox) rather than transcoding to PCM client-side — the
  backend's Speech-to-Text config was set to match (see backend
  `voice_service.py`). Unsupported browsers (older Safari) get a plain-
  language fallback message instead of a broken recorder.
- **Citizen pages never require login**; only `/app/*` (staff/district/
  admin) does, per the architecture decision to keep JanMitra Citizen Mode
  fully public.

## Build

```bash
npm run build   # tsc -b && vite build → dist/
npm run preview
```

## Deployment

Deploy `dist/` to Vercel (or any static host). Set the same three env vars
as `.env.local` in Vercel's project settings. No server-side rendering is
used, so any static host works.
