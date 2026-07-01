# BeastDesk — AI-Powered Customer Email Automation

An end-to-end system that connects to Gmail, auto-triages incoming customer emails,
drafts grounded replies from a knowledge base (RAG), detects sentiment, escalates
risky threads to a human, and gives the team a full dashboard.

Built to the stack you specified:

| Layer            | Technology                                   |
|-------------------|-----------------------------------------------|
| LLM               | **Groq API** — `llama-3.3-70b-versatile`, temperature `0.5` |
| Embeddings        | **sentence-transformers** (`all-MiniLM-L6-v2`) — free, local, no API key |
| Chunking          | **langchain-text-splitters** (`RecursiveCharacterTextSplitter`) — free |
| Vector DB         | **ChromaDB** (persistent local or hosted HTTP) |
| Backend           | **FastAPI** (Python) |
| Relational DB     | **PostgreSQL on Supabase** |
| Frontend          | **React** (Vite) |
| Frontend hosting  | **Vercel** (free tier) |
| Backend hosting   | **Render** (free tier) |

---

## 1. How it works (end-to-end flow)

```
 Gmail inbox
     │  OAuth2 + polling every 60s (APScheduler)
     ▼
 FastAPI backend (Render)
     │
     ├─► Parse email (sender, subject, body, thread)
     │
     ├─► Groq LLM call #1 — classify_and_score()
     │      → category (legal / product_issue / delivery_issue / return_refund /
     │                   billing / general_enquiry / feedback_praise / spam)
     │      → sentiment (angry / frustrated / sad / neutral / happy)
     │      → intent, is_legal_risk, confidence
     │
     ├─► Embed the email (sentence-transformers, local, free)
     │
     ├─► Query ChromaDB for the top-k most relevant Knowledge Base chunks
     │      (chunks were created at upload time via langchain text splitter
     │       + embedded with the same local model)
     │
     ├─► Groq LLM call #2 — generate_reply()
     │      → tone adapts to sentiment/category, grounded ONLY in retrieved
     │        KB chunks, never invents policy/price/timeline facts
     │
     ├─► Escalation engine (escalation_service.py)
     │      → legal category, low confidence (<70%), VIP customer,
     │        3rd+ angry contact, or any custom rule from Settings
     │      → if triggered: in-app flag + optional Slack/Teams webhook
     │
     └─► Everything persisted to Postgres (Supabase) and surfaced in the
         React dashboard: Inbox, Thread view (approve & send), Analytics,
         Knowledge Base manager, Settings, Admin · Team
```

The same pipeline (`run_pipeline_for_thread`) is used by:
- the **background poller** (`scheduler.py`, every N seconds) for live Gmail traffic, and
- the **manual "re-run AI" endpoint** (`/api/pipeline/run/{thread_id}`) for testing/debugging.

### Reply modes
Drafts are never auto-sent blind — they land in the Inbox as `auto_replied` (low risk)
or `escalated` (needs a human). An agent opens the thread, edits the draft if needed,
and clicks **Approve & Send**, which calls the Gmail API to actually send the email
in the original thread.

---

## 2. Folder structure

```
email-automation/
│
├── backend/                          FastAPI app → deploy to Render
│   ├── app/
│   │   ├── main.py                   App entrypoint, CORS, router registration, admin seeding
│   │   ├── config.py                 Pydantic settings (.env driven)
│   │   ├── database.py               SQLAlchemy engine/session (Supabase Postgres)
│   │   ├── models.py                 ORM models: User, GmailAccount, EmailThread,
│   │   │                             EmailMessage, KnowledgeBaseArticle, EscalationRule, AppSettings
│   │   ├── schemas.py                Pydantic request/response schemas
│   │   ├── scheduler.py              APScheduler job: polls Gmail every N seconds
│   │   │
│   │   ├── core/
│   │   │   └── security.py           Password hashing, JWT issue/verify, role guards
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py               Login, /me, admin user management
│   │   │   ├── gmail.py              OAuth2 start/callback, connected accounts
│   │   │   ├── emails.py             List threads, thread detail, approve & send
│   │   │   ├── knowledge_base.py     Manual + file (PDF/DOCX/TXT) KB upload, retrieval preview
│   │   │   ├── settings_router.py    Escalation rules, app settings
│   │   │   ├── analytics.py          Summary stats, top escalation reasons
│   │   │   └── pipeline.py           Manual pipeline trigger (shared by scheduler)
│   │   │
│   │   └── services/
│   │       ├── groq_service.py       Groq client — classify_and_score(), generate_reply()
│   │       ├── embedding_service.py  Local sentence-transformers embeddings (free)
│   │       ├── chunking_service.py   langchain RecursiveCharacterTextSplitter (free)
│   │       ├── vector_store.py       ChromaDB add/query/delete wrapper
│   │       ├── rag_service.py        Orchestrates classify → retrieve → generate
│   │       ├── escalation_service.py Escalation rule evaluation + Slack ping
│   │       └── gmail_service.py      OAuth, polling, label management, send
│   │
│   ├── requirements.txt
│   ├── render.yaml                   Render Blueprint (web service + persistent disk for Chroma)
│   ├── Procfile                      Alternative to render.yaml (uvicorn start command)
│   └── .env.example
│
├── frontend/                         React (Vite) app → deploy to Vercel
│   ├── src/
│   │   ├── main.jsx                  React root
│   │   ├── App.jsx                   Router + route guards
│   │   ├── index.css                 Design tokens / global styles
│   │   │
│   │   ├── api/
│   │   │   └── client.js             Axios instance, attaches JWT, reads VITE_API_BASE_URL
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.jsx       Login/logout, current user, isAdmin flag
│   │   │
│   │   ├── components/
│   │   │   ├── Sidebar.jsx           Nav (Overview / Inbox / KB / Analytics / Settings / Admin)
│   │   │   ├── ProtectedRoute.jsx    Route guard (auth + admin-only)
│   │   │   └── SentimentBadge.jsx    Emoji + colour-coded sentiment chip
│   │   │
│   │   └── pages/
│   │       ├── Login.jsx
│   │       ├── Dashboard.jsx         Overview: stats + recent threads
│   │       ├── Inbox.jsx             Filterable thread list
│   │       ├── EmailThread.jsx       Full thread + AI draft + approve & send + KB chunks used
│   │       ├── KnowledgeBase.jsx     Add/upload articles, delete, retrieval preview
│   │       ├── Analytics.jsx         Category pie chart, escalation reasons bar chart
│   │       ├── Settings.jsx          Connect Gmail, manage escalation rules
│   │       └── AdminUsers.jsx        Admin-only: add/remove team members
│   │
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── vercel.json                   SPA rewrite rule for client-side routing
│   └── .env.example
│
└── README.md                         You are here
```

