# SwasthyaAI

## AI Decision Intelligence Platform for Public Healthcare

SwasthyaAI is an AI-powered decision intelligence platform designed to improve public healthcare operations while helping citizens access the healthcare schemes they are eligible for.

---

## Problem Statement

Primary Health Centres (PHCs) and Community Health Centres (CHCs) face several operational challenges:

* Medicine stock-outs
* Poor visibility into doctor attendance
* Bed availability issues
* Unpredictable patient footfall
* Lack of proactive resource redistribution
* Citizens being unaware of healthcare schemes and their eligibility

These issues lead to delays, inefficiencies, and reduced access to healthcare benefits.

---

## Our Solution

SwasthyaAI combines operational healthcare intelligence with AI-powered citizen assistance.

The platform focuses on:

* Improving healthcare center operations
* Predicting shortages before they happen
* Supporting district administrators with recommendations
* Helping citizens discover healthcare schemes they are eligible for

---

# Phase 1 Hackathon MVP

## 1. PHC Dashboard

Provides operational visibility into:

* Medicine Inventory
* Doctor Attendance
* Bed Availability
* Patient Footfall
* Critical Alerts

---

## 2. AI Inventory Intelligence

Monitors:

* Current stock levels
* Consumption trends
* Low stock situations
* Forecasted shortages

Provides:

* Stock-out predictions
* Redistribution recommendations
* AI-generated explanations

Example:

> Paracetamol stock is expected to be exhausted within 5 days due to increased patient load. Nearby PHC A can transfer 400 tablets.

---

## 3. JanMitra

### AI-Powered Healthcare Scheme Assistant

JanMitra helps both citizens and hospital staff identify healthcare schemes based on patient profiles.

### Citizen Mode

Citizens can:

* Discover healthcare schemes
* Check eligibility
* Understand benefits
* View required documents
* Learn application steps

### Hospital Staff Mode

Hospital staff can use JanMitra during patient registration.

Using patient information already collected during registration, JanMitra automatically identifies:

* Eligible healthcare schemes
* Benefits available
* Required documents
* Missing information
* Next steps

This transforms PHCs into welfare access centers rather than only treatment centers.

---

## 4. District AI Copilot

District administrators can ask questions such as:

* Which PHCs need attention today?
* Which hospitals are likely to face medicine shortages?
* Where should resources be redistributed?

The AI summarizes district-wide operational issues and recommends actions.

---

## 5. Multilingual Voice Assistant

Supports:

* English
* Hindi

Users can interact with the system using voice instead of typing.

Flow:

Voice Input

↓

Speech-to-Text

↓

AI Understanding

↓

Backend Processing

↓

AI Response

↓

Text-to-Speech

---

# Responsible AI

SwasthyaAI uses AI only where it provides genuine value.

| Feature                       | AI Used | Reason                                                    |
| ----------------------------- | ------- | --------------------------------------------------------- |
| Scheme Eligibility            | ❌       | Rule engine ensures deterministic and auditable decisions |
| Profile Extraction            | ✅       | Natural language understanding                            |
| Scheme Explanation            | ✅       | Simplifies complex government information                 |
| Inventory Forecasting         | ⚠️      | Backend performs calculations while AI explains forecasts |
| Redistribution Recommendation | ✅       | AI analyzes multiple operational factors                  |
| District Copilot              | ✅       | Conversational analysis and summaries                     |
| CRUD Operations               | ❌       | Standard backend logic                                    |

---

## Hallucination Prevention

SwasthyaAI follows a:

**Retrieval → Rules → AI**

architecture.

AI never:

* Determines eligibility
* Invents schemes
* Fabricates stock information
* Modifies records

AI only explains and summarizes verified backend data.

---

## Tech Stack

### Frontend

* React
* Vite
* TypeScript
* Tailwind CSS
* shadcn/ui

### Backend

* FastAPI
* Python
* SQLAlchemy
* Alembic

### Database

* Supabase PostgreSQL

### AI Layer

* Gemini API
* Ollama (local development support)

### Voice and Language

* Google Speech-to-Text
* Google Text-to-Speech
* Google Translation API


### Deployment

* Vercel
* Google Cloud Run
* Supabase

---
## Datasets Used

### Dummy Data

* 10 PHCs
* Medicine inventory
* Doctor attendance
* Bed availability
* Patient footfall

### Government Data

* Central healthcare schemes
* Maharashtra healthcare schemes
* Public healthcare datasets
* Census and demographic data (future)

---

## Future Enhancements

### JanMitra Expansion

* More healthcare schemes
* Document upload and verification
* Application tracking
* Notifications and reminders

### Inventory Intelligence

* Procurement forecasting
* Expiry optimization
* Supplier recommendations

### District AI Copilot

* Disease surveillance
* Predictive analytics
* Budget planning

### Additional Modules

* Telemedicine
* ABDM integration
* Ambulance optimization
* IoT integration
* WhatsApp support
* SMS support
* Citizen Health Profile
* AI Inspection Assistant

---

## Why SwasthyaAI Matters

SwasthyaAI is designed to improve healthcare delivery from both sides:

### For Healthcare Workers

* Better operational visibility
* Reduced stock-outs
* Better resource planning

### For Administrators

* District-wide intelligence
* Proactive interventions
* Better allocation of resources

### For Citizens

* Better access to healthcare schemes
* Reduced confusion
* Improved welfare access

---


## Local Development Setup

### Clone Repository

```bash
git clone <repository-url>
cd swasthyaai
```

### Backend Setup

```bash
cd backend

python -m venv .venv

source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

Configure environment variables:

```env
DATABASE_URL=
GEMINI_API_KEY=
OLLAMA_BASE_URL=
GOOGLE_APPLICATION_CREDENTIALS=
FIREBASE_PROJECT_ID=
```

Run backend:

```bash
uvicorn app.main:app --reload
```

---

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Configure environment variables:

```env
VITE_API_URL=
VITE_FIREBASE_API_KEY=
VITE_GOOGLE_MAPS_KEY=
```

---

## Deployment

### Frontend

Deploy on:

* Vercel

### Backend

Deploy on:

* Google Cloud Run
* Render (development fallback)

### Database

Deploy on:

* Supabase

---
## Built For

**Build with AI: Code for Communities**

Track 03 — Smart Health

AI-Driven Health Center & Supply Chain Management

---

## Team

Built with the vision of making public healthcare more intelligent, proactive, and accessible for every citizen.
