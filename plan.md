# Quantum Wealth & BO Platform — Updated plan.md

## 1) Objectives
- **Completed:** Proved the core workflow end-to-end: **ISIN → MOEX resolve → store → RSS news → Claude analysis (with liquidity-fund rule) → structured output**.
- **Completed:** Delivered a V1 **Bloomberg/TradingView-style dark terminal UI** with working modules: **Auth**, **Portfolio**, **News**, **AI Insights**, **TradingView Signals**, **BO Trade Log**, **Adaptive Memory + Safeguards**, **Dashboard**.
- **Now (current focus):** Move from MVP to **production-grade V1.5**:
  - Make Adaptive Memory more **RAG-like and enforceable** (always retrieved and applied).
  - Add deeper analytics (loss clustering, session/expiry breakdowns, portfolio allocation/performance charts).
  - Improve operational robustness (background jobs, caching, throttling).
  - Continue tightening security and data isolation (auth already implemented; expand).

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation: do not proceed until stable)
**Status: COMPLETED (All 4 POCs passed)**

**POC-1: MOEX ISS ISIN→Asset Resolver (websearch + script)**
- Validated `https://iss.moex.com/iss/securities.json?q=<ISIN>` resolution.
- Implemented caching + error handling.
- **Outcome:** Reliable ISIN→(SECID, shortname, fullname, type/group, board) resolution.

**POC-2: Claude via Emergent Key (script)**
- Confirmed Anthropic Claude works via `emergentintegrations`.
- Enforced the **liquidity fund rule**: ignore technical indicators, treat as cash yield.
- **Outcome:** Structured JSON responses.

**POC-3: RSS Aggregation (script)**
- Implemented RSS aggregation from **free/public sources** (Yahoo Finance, Investing.com, RBC, MOEX news).
- Dedupe + normalization.

**POC-4: Core Orchestration Dry Run (script)**
- Chain validated: MOEX resolution + RSS + Claude + memory context.
- **Outcome:** One-command orchestration succeeded.


### Phase 2 — V1 App Development (MVP terminal)
**Status: COMPLETED (Backend + Frontend built and verified)**

**Backend (FastAPI + MongoDB)**
- Implemented modular API endpoints:
  - `POST /api/auth/login` (rate-limited)
  - `GET /api/auth/me`
  - `POST /api/portfolio/resolve-isin`
  - `POST /api/portfolio/holdings` (auto-resolve ISIN via MOEX before save)
  - `GET /api/portfolio/holdings`, `DELETE /api/portfolio/holdings/{id}`
  - `POST /api/news/refresh`, `GET /api/news` (**fixed** serialization error)
  - `POST /api/ai/portfolio-insight` (uses portfolio + news + memory + safeguards)
  - `POST /api/signals/webhook`, `GET /api/signals`
  - `POST /api/trades`, `GET /api/trades`, `PUT /api/trades/{id}`, `GET /api/trades/stats`
  - `GET /api/memory`, `POST /api/memory`
  - `GET /api/safeguards`, `POST /api/safeguards/manual`, `PUT /api/safeguards/{id}/toggle`, `DELETE /api/safeguards/{id}`
  - `POST /api/safeguards/generate` (AI rules from loss trades)
  - `GET /api/dashboard/stats`
- Implemented MOEX ISIN normalization utility + in-memory cache.
- Implemented RSS caching to Mongo.
- Implemented AI analysis logging into memory.

**Frontend (React + Tailwind + shadcn/ui)**
- Terminal app shell: left icon sidebar + top bar + bottom status bar.
- Pages working:
  - Dashboard
  - Portfolio (Add Holding dialog with ISIN live resolution preview)
  - News (filters + refresh)
  - AI Insights (Analyze Portfolio + structured display)
  - Signals (webhook list + test signal + one-click trade logging)
  - Trades (journal + mark win/loss)
  - Memory & Safeguards (tabs + AI generate + manual rule)

**End of Phase 2: E2E test**
- **Completed:** add holding → resolved names → refresh news → AI insight → webhook signal → log trade → mark loss → generate safeguards.

**Testing outcome**
- Initial testing agent report: Backend **18/19** passed (94.7%); Frontend **20/20** passed (100%).
- **Fixed:** `/api/news/refresh` 500 serialization error.
- **Current state:** Major features functioning end-to-end.


