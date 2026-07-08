# SwasthyaAI Backend

FastAPI backend for SwasthyaAI — see `/docs/ARCHITECTURE.md` at the repo root
for the full system design and the reasoning behind each architectural
decision. This README covers only how to run and operate this service.

## Stack

FastAPI · SQLAlchemy 2.0 · Alembic · Supabase Postgres · Supabase Auth (JWT)
· structlog · slowapi (rate limiting) · cachetools (caching) · Gemini/OpenAI/
Ollama behind a provider abstraction.

## Local setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set DATABASE_URL (Supabase or local Postgres — see docker/docker-compose.local.yml),
# SUPABASE_JWT_SECRET, and at minimum GEMINI_API_KEY if you want live AI responses.
# Every endpoint still works with no AI key configured — AI explanation calls
# gracefully fall back to a templated explanation built from verified data.

alembic upgrade head
python -m scripts.seed_db          # populates 10 PHCs, 30 medicines, 7 schemes, etc.

uvicorn app.main:app --reload
```

Interactive API docs: `http://localhost:8000/api/v1/docs`

## Running against a local Postgres instead of Supabase

```bash
docker compose -f docker/docker-compose.local.yml up
```

## Tests

```bash
pytest -v
```

The suite covers the deterministic domain logic (eligibility rule engine,
inventory forecasting/redistribution, district scoring) and the AI
guardrails (prompt-injection detection, output grounding) with unit tests
that need no network access, plus a handful of API-level smoke tests against
the seeded database.

## Re-seeding

```bash
python -m scripts.seed_db          # no-op if already seeded
python -m scripts.seed_db --reset  # truncates and reseeds everything
```

## Switching AI providers

Change one value in `.env`:

```
AI_PROVIDER=gemini   # or: openai | ollama
```

No code changes required — see `app/ai/orchestrator.py`.

## Authentication for local testing

There's no Supabase project in a local sandbox, so to call an authenticated
endpoint you need a JWT signed with the same `SUPABASE_JWT_SECRET` in your
`.env`, and a matching row in `staff_profiles`:

```python
import time, uuid
from jose import jwt

payload = {"sub": str(uuid.uuid4()), "aud": "authenticated", "exp": int(time.time()) + 3600}
print(jwt.encode(payload, "<your SUPABASE_JWT_SECRET>", algorithm="HS256"))
```

```sql
INSERT INTO staff_profiles (id, email, full_name, role, phc_id, district_id, created_at)
VALUES ('<the sub UUID above>', 'test@example.com', 'Test User', 'phc_staff', 1, 1, now());
```

In real deployments this row is created automatically when a staff member
signs up through Supabase Auth (wire that up on the frontend/admin side —
this backend only reads `staff_profiles`, it doesn't create the Supabase
Auth user itself).

## Deployment

Build and push the container, then deploy to Cloud Run:

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/swasthyaai-backend
gcloud run deploy swasthyaai-backend \
  --image gcr.io/PROJECT_ID/swasthyaai-backend \
  --region asia-south1 \
  --min-instances 0 \
  --set-env-vars-file .env.yaml   # or configure via Secret Manager
```

See `docs/ARCHITECTURE.md` section 7 for the full deployment architecture
and the pre-flight checklist (GCP billing, Supabase project, API keys) that
must be done before first deploy.
