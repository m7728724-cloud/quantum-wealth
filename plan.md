# Quantum Wealth & BO Platform — plan.md

## 1) Objectives
- Prove the **core workflow** works end-to-end: **(ISIN → MOEX resolve → store → AI reads portfolio + news → outputs analysis)**.
- Deliver a V1 terminal UI (dark, Bloomberg/TradingView feel) with: **Portfolio**, **News**, **AI Insights**, **TradingView Signals**, **BO Trade Log**, **Adaptive Memory**.
- Ensure security foundations: **bcrypt + JWT**, strict rate limiting, and seeded admin account (added after core is proven).

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation: do not proceed until stable)
**Goal:** Validate all external dependencies and the “if-broken-app-is-useless” path.

**POC-1: MOEX ISS ISIN→Asset Resolver (websearch + script)**
- Websearch MOEX ISS best endpoints for **securities lookup by ISIN** + board/market nuances.
- Write a minimal Python script that:
  - Accepts ISIN (e.g., `RU000A10AHE5`).
  - Queries MOEX ISS, returns `{isin, secid, shortname, fullname, type/market, currency}`.
  - Handles: not found, ambiguous results, MOEX downtime, retries/backoff.
- Success = consistent name resolution for sample equities/bonds/funds + clear error states.

**POC-2: Claude via Emergent Key (script)**
- Minimal Python script calling Claude with:
  - A tiny portfolio JSON + one RSS article text.
  - Required constraint: **Liquidity fund rule** (ignore RSI/TA, treat as cash yield).
- Success = deterministic-ish structured output (JSON schema) + safe failure handling.

**POC-3: RSS Aggregation (script)**
- Pick initial feeds (no keys): RBC.ru, MOEX news, Yahoo Finance, Investing.com (RSS if available).
- Script fetches, normalizes to `{source,title,link,published,summary,text_if_possible}` and caches.
- Success = stable parsing + dedupe + timestamp ordering.

**POC-4: Core Orchestration Dry Run (script)**
- Chain: `ISIN input → MOEX resolve → store doc (local JSON or Mongo) → fetch RSS → Claude analysis → output summary + risks + watchlist`.
- Success = one-command run that produces a final analysis artifact.

### Phase 2 — V1 App Development (MVP terminal; delay auth until Phase 4)
**Backend (FastAPI + MongoDB)**
- Project skeleton: modular routers: `/portfolio`, `/ai`, `/news`, `/signals`, `/trades`, `/memory`, `/health`.
- Implement core endpoints:
  - `POST /portfolio/holdings` (accept ISIN + qty + optional buy price) → **resolve via MOEX before save**.
  - `GET /portfolio/holdings` (resolved names always returned).
  - `POST /news/refresh` (pull RSS → cache) and `GET /news`.
  - `POST /ai/portfolio-insight` (reads portfolio + latest news + memory → returns structured insight).
  - `POST /signals/webhook` (TradingView webhook ingest → store Signals).
  - `POST /trades` + `GET /trades` (BO logging).
  - `POST /memory/log` + `GET /memory` (store AI interactions/outcomes).
  - `POST /safeguards/generate` (analyze losses → write SafeguardRules).
- Data rules:
  - Holdings require `isin`, `resolved_name`, `asset_class`, `secid`, timestamps.
  - Liquidity funds flagged (e.g., by MOEX type/board or manual toggle) → AI prompt enforces rule.

**Frontend (React + Tailwind + shadcn/ui)**
- Terminal layout: left nav + main multi-panel dashboard.
- Pages/Panels:
  - Portfolio table (add holding modal: ISIN, qty, price) with inline resolution preview.
  - News panel (filters: RU/global, source, keyword) + refresh.
  - AI Insights panel (one-click “Analyze Portfolio”) showing: macro view, risks, actions, confidence.
  - TradingView Signals panel (live list from webhook storage; manual “log trade” from signal).
  - BO Trades journal (result tagging Win/Loss + notes).
  - Adaptive Memory + Safeguard Rules viewer.

**End of Phase 2: 1 round E2E test**
- Run: add holding by ISIN → see resolved name → refresh news → AI insight generated → post a webhook signal → log trade → mark loss → generate safeguards.

### Phase 3 — Feature Expansion (production-friendly modularization)
- Improve Adaptive Memory Engine (RAG-style):
  - Retrieval: last N relevant memories + safeguards + similar-loss patterns.
  - Enforce: AI must **always** retrieve memory before recommendations.
- Add analytics:
  - Loss clustering (asset/time/news-window) and rule suggestions.
  - BO stats (win rate by asset/expiry/session).
- Operational hardening:
  - Background job option for RSS refresh (manual trigger remains).
  - Better MOEX caching (per ISIN/secid) and throttling.

**End of Phase 3: 1 round E2E test**
- Validate memory retrieval impacts output; validate safeguard generation prevents repeated bad setups.

### Phase 4 — Security & Auth (JWT + rate limiting + seeded admin)
- Implement username/password auth:
  - bcrypt hashing, JWT access tokens, secure cookie or Authorization header.
  - Strict rate limiting on login + sensitive endpoints.
- Seed admin account on startup:
  - Username: `Vika-net1` / Password: `Dd19840622` (store only hashed).
- Add per-user data partitioning for all collections.

**End of Phase 4: 1 round E2E test**
- Login throttling, token expiry/refresh behavior, data isolation.

## 3) Next Actions (immediate)
1. Do MOEX ISS endpoint websearch and implement **POC-1** script.
2. Implement **POC-2** Claude script with required liquidity-fund constraint + JSON output contract.
3. Implement **POC-3** RSS script + caching/dedupe.
4. Implement **POC-4** orchestration script; iterate until it’s reliable.
5. After POC success, build Phase 2 V1 app in one connected pass (backend+frontend) and run the E2E test.

## 4) Success Criteria
- **ISIN normalization**: entering an ISIN always results in a resolved, human-readable asset name (or a clear actionable error).
- **AI analysis**: insights incorporate latest RSS news + portfolio + memory; liquidity funds treated as cash yield (no TA).
- **TradingView → Signals → Trades**: webhook ingestion works; user can log BO trades and outcomes.
- **Adaptive Memory**: losses generate safeguard rules; future AI recommendations reference them.
- **Security (post-Phase 4)**: bcrypt+JWT, strict login rate limiting, seeded admin works, per-user data isolation.
