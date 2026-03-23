# AI Mental Wellbeing Copilot

### Safety-Governed Multi-Agent Architecture for Personalized Mental Health Support

A production-grade AI mental health support platform built on a **27-agent orchestration pipeline** with safety-first design, enterprise governance, and personalized memory systems. The platform combines LangGraph-driven agent workflows, a FastAPI async backend, and a modern Next.js React frontend to deliver empathetic, context-aware mental wellbeing assistance with robust crisis detection and human oversight.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Multi-Agent Pipeline](#multi-agent-pipeline)
5. [Tech Stack](#tech-stack)
6. [Project Structure](#project-structure)
7. [Getting Started](#getting-started)
8. [Environment Variables](#environment-variables)
9. [API Reference](#api-reference)
10. [Database Schema](#database-schema)
11. [Frontend Application](#frontend-application)
12. [Agent Details](#agent-details)
13. [Services Layer](#services-layer)
14. [Safety & Governance](#safety--governance)
15. [Enterprise Features](#enterprise-features)
16. [Localization](#localization)
17. [Testing](#testing)
18. [Infrastructure & Deployment](#infrastructure--deployment)
19. [Scripts Reference](#scripts-reference)
20. [Contributing](#contributing)

---

## Overview

The AI Mental Wellbeing Copilot is an intelligent conversational system designed to provide personalized mental health support while maintaining strict safety guardrails. Every user message passes through a multi-stage agent pipeline that performs safety triage, retrieves episodic and semantic memories, analyzes tone and intent, routes to specialized therapeutic agents, and composes responses under policy enforcement.

The system is designed around three core principles: **safety first** (crisis detection before anything else), **personalization** (memory and preference learning across sessions), and **transparency** (full audit trails and human review pathways).

---

## Key Features

**Conversational Support:** Real-time chat interface backed by 27 specialized AI agents that collaboratively analyze, reason, and respond to user messages with therapeutic support techniques including CBT reframing, behavioral activation, distress stabilization, reflective listening, sleep recovery, social support coaching, journaling insights, and habit care planning.

**Safety-Governed Pipeline:** Every interaction begins with a safety triage agent. High-risk inputs are immediately routed to crisis escalation, bypassing the standard pipeline. Evidence quality checks, human-readable summaries, and audit logging ensure that all safety-critical decisions are reviewable.

**Memory & Personalization:** A dual-memory architecture (episodic and semantic) with pgvector-powered semantic search enables the system to recall relevant past interactions, learn user preferences over time, and detect longitudinal trends in mood and behavior.

**Enterprise Administration:** Multi-tenant organization support with role-based access control, admin dashboards for safety event review, care plan oversight, policy configuration, audit log inspection, and enterprise-wide analytics.

**External Integrations:** Pluggable integration framework for syncing with external health and wellness data sources, with job-based sync orchestration and connection management.

**Localization:** Multi-language support with configurable language preferences, translation management through the admin interface, and fallback language handling.

**Journaling & Check-ins:** Structured journaling with theme extraction and insight generation, plus daily wellness check-ins with trend tracking.

**Care & Action Plans:** Personalized care plans with milestone tracking, action plan management, and automated follow-up scheduling via durable Temporal workflows.

---

## Architecture

The system follows a modular monorepo architecture with clear separation between the API backend, web frontend, shared contracts, and infrastructure.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Next.js Frontend (Port 3000)                 │
│  Dashboard │ Chat │ Journal │ Insights │ Plans │ Admin │ Settings   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTP/REST
┌────────────────────────────────▼────────────────────────────────────┐
│                     FastAPI Backend (Port 8000)                      │
│                                                                      │
│  ┌──────────┐  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Routes   │  │  Services  │  │  Orchestration│  │   Agents     │  │
│  │  (API)    │──│  (Domain)  │──│  (LangGraph)  │──│  (27 total)  │  │
│  └──────────┘  └────────────┘  └──────────────┘  └──────────────┘  │
│                                                                      │
│  ┌──────────┐  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Models   │  │ Repositories│  │  Schemas     │  │  Temporal    │  │
│  │  (ORM)    │  │  (Data)    │  │  (Pydantic)  │  │  (Workflows) │  │
│  └──────────┘  └────────────┘  └──────────────┘  └──────────────┘  │
└───────┬──────────────────┬──────────────────────────┬───────────────┘
        │                  │                          │
   ┌────▼────┐      ┌─────▼─────┐             ┌─────▼──────┐
   │PostgreSQL│      │   Redis    │             │  Temporal   │
   │16+pgvector│     │   7.x     │             │  (Optional) │
   └──────────┘      └───────────┘             └────────────┘
```

**Design Patterns:**

- **Multi-Agent Orchestration** — LangGraph state machine coordinates 27 agents through conditional routing based on safety assessment, user context, and intent classification.
- **Async-First** — All database, cache, and HTTP operations use async/await for high concurrency.
- **Repository Pattern** — Data access abstracted through repository classes, separating domain logic from persistence.
- **Dependency Injection** — FastAPI's `Depends` mechanism for service composition and testability.
- **Durable Workflows** — Temporal-based follow-up scheduling survives process restarts and handles retries.
- **Event Sourcing (Partial)** — Care plans and safety events maintain event histories for auditability.

---

## Multi-Agent Pipeline

Every user message flows through the following orchestrated pipeline, defined in `apps/api/src/mental_wellbeing_api/orchestration/graph.py`:

```
User Message
     │
     ▼
┌─────────────────┐
│  Safety Triage   │──── High Risk ────┐
│  Agent           │                    │
└────────┬────────┘                    │
         │ Low Risk                     │
         ▼                              ▼
┌─────────────────┐          ┌──────────────────┐
│ Episodic Memory  │          │ Crisis Escalation │
│ Retrieval        │          └────────┬─────────┘
└────────┬────────┘                    │
         ▼                              │
┌─────────────────┐                    │
│ Semantic Memory  │                    │
│ Retrieval        │                    │
└────────┬────────┘                    │
         ▼                              │
┌─────────────────┐                    │
│ Session Context  │                    │
│ Builder          │                    │
└────────┬────────┘                    │
         ▼                              │
┌─────────────────┐                    │
│ Input Structuring│                    │
└────────┬────────┘                    │
         ▼                              │
┌─────────────────┐                    │
│ Tone & Emotion   │                    │
│ Analyzer         │                    │
└────────┬────────┘                    │
         ▼                              │
┌─────────────────┐                    │
│ Intent Router    │                    │
└────────┬────────┘                    │
         ▼                              │
┌─────────────────┐                    │
│ Support Mode     │                    │
│ Router           │                    │
└────────┬────────┘                    │
         ▼                              │
┌─────────────────────────────────┐    │
│     Specialist Agent Selection   │    │
│                                  │    │
│  • Reflective Support            │    │
│  • Distress Stabilization        │    │
│  • Behavioral Activation         │    │
│  • CBT Reframing                 │    │
│  • Sleep Recovery                │    │
│  • Social Support                │    │
│  • Journaling Insight            │    │
│  • Habit Care Planning           │    │
└────────────┬────────────────────┘    │
              │                         │
              ▼                         │
┌─────────────────┐                    │
│ Trend Analysis   │◄──────────────────┘
└────────┬────────┘
         ▼
┌─────────────────┐
│ Preference       │
│ Learning         │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Follow-up        │
│ Planner          │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Evidence Quality │
│ Check            │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Human Summary    │
│ Generator        │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Audit Logger     │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Response         │
│ Composer         │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Policy Guardrails│
└────────┬────────┘
         ▼
┌─────────────────┐
│ Execution        │
│ Finalizer        │
└────────┬────────┘
         ▼
    Final Response
```

The pipeline state is managed through `AgentRuntimeState`, a TypedDict with approximately 100 fields that tracks everything from user input and safety assessments to memory retrievals, emotional analysis, specialist outputs, and final compositions.

---

## Tech Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| FastAPI | 0.115+ | Web framework |
| Uvicorn | Latest | ASGI server |
| SQLAlchemy | 2.0+ | Async ORM |
| Alembic | 1.13+ | Database migrations |
| PostgreSQL | 16 | Primary database |
| pgvector | 0.3.6+ | Vector similarity search |
| Redis | 7.x | Caching layer |
| LangGraph | 0.2.14+ | Agent orchestration |
| LangChain | 0.3.0+ | LLM toolkit |
| OpenAI | 1.43+ | LLM provider (gpt-4o-mini default) |
| Ollama | 0.4.7+ | Local LLM support |
| Temporal | 1.8+ | Durable workflows |
| Pydantic | 2.8+ | Data validation and settings |
| structlog | 24.4+ | Structured JSON logging |
| OpenTelemetry | 1.36+ | Observability |
| httpx | 0.27+ | Async HTTP client |
| tenacity | 9.0+ | Retry logic |
| orjson | 3.10+ | Fast JSON serialization |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| Next.js | 15.3.4 | React framework (App Router) |
| React | 18.3.1 | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.4+ | Utility-first styling |
| Radix UI | Latest | Accessible component primitives |
| React Query | 5.83+ | Server state management |
| React Hook Form | 7.61+ | Form handling |
| Framer Motion | 12.37+ | Animations |
| Zod | 3.25+ | Schema validation |
| Recharts | 2.15+ | Data visualization |
| Lucide React | 0.462+ | Icon library |
| Sonner | Latest | Toast notifications |

### Infrastructure

| Technology | Purpose |
|---|---|
| Docker & Docker Compose | Containerization |
| Alembic | Schema migrations |
| Temporal Server | Workflow orchestration (optional) |

---

## Project Structure

```
.
├── apps/
│   ├── api/                                    # FastAPI backend
│   │   ├── src/mental_wellbeing_api/
│   │   │   ├── main.py                         # Application entry point
│   │   │   ├── core/
│   │   │   │   ├── config.py                   # Pydantic settings configuration
│   │   │   │   ├── logging.py                  # Structured logging setup
│   │   │   │   └── telemetry.py                # OpenTelemetry integration
│   │   │   ├── db/
│   │   │   │   ├── base.py                     # SQLAlchemy declarative base
│   │   │   │   └── session.py                  # Async engine and session factory
│   │   │   ├── api/
│   │   │   │   ├── deps.py                     # Dependency injection helpers
│   │   │   │   └── routes/
│   │   │   │       ├── health.py               # Health checks
│   │   │   │       ├── auth.py                 # Authentication
│   │   │   │       ├── users.py                # User management
│   │   │   │       ├── conversations.py        # Chat sessions and messages
│   │   │   │       ├── agent_runtime.py        # Agent execution endpoints
│   │   │   │       ├── journal_entries.py       # Journal CRUD
│   │   │   │       ├── check_ins.py            # Wellness check-ins
│   │   │   │       ├── care_plans.py           # Care plan lifecycle
│   │   │   │       ├── action_plans.py         # Action plan management
│   │   │   │       ├── follow_ups.py           # Follow-up scheduling
│   │   │   │       ├── memory_trends.py        # Memory and trend APIs
│   │   │   │       ├── safety_flags.py         # Safety flag management
│   │   │   │       ├── admin.py                # Admin dashboard
│   │   │   │       ├── admin_settings.py       # Enterprise settings
│   │   │   │       ├── admin_enterprise.py     # Organization management
│   │   │   │       ├── admin_integrations.py   # Integration management
│   │   │   │       ├── admin_external_integrations.py
│   │   │   │       ├── enterprise.py           # Enterprise features
│   │   │   │       ├── external_integrations.py # External sync
│   │   │   │       └── localization.py         # Multi-language support
│   │   │   ├── agents/                         # 27 specialized agents
│   │   │   │   ├── safety_triage_agent.py
│   │   │   │   ├── crisis_escalation_agent.py
│   │   │   │   ├── episodic_memory_agent.py
│   │   │   │   ├── semantic_memory_retriever_agent.py
│   │   │   │   ├── session_context_builder_agent.py
│   │   │   │   ├── input_structuring_agent.py
│   │   │   │   ├── tone_emotion_analyzer_agent.py
│   │   │   │   ├── intent_router_agent.py
│   │   │   │   ├── support_mode_router_agent.py
│   │   │   │   ├── supervisor_agent.py
│   │   │   │   ├── reflective_agent.py
│   │   │   │   ├── distress_stabilization_agent.py
│   │   │   │   ├── behavioral_activation_agent.py
│   │   │   │   ├── cbt_reframing_agent.py
│   │   │   │   ├── sleep_recovery_agent.py
│   │   │   │   ├── social_support_agent.py
│   │   │   │   ├── journaling_insight_agent.py
│   │   │   │   ├── habit_care_plan_agent.py
│   │   │   │   ├── trend_analyzer_agent.py
│   │   │   │   ├── preference_learning_agent.py
│   │   │   │   ├── follow_up_planner_agent.py
│   │   │   │   ├── evidence_quality_agent.py
│   │   │   │   ├── human_summary_generator_agent.py
│   │   │   │   ├── audit_agent.py
│   │   │   │   ├── response_composer_agent.py
│   │   │   │   ├── policy_guardrail_agent.py
│   │   │   │   └── execution_finalize_agent.py
│   │   │   ├── orchestration/
│   │   │   │   ├── graph.py                    # LangGraph workflow definition
│   │   │   │   ├── state.py                    # AgentRuntimeState (~100 fields)
│   │   │   │   └── runtime.py                  # State utilities
│   │   │   ├── services/                       # 35+ domain services
│   │   │   ├── models/                         # 32 SQLAlchemy ORM models
│   │   │   ├── schemas/                        # Pydantic request/response schemas
│   │   │   ├── repositories/                   # Data access layer
│   │   │   ├── policies/                       # Policy enforcement modules
│   │   │   └── temporal/
│   │   │       ├── client.py
│   │   │       ├── worker.py
│   │   │       ├── workflows/
│   │   │       │   └── follow_up_workflow.py
│   │   │       └── activities/
│   │   │           └── follow_up_activities.py
│   │   ├── alembic/                            # Database migrations
│   │   ├── tests/                              # Backend test suite
│   │   ├── pyproject.toml                      # Python dependencies
│   │   └── .env.example                        # Environment template
│   │
│   └── web/                                    # Next.js frontend
│       ├── src/
│       │   ├── app/                            # Pages (App Router)
│       │   │   ├── page.tsx                    # Landing page
│       │   │   ├── layout.tsx                  # Root layout
│       │   │   ├── auth/page.tsx               # Authentication
│       │   │   ├── app/                        # Main app pages
│       │   │   │   ├── page.tsx                # Dashboard
│       │   │   │   ├── chat/page.tsx           # Chat interface
│       │   │   │   ├── journal/page.tsx        # Journal entries
│       │   │   │   ├── insights/page.tsx       # Personal insights
│       │   │   │   ├── programs/page.tsx       # Support programs
│       │   │   │   ├── plans/page.tsx          # Care plans
│       │   │   │   ├── safety/page.tsx         # Safety resources
│       │   │   │   ├── settings/page.tsx       # User settings
│       │   │   │   ├── integrations/page.tsx   # External integrations
│       │   │   │   ├── checkin/page.tsx        # Wellness check-ins
│       │   │   │   └── onboarding/page.tsx     # Onboarding flow
│       │   │   └── admin/                      # 16 admin pages
│       │   ├── components/
│       │   │   ├── ui/                         # 45+ Radix UI components
│       │   │   └── layout/                     # AppLayout, MobileNav
│       │   ├── lib/                            # 17 API client libraries
│       │   ├── config/                         # Environment config
│       │   ├── providers/                      # React Query provider
│       │   └── types/                          # TypeScript type definitions
│       ├── public/                             # Static assets
│       ├── test/                               # Frontend tests
│       ├── package.json
│       ├── next.config.mjs
│       ├── tailwind.config.ts
│       └── tsconfig.json
│
├── packages/
│   ├── contracts/                              # Shared API contracts
│   └── docs-shared/                            # Shared documentation
│
├── infra/
│   ├── docker/
│   │   ├── api.Dockerfile
│   │   └── web.Dockerfile
│   └── scripts/
│       ├── bootstrap.sh                        # Initial setup
│       ├── dev-up.sh                           # Start dev environment
│       ├── dev-down.sh                         # Tear down dev environment
│       └── backend_v1_smoke.sh                 # Smoke tests
│
├── policies/                                   # Policy configurations
├── prompts/                                    # LLM prompt templates
├── docs/                                       # Documentation
├── tests/                                      # Integration & smoke tests
├── docker-compose.yml
├── .editorconfig
├── .env.example
├── .nvmrc                                      # Node 20
└── .gitignore
```

---

## Getting Started

### Prerequisites

- **Docker & Docker Compose** — for PostgreSQL and Redis
- **Python 3.11+** — backend runtime
- **Node.js 20** — frontend runtime (see `.nvmrc`)
- **npm** — frontend package manager
- **OpenAI API key** — for LLM-powered agents (or Ollama for local models)

### Quick Start

**1. Clone and Bootstrap**

```bash
git clone <repository-url>
cd ai-mental-wellbeing-copilot
./infra/scripts/bootstrap.sh
```

The bootstrap script installs Python dependencies in a virtual environment and installs frontend packages.

**2. Start Infrastructure**

```bash
./infra/scripts/dev-up.sh
```

This starts PostgreSQL 16 (with pgvector) on port 55432 and Redis 7 on port 6379 via Docker Compose.

**3. Configure Environment**

```bash
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env and add your OPENAI_API_KEY
```

**4. Run Database Migrations**

```bash
cd apps/api
source .venv/bin/activate
alembic upgrade head
```

**5. Start the Backend**

```bash
cd apps/api
source .venv/bin/activate
python -m uvicorn mental_wellbeing_api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

**6. Start the Frontend**

```bash
cd apps/web
npm install
npm run dev
```

The web app will be available at `http://localhost:3000`.

**7. Verify Setup**

```bash
./infra/scripts/backend_v1_smoke.sh
```

### Tear Down

```bash
./infra/scripts/dev-down.sh
```

---

## Environment Variables

### Application Settings

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `local` | Environment (local, staging, production) |
| `APP_NAME` | `AI Mental Wellbeing Copilot API` | Application name |
| `APP_VERSION` | `0.1.0` | Application version |
| `API_V1_PREFIX` | `/api/v1` | API route prefix |
| `APP_DEBUG` | `true` | Debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |

### Database

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | `55432` | PostgreSQL port |
| `POSTGRES_DB` | `mental_wellbeing` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |

### Cache

| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database number |

### LLM Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | **Required.** OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model for agent inference |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_DEFAULT_MODEL` | `llama3.2` | Default Ollama model |

### Authentication & RBAC

| Variable | Default | Description |
|---|---|---|
| `AUTH_MODE` | `development_bypass` | Auth mode (development_bypass, session) |
| `AUTH_SESSION_SECRET` | — | Session signing secret |
| `AUTH_ACCESS_TOKEN_TTL_MINUTES` | `480` | Token TTL in minutes |
| `AUTH_HEADER_NAME` | `Authorization` | Auth header name |
| `AUTH_COOKIE_NAME` | `mwc_session` | Session cookie name |
| `AUTH_ALLOW_DEV_BOOTSTRAP` | `true` | Allow dev user bootstrap |
| `AUTH_ALLOW_DEV_HEADERS` | `true` | Allow dev auth headers |

### Temporal Workflows

| Variable | Default | Description |
|---|---|---|
| `TEMPORAL_ENABLED` | `false` | Enable Temporal integration |
| `TEMPORAL_NAMESPACE` | `default` | Temporal namespace |
| `TEMPORAL_TASK_QUEUE` | `mental-wellbeing-followups` | Task queue name |
| `SCHEDULER_BACKEND` | `local_contract` | Scheduler backend type |

### Enterprise

| Variable | Default | Description |
|---|---|---|
| `ENTERPRISE_DEFAULT_ORG_NAME` | `Default Enterprise` | Default org name |
| `ENTERPRISE_DEFAULT_ORG_SLUG` | `default-enterprise` | Default org slug |
| `ENTERPRISE_ADMIN_ROLE_NAME` | `platform_admin` | Admin role name |

### Observability

| Variable | Default | Description |
|---|---|---|
| `OTEL_ENABLED` | `false` | Enable OpenTelemetry |
| `OTEL_SERVICE_NAME` | `mental-wellbeing-api` | Service name for traces |

### Storage

| Variable | Default | Description |
|---|---|---|
| `STORAGE_PROVIDER` | `local` | Storage backend (local, s3) |
| `STORAGE_LOCAL_ROOT` | `.runtime/storage` | Local storage path |
| `STORAGE_PUBLIC_BASE_URL` | — | Public URL for file access |

### Queue & Reliability

| Variable | Default | Description |
|---|---|---|
| `QUEUE_MAX_ATTEMPTS` | `3` | Max retry attempts |
| `QUEUE_DEAD_LETTER_ENABLED` | `true` | Enable dead letter queue |
| `QUEUE_MAX_INFLIGHT` | `100` | Max concurrent jobs |
| `QUEUE_VISIBILITY_TIMEOUT_SECONDS` | `900` | Job visibility timeout |
| `QUEUE_ENFORCE_IDEMPOTENCY` | `true` | Enforce idempotent operations |

### Frontend

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | Backend API URL |

### CORS

| Variable | Default | Description |
|---|---|---|
| `CORS_ALLOW_ORIGINS` | — | Comma-separated allowed origins |

---

## API Reference

**Base URL:** `http://localhost:8000/api/v1`

### Health & Status

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root info (app name, version, status) |
| `GET` | `/health` | Health status |
| `GET` | `/health/dependencies` | PostgreSQL and Redis connectivity |

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login` | User login |
| `POST` | `/auth/logout` | User logout |
| `GET` | `/auth/session` | Current session info |

### Users

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users/me` | Get current user profile |
| `PUT` | `/users/me` | Update user profile |
| `GET` | `/users/{id}` | Get user by ID |

### Conversations

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/conversations/sessions` | Create new chat session |
| `GET` | `/conversations/sessions` | List user sessions |
| `GET` | `/conversations/sessions/{id}` | Get session details |
| `POST` | `/conversations/messages` | Send a message |
| `GET` | `/conversations/messages` | Get messages for a session |

### Agent Runtime

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/agent-runtime/smoke` | Execute full agent pipeline |
| `POST` | `/agent-runtime/safety-evaluate` | Safety-only evaluation |

### Journal Entries

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/journal-entries` | Create journal entry |
| `GET` | `/journal-entries` | List journal entries |
| `GET` | `/journal-entries/{id}` | Get journal entry |
| `PUT` | `/journal-entries/{id}` | Update journal entry |
| `DELETE` | `/journal-entries/{id}` | Delete journal entry |

### Check-ins

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/check-ins` | Create check-in |
| `GET` | `/check-ins` | List check-ins |

### Care Plans

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/care-plans` | Create care plan |
| `GET` | `/care-plans` | List care plans |
| `GET` | `/care-plans/{id}` | Get care plan details |
| `PUT` | `/care-plans/{id}` | Update care plan |

### Action Plans

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/action-plans` | Create action plan |
| `GET` | `/action-plans` | List action plans |
| `PUT` | `/action-plans/{id}` | Update action plan |

### Follow-ups

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/follow-ups` | Schedule follow-up |
| `GET` | `/follow-ups` | List follow-ups |
| `PUT` | `/follow-ups/{id}` | Update follow-up |

### Safety Flags

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/safety-flags` | Create safety flag |
| `GET` | `/safety-flags` | List safety flags |
| `GET` | `/safety-flags/review-queue` | Get review queue |

### Memory & Trends

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/memory-trends/recall` | Retrieve relevant memories |
| `GET` | `/memory-trends/trends` | Get trend analysis |

### Admin

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/dashboard` | Admin dashboard data |
| `GET` | `/admin/safety-events` | Safety event listing |
| `GET` | `/admin/analytics` | Organization analytics |
| `GET` | `/admin/audit-logs` | Audit log history |
| `PUT` | `/admin/settings` | Update admin settings |

### Localization

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/localization/languages` | Available languages |
| `GET` | `/localization/translations` | Get translations |
| `PUT` | `/localization/translations` | Update translations |

### External Integrations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/external-integrations` | List integrations |
| `POST` | `/external-integrations/connect` | Create connection |
| `POST` | `/external-integrations/sync` | Trigger sync |

---

## Database Schema

The application uses 32 SQLAlchemy models organized across the following domains. All models use UUID primary keys and include `created_at` / `updated_at` timestamps.

### Core Entities

**User (`user.py`)** — User accounts with UUID primary keys, linked to profiles and preferences. `UserProfile` stores extended information. `UserPreference` tracks learned preference data for personalization.

**Organization (`organization.py`)** — Multi-tenant enterprise organizations. `OrgMember` links users to orgs with `OrgRole` for role-based access.

**AuthSession (`auth_session.py`)** — Tracks active authentication sessions with token management.

### Conversation & Memory

**ConversationSession / ConversationMessage (`conversation.py`)** — Chat sessions with threaded messages. Messages store role, content, and metadata for the full conversation history.

**MemoryChunk (`memory_chunk.py`)** — Vector-embedded memory fragments using pgvector for semantic similarity search. Supports both episodic (event-based) and semantic (meaning-based) memory types.

**JournalEntry / JournalTheme (`journal_entry.py`)** — Structured journal entries with extracted themes for insight generation.

**AgentTrace (`agent_trace.py`)** — Execution traces for every agent invocation, enabling debugging and performance analysis.

### Safety & Governance

**SafetyFlag (`safety_flag.py`)** — Risk flags raised during safety triage, categorized by severity level.

**SafetyReview (`safety_review.py`)** — Human review records for safety flags, tracking reviewer decisions and notes.

**SafetyEvent (`safety_event.py`)** — Immutable safety event records for compliance auditing.

**AuditLog (`audit_log.py`)** — Comprehensive audit trail for all significant system actions.

**InterventionLog (`intervention_log.py`)** — Records of safety interventions taken by the system.

**ConfigAudit (`admin_config_audit.py`)** — Tracks admin configuration changes.

### Planning & Follow-ups

**CarePlan / CarePlanEvent (`care_plan.py`)** — Personalized care plans with event-sourced progress tracking.

**ActionPlan (`action_plan.py`)** — Discrete action items with status tracking.

**FollowUpPlan / FollowUpEvent (`follow_up_plan.py`)** — Scheduled follow-up reminders with Temporal workflow integration.

**TrendSnapshot (`trend_snapshot.py`)** — Point-in-time snapshots of user trend data for longitudinal analysis.

### External & Integration

**ExternalSignal (`external_signal.py`)** — Inbound signals from external integrations.

**ExternalSyncJob (`external_sync_job.py`)** — Job tracking for external data synchronization.

**ExternalIntegrationConnection (`external_integration_connection.py`)** — Managed connections to external providers.

**StoredArtifact (`stored_artifact.py`)** — File and artifact storage metadata.

**CheckIn (`check_in.py`)** — Daily wellness check-in records.

**TriggerCluster (`trigger_cluster.py`)** — Grouped trigger patterns for trend detection.

**EnterpriseSetting (`enterprise_setting.py`)** — Organization-level configuration settings.

---

## Frontend Application

### User-Facing Pages

**Dashboard** (`app/page.tsx`) — The main hub showing mood trends, recent memory highlights, active action plans, and quick-access navigation. Animated with Framer Motion for smooth transitions.

**Chat** (`app/chat/page.tsx`) — Real-time conversational interface that sends messages through the full 27-agent pipeline. Displays AI responses with emotional awareness and therapeutic support.

**Journal** (`app/journal/page.tsx`) — Create, view, and manage journal entries. The system extracts themes and generates insights from journal content using the journaling insight agent.

**Insights** (`app/insights/page.tsx`) — Visual trend analysis showing mood patterns, behavioral trends, and personalized observations generated by the trend analysis agents.

**Programs** (`app/programs/page.tsx`) — Browse and enroll in structured support programs (behavioral activation, sleep recovery, social skills, etc.).

**Plans** (`app/plans/page.tsx`) — View and manage care plans with milestone tracking, progress visualization, and action item management.

**Safety** (`app/safety/page.tsx`) — Access crisis resources, emergency contacts, and safety information. Displayed prominently when safety flags are raised.

**Settings** (`app/settings/page.tsx`) — Configure profile information, notification preferences, language settings, and privacy controls.

**Integrations** (`app/integrations/page.tsx`) — Connect external health and wellness apps for data synchronization.

**Check-in** (`app/checkin/page.tsx`) — Guided daily wellness check-ins that feed into trend analysis and personalization.

**Onboarding** (`app/onboarding/page.tsx`) — New user onboarding flow collecting preferences and baseline information.

### Admin Pages

The admin section provides 16 dedicated pages for platform governance: Dashboard, Analytics, Safety Events, Cases, Escalations, Care Plans, Policy, Audit, Policy History, Decision Paths, Reviewer Dashboard, Localization, Settings, External Integrations, Enterprise Analytics, and Flagged Content.

### Component Library

The frontend uses 45+ UI components built on Radix UI primitives with Tailwind CSS styling, including: Accordion, Alert, AlertDialog, Avatar, Badge, Breadcrumb, Button, Calendar, Card, Carousel, Chart, Checkbox, Collapsible, Command, Dialog, Drawer, DropdownMenu, Form, HoverCard, Input, Label, Menubar, NavigationMenu, Pagination, Popover, Progress, RadioGroup, ResizablePanel, ScrollArea, Select, Separator, Sheet, Sidebar, Skeleton, Slider, Sonner (Toasts), Switch, Table, Tabs, Textarea, Toggle, ToggleGroup, and Tooltip.

---

## Agent Details

Each of the 27 agents is a self-contained Python module in `apps/api/src/mental_wellbeing_api/agents/`. Every agent receives the shared `AgentRuntimeState` and returns an updated state after performing its specialized task.

| Agent | File | Responsibility |
|---|---|---|
| **Safety Triage** | `safety_triage_agent.py` | First-pass risk assessment of every user message. Classifies risk level (low, medium, high, critical) and sets routing flags. |
| **Crisis Escalation** | `crisis_escalation_agent.py` | Handles high-risk inputs with crisis protocols, resource provision, and escalation to human reviewers. |
| **Episodic Memory** | `episodic_memory_agent.py` | Retrieves relevant past interactions and events from the user's episodic memory store. |
| **Semantic Memory** | `semantic_memory_retriever_agent.py` | Performs vector similarity search to find semantically related memory chunks. |
| **Session Context** | `session_context_builder_agent.py` | Assembles the full context window from memories, session history, and user profile data. |
| **Input Structuring** | `input_structuring_agent.py` | Normalizes and structures the raw user input for downstream processing. |
| **Tone & Emotion** | `tone_emotion_analyzer_agent.py` | Analyzes emotional tone, sentiment, and affective state of the user message. |
| **Intent Router** | `intent_router_agent.py` | Classifies user intent to determine appropriate support modality. |
| **Support Mode Router** | `support_mode_router_agent.py` | Routes to the appropriate specialist agent based on intent and emotional state. |
| **Supervisor** | `supervisor_agent.py` | Orchestrates specialist agent selection and coordination. |
| **Reflective Support** | `reflective_agent.py` | Provides empathetic reflective listening and validation. |
| **Distress Stabilization** | `distress_stabilization_agent.py` | Applies grounding and stabilization techniques for acute distress. |
| **Behavioral Activation** | `behavioral_activation_agent.py` | Suggests behavioral activation strategies for depression and low motivation. |
| **CBT Reframing** | `cbt_reframing_agent.py` | Applies cognitive behavioral therapy reframing techniques to negative thought patterns. |
| **Sleep Recovery** | `sleep_recovery_agent.py` | Provides sleep hygiene guidance and recovery strategies. |
| **Social Support** | `social_support_agent.py` | Coaches on social connection, relationship skills, and support-seeking. |
| **Journaling Insight** | `journaling_insight_agent.py` | Generates insights from journal entries and writing patterns. |
| **Habit Care Planning** | `habit_care_plan_agent.py` | Creates and manages habit-forming care plans. |
| **Trend Analyzer** | `trend_analyzer_agent.py` | Detects longitudinal patterns in mood, behavior, and engagement. |
| **Preference Learning** | `preference_learning_agent.py` | Updates the user preference model based on interaction feedback. |
| **Follow-up Planner** | `follow_up_planner_agent.py` | Schedules appropriate follow-up check-ins and reminders. |
| **Evidence Quality** | `evidence_quality_agent.py` | Validates the quality and appropriateness of agent reasoning and evidence. |
| **Human Summary** | `human_summary_generator_agent.py` | Generates human-readable summaries for reviewer dashboards. |
| **Audit Logger** | `audit_agent.py` | Records comprehensive audit trails for compliance. |
| **Response Composer** | `response_composer_agent.py` | Assembles the final user-facing response from all agent outputs. |
| **Policy Guardrail** | `policy_guardrail_agent.py` | Enforces safety policies and content guidelines on the composed response. |
| **Execution Finalizer** | `execution_finalize_agent.py` | Finalizes the pipeline execution, persists state, and emits events. |

---

## Services Layer

The services layer (`apps/api/src/mental_wellbeing_api/services/`) contains 35+ domain service classes that encapsulate business logic. Key services include:

**`agent_runtime_service.py`** — The primary orchestration service that initializes `AgentRuntimeState`, invokes the LangGraph workflow, and processes results.

**`safety_service.py`** — Risk detection and safety flag management. Processes safety triage results, creates flags, and manages the review queue.

**`memory_service.py`** — Memory storage and retrieval using pgvector. Handles both episodic and semantic memory operations with embedding-based similarity search.

**`llm_service.py`** — Abstraction layer for LLM interactions. Supports OpenAI and Ollama providers with configurable model selection and retry logic.

**`embeddings_service.py`** — Vector embedding generation for memory chunks and semantic search queries.

**`care_plan_service.py`** — Full lifecycle management for care plans including creation, progress tracking, event recording, and completion.

**`follow_up_service.py`** — Follow-up scheduling with support for both local contract-based scheduling and Temporal durable workflows.

**`trend_intelligence_service.py`** — Trend detection and pattern analysis across check-ins, journal entries, and conversation data.

**`preference_service.py`** — User preference learning and retrieval. Maintains a preference model updated by the preference learning agent.

**`journaling_intelligence_service.py`** — Journal analysis including theme extraction, sentiment tracking, and insight generation.

**`auth_service.py`** — Authentication handling with configurable auth modes (development bypass, session-based).

**`rbac_service.py`** — Role-based access control enforcement. Manages roles, permissions, and authorization checks.

**`enterprise_admin_analytics_service.py`** — Organization-wide analytics aggregation and reporting.

**`external_integrations_service.py`** — External provider connection management and data synchronization orchestration.

**`localization_service.py`** — Translation management, language detection, and localized content delivery.

**`storage_service.py`** — File and artifact storage with pluggable backends (local filesystem, S3).

**`secret_manager_service.py`** — Secrets management with configurable backends (environment variables, managed secret stores).

**`scheduler_service.py`** — Task scheduling abstraction supporting local and distributed scheduling backends.

**`temporal_contract_service.py`** — Temporal workflow client for durable follow-up scheduling.

---

## Safety & Governance

Safety is the foundational design principle of the platform. The system implements multiple layers of protection:

**Layer 1 — Safety Triage (Agent):** Every user message is assessed for risk before any other processing. The safety triage agent classifies messages into risk levels (low, medium, high, critical) and sets routing flags that determine the pipeline path.

**Layer 2 — Crisis Escalation (Agent):** High-risk messages bypass the standard pipeline and are routed directly to the crisis escalation agent, which provides immediate crisis resources and escalates to human reviewers.

**Layer 3 — Evidence Quality (Agent):** Before any response is composed, the evidence quality agent validates that the reasoning chain and supporting evidence meet quality thresholds.

**Layer 4 — Policy Guardrails (Agent):** The composed response passes through the policy guardrail agent, which enforces content policies, removes harmful content, and ensures responses align with therapeutic guidelines.

**Layer 5 — Human Review:** Safety flags create entries in the reviewer dashboard, enabling human clinicians to review flagged interactions, approve or modify responses, and update safety policies.

**Layer 6 — Audit Trail:** Every agent execution, safety decision, and configuration change is recorded in the audit log for compliance and accountability.

**Admin Tools:** The admin interface provides dashboards for safety events, escalation queues, case management, policy configuration, decision path visualization, and audit log inspection.

---

## Enterprise Features

**Multi-Tenancy:** Organizations are first-class entities with their own settings, members, roles, and data isolation.

**Role-Based Access Control (RBAC):** Configurable roles (platform admin, org admin, reviewer, clinician, user) with granular permissions for each API endpoint and admin function.

**Organization Management:** Create and manage organizations, invite members, assign roles, and configure org-level settings through the admin enterprise endpoints.

**Enterprise Analytics:** Cross-organization analytics for platform operators, including usage metrics, safety statistics, and engagement trends.

**Configuration Governance:** All admin configuration changes are audited with before/after snapshots, reviewer identification, and timestamp tracking.

**Integration Management:** Centralized control over external integration connections, sync schedules, and data flow policies.

---

## Localization

The platform supports multi-language operation through a dedicated localization system:

**Language Management:** Admin interface for configuring available languages, setting default languages, and managing translation status.

**Translation Workflow:** Translations are managed through the admin localization page, with support for bulk updates and status tracking.

**User Preferences:** Users can set their preferred language in settings, with automatic content delivery in their chosen language.

**Fallback Handling:** When a translation is missing, the system falls back to the default language to ensure uninterrupted service.

---

## Testing

### Backend Tests

The backend test suite uses pytest with async support:

```bash
cd apps/api
source .venv/bin/activate
pytest tests/ -v
```

Key testing features: pytest-asyncio for async test support, structured test organization by domain, and integration with the smoke test script.

### Frontend Tests

**Unit Tests (Vitest):**

```bash
cd apps/web
npm run test
```

**End-to-End Tests (Playwright):**

```bash
cd apps/web
npx playwright test
```

### Smoke Tests

A comprehensive smoke test script validates the backend API:

```bash
./infra/scripts/backend_v1_smoke.sh
```

---

## Infrastructure & Deployment

### Docker Compose (Local Development)

The `docker-compose.yml` provisions the required infrastructure services:

**PostgreSQL 16** with the pgvector extension enabled, exposed on port 55432. Includes a health check that verifies database readiness. Data is persisted in a named Docker volume (`pg_data`).

**Redis 7** exposed on port 6379. Includes a health check using `redis-cli ping`. Data is persisted in a named volume (`redis_data`).

### Docker Images

**API** (`infra/docker/api.Dockerfile`) — Containerized FastAPI backend with all Python dependencies.

**Web** (`infra/docker/web.Dockerfile`) — Containerized Next.js frontend optimized for production.

### Temporal (Optional)

When `TEMPORAL_ENABLED=true`, the system connects to a Temporal server for durable workflow execution. The `FollowUpReminderWorkflow` handles scheduled follow-up reminders with guaranteed delivery and automatic retries.

---

## Scripts Reference

| Script | Purpose |
|---|---|
| `infra/scripts/bootstrap.sh` | One-time setup: creates Python venv, installs backend and frontend dependencies |
| `infra/scripts/dev-up.sh` | Starts Docker Compose services (PostgreSQL, Redis) |
| `infra/scripts/dev-down.sh` | Stops Docker Compose services |
| `infra/scripts/backend_v1_smoke.sh` | Runs smoke tests against the backend API |

---

## Contributing

### Code Organization Conventions

**Backend:** Python code follows Ruff formatting and linting rules. Type hints are enforced via MyPy. All database operations use async/await patterns. New agents should follow the existing pattern of receiving `AgentRuntimeState` and returning an updated state dict.

**Frontend:** TypeScript strict mode is enabled. Components use Radix UI primitives with Tailwind CSS. API calls go through the typed client libraries in `lib/`. New pages follow the Next.js App Router convention.

### Adding a New Agent

1. Create a new agent file in `apps/api/src/mental_wellbeing_api/agents/`
2. Implement the agent function accepting `AgentRuntimeState` and returning a state update dict
3. Register the agent as a node in `orchestration/graph.py`
4. Add appropriate edges (conditional or direct) in the graph definition
5. Update `AgentRuntimeState` in `orchestration/state.py` if new state fields are needed

### Database Migrations

```bash
cd apps/api
source .venv/bin/activate
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

---

## Code Metrics

| Metric | Count |
|---|---|
| Backend Python files | 100+ |
| Backend lines of code | ~15,500 |
| Frontend TypeScript/TSX files | 135 |
| Specialized AI agents | 27 |
| API route modules | 20+ |
| API endpoints | 50+ |
| Database models | 32 |
| Service classes | 35+ |
| UI components | 45+ |
| API client libraries | 17 |
| Database migrations | 10+ |

---

**Built with safety and empathy at the core.**