### Phase 3 — Feature Expansion (production-friendly improvements)
**Status: IN PROGRESS (next milestone: V1.5)**

**3.1 Adaptive Memory Engine — strengthen RAG + enforcement**
- Implement explicit retrieval pipeline for AI calls:
  - Fetch last N memories
  - Fetch active safeguards
  - Fetch most relevant loss clusters (if available)
- Add “must-cite safeguards” behavior:
  - AI response includes which safeguards were applied and why.
- Improve memory storage schema:
  - Normalize tags, outcome, affected assets, timeframe, session.

**3.2 Analytics additions (terminal-grade)**
- Trades:
  - Win rate by **asset**, **expiry**, **session/time-of-day**, **direction**.
  - Loss clustering: detect high-loss windows around news times.
- Portfolio:
  - Allocation by asset class (stock/bond/liquidity fund).
  - Optional performance chart scaffolding (later extend to price pulls).

**3.3 Operational hardening**
- Background refresh:
  - Scheduled RSS refresh (e.g., APScheduler or lightweight background task) with manual refresh retained.
- Better MOEX caching:
  - Persist ISIN→SECID/name mapping cache in Mongo (with TTL) instead of only in-memory.
  - Retry/backoff and throttle for MOEX ISS requests.
- Error handling:
  - Standardized error envelope across endpoints.
  - Logging improvements for external calls (MOEX/RSS/Claude).

**3.4 UI polish + charts**
- Add Recharts panels:
  - Portfolio allocation pie.
  - Win/Loss bar chart.
  - Session-based performance heatmap (optional).
- UX improvements:
  - Global search (tickers/ISIN/news keywords).
  - Better empty states and loading skeletons.
  - Keep dense Bloomberg-style tables.

**End of Phase 3: 1 round E2E test**
- Validate:
  - Memory retrieval is always used before AI recommendations.
  - Safeguards generated from losses show up and are referenced by AI.
  - Analytics computations match stored trades.
  - Background refresh does not break manual refresh.


### Phase 4 — Security & Auth (hardening + multi-user readiness)
**Status: PARTIALLY COMPLETED (Auth foundation already implemented in Phase 2)**

**Already implemented**
- Username/password login with **bcrypt hashing**.
- JWT bearer auth.
- Strict rate limiting on login (`5/minute`).
- Seeded admin on startup:
  - Username: `Vika-net1`
  - Password: `Dd19840622` (stored hashed)

**Remaining upgrades**
- Enforce auth on sensitive endpoints (currently mixed; ensure consistent protection policy).
- Per-user data partitioning:
  - Add `user` field to all collections and scope queries by user.
- Token lifecycle:
  - Optional refresh tokens or shorter-lived access tokens.
- Security headers and CORS tightening:
  - Reduce `CORS_ORIGINS="*"` for deployment.
- Audit logging:
  - Login attempts, safeguard toggles, AI actions.

**End of Phase 4: 1 round E2E test**
- Validate:
  - Rate limiting on login.
  - JWT expiry behavior.
  - Data isolation for multiple users.
  - No unauthenticated access to protected resources.


## 3) Next Actions (immediate)
1. **Phase 3.1:** Implement robust Adaptive Memory retrieval + enforce “safeguards must be referenced” in AI output.
2. **Phase 3.2:** Add analytics endpoints + UI panels (win/loss by asset/expiry/session).
3. **Phase 3.3:** Add background RSS refresh + Mongo TTL cache for MOEX ISIN resolutions.
4. **Phase 3.4:** Add Recharts-based visual panels (allocation + win/loss).
5. **Phase 4:** Finish auth enforcement + per-user partitioning + tighten CORS for deployment.

## 4) Success Criteria
- **ISIN normalization:** Entering an ISIN always resolves to a human-readable MOEX asset name (or returns a clear actionable error).
- **AI analysis:** Insights incorporate latest RSS news + portfolio + memory + safeguards; liquidity funds treated as cash yield (no TA).
- **TradingView → Signals → Trades:** Webhook ingestion works; user can log BO trades and outcomes with one-click flow.
- **Adaptive Memory:** Losses generate safeguard rules; future AI recommendations retrieve and reference them.
- **Security:** JWT auth + strict login rate limiting are live; Phase 4 hardening completes per-user isolation and endpoint protection.