---

## 3. Admin vs Agent roles

- **Admin** (seeded from `ADMIN_EMAIL` / `ADMIN_PASSWORD` on first boot):
  connect/disconnect Gmail accounts, manage escalation rules, add/remove team
  members (`/admin/users`), everything an Agent can do.
- **Agent**: views Inbox/Analytics/Knowledge Base, approves & sends AI drafts,
  cannot touch Gmail connections, rules, or the team list.

Role is enforced both in the UI (routes hidden) and in the API (`require_admin`
dependency on sensitive endpoints) — never trust the frontend alone.

---

## 4. Setup & local development

### Prerequisites
- Python 3.11+
- Node 18+
- A Supabase project (Postgres connection string)
- A Groq API key — https://console.groq.com
- A Google Cloud project with the Gmail API enabled and an OAuth 2.0 Web Client ID

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in DATABASE_URL, GROQ_API_KEY, GOOGLE_CLIENT_ID, etc.
uvicorn app.main:app --reload
```
On first boot the app auto-creates tables and seeds one admin user from
`ADMIN_EMAIL` / `ADMIN_PASSWORD`.

### Frontend
```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```
Visit `http://localhost:5173` and log in with the admin credentials above.

---

## 5. Deployment

### Backend → Render
1. Push `backend/` to a GitHub repo.
2. In Render: **New → Blueprint**, point it at the repo (`render.yaml` is auto-detected),
   or create a Web Service manually with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add a **persistent disk** mounted at `chroma_data/` (already declared in `render.yaml`)
   so the ChromaDB index survives restarts/deploys on the free tier.
4. Set all environment variables from `.env.example` in the Render dashboard
   (never commit `.env`).
5. In Google Cloud Console, set the OAuth redirect URI to
   `https://<your-render-app>.onrender.com/api/gmail/oauth/callback`.

### Database → Supabase
1. Create a Supabase project → copy the **connection string** (use the "Session pooler"
   URI for serverless-friendly connections) into `DATABASE_URL`.
2. No manual migrations needed — SQLAlchemy creates tables on first boot.

### Vector DB → ChromaDB
- Default mode (`CHROMA_MODE=persistent`) stores the index on Render's disk — free,
  zero extra infra.
- If you outgrow that, switch to `CHROMA_MODE=http` and point `CHROMA_HTTP_HOST` /
  `CHROMA_HTTP_PORT` at any hosted Chroma server; no code changes required.

### Frontend → Vercel
1. Push `frontend/` to GitHub, import the repo in Vercel.
2. Framework preset: **Vite**. Build command `npm run build`, output dir `dist`.
3. Set `VITE_API_BASE_URL` to your Render backend URL in Vercel's environment variables.
4. `vercel.json` already handles SPA client-side routing rewrites.
5. Update the backend's `FRONTEND_ORIGIN` env var to your Vercel URL so CORS allows it.

---

## 6. Why this stack is free-tier friendly

- **Groq**: generous free-tier rate limits, fast inference, no GPU to manage.
- **sentence-transformers**: runs on CPU, downloaded once, no per-call cost or API key —
  this is what satisfies "free tools for embedding."
- **langchain-text-splitters**: pure Python, no external service — satisfies "free
  tools for chunking."
- **ChromaDB persistent mode**: no separate database service to pay for; lives on
  Render's free disk.
- **Supabase free tier**: 500MB Postgres, enough for thousands of email threads.
- **Render + Vercel free tiers**: backend and frontend both deployable at $0; Render's
  free web service sleeps when idle, which is fine for a support-volume MVP and can be
  upgraded later without code changes.

---

## 7. Extending this scaffold

This repo is a complete, working scaffold of every feature in the project brief
(Gmail OAuth + polling, categorization, sentiment/intent, RAG replies, escalation,
full dashboard, KB manager with bulk upload, settings/rules, admin user management).
Natural next steps before a real production launch:
- Swap polling for Gmail **Pub/Sub push notifications** for near-instant triage.
- Add **Bulk import from Notion/Confluence/Zendesk** connectors in `knowledge_base.py`.
- Add **SLA timers** and working-hours logic in `app_settings`.
- Add automated tests (`pytest` for backend, `vitest` for frontend).
