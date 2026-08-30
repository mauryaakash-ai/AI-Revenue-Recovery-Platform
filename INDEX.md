# RevPilot — Project Index

**Version**: 0.1.0 (Phase 1: Foundation Complete)  
**Last Updated**: August 30, 2026  
**Status**: ✓ Ready for Phase 2

---

## Getting Started (3 Steps)

1. **Quick Start Guide**: See [`QUICKSTART.md`](QUICKSTART.md) for one-command setup
2. **Project Overview**: See [`README.md`](README.md) for full architecture and features
3. **Phase 1 Details**: See [`PHASE_1_STATUS.md`](PHASE_1_STATUS.md) for what's built and what's stubbed

---

## Key Documents by Role

### **Developers Building Features**
- **Backend Devs**: Start with `backend/app/models.py` (schema), `backend/app/routes/` (endpoints)
- **Frontend Devs**: Start with `frontend/pages/` (Next.js pages), `frontend/styles/` (Tailwind)
- **Data Engineers**: Start with `data/generator.py` (synthetic data pipeline)

### **DevOps / Infrastructure**
- **Docker Setup**: `docker-compose.yml` (all services in one file)
- **Environment**: `.env.example` (copy and customize)
- **Deployment**: See Phase 8 in `README.md` (TBD)

### **Product / Requirements**
- **Spec Overview**: [`README.md`](README.md) — Full feature roadmap and architecture
- **Phase Progress**: [`PHASE_1_STATUS.md`](PHASE_1_STATUS.md) — What's done, what's next
- **Demo Flow**: See "Demo Flow" section in [`README.md`](README.md)

### **QA / Testing**
- **Test Scenarios**: See "Testing & Evaluation" in [`README.md`](README.md)
- **Synthetic Data**: See "Injected Anomalies" in [`PHASE_1_STATUS.md`](PHASE_1_STATUS.md)
- **Verification**: See "How to Test Phase 1" in [`PHASE_1_STATUS.md`](PHASE_1_STATUS.md)

---

## Project Structure

```
g:\project_Razorpay/
│
├── 📖 README.md                    # Full documentation & roadmap
├── 📖 QUICKSTART.md               # Quick setup instructions
├── 📖 PHASE_1_STATUS.md           # Phase 1 completion report
├── 📖 INDEX.md                    # This file
│
├── 🐳 docker-compose.yml          # All services (Postgres, FastAPI, Next.js, Redis)
├── .env.example                   # Environment template
├── .gitignore                     # Git config
│
├── frontend/                       # Next.js + React + TypeScript
│   ├── pages/                     # Route pages
│   │   ├── _app.tsx              # App wrapper
│   │   └── index.tsx             # Home page (health check demo)
│   ├── styles/
│   │   └── globals.css           # Global Tailwind
│   ├── package.json              # Dependencies
│   ├── tsconfig.json             # TypeScript config
│   ├── next.config.js            # Next.js config
│   ├── tailwind.config.js        # Tailwind config
│   ├── postcss.config.js         # CSS processing
│   └── Dockerfile                # Frontend Docker image
│
├── backend/                        # FastAPI + SQLAlchemy + Python
│   ├── app/
│   │   ├── main.py               # FastAPI app entry, routes registration
│   │   ├── config.py             # Settings (from env vars)
│   │   ├── database.py           # SQLAlchemy setup, session mgmt
│   │   ├── models.py             # All ORM models (Merchant, Transaction, etc.)
│   │   ├── routes/
│   │   │   ├── merchants.py      # Merchant CRUD endpoints
│   │   │   ├── transactions.py   # Transaction query endpoints
│   │   │   ├── analytics.py      # Analytics endpoints (revenue, success rate, etc.)
│   │   │   └── agent.py          # Agent query endpoints (stub for Phase 4)
│   │   └── __init__.py
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                # Backend Docker image
│   └── .env                       # Runtime env (generated from .env.example)
│
├── data/
│   └── generator.py              # Synthetic data generator (50K transactions, injected anomalies)
│
├── migrations/                     # Alembic migrations (TBD Phase 8)
│
└── setup.sh / setup.bat           # One-command setup scripts
```

---

## Service Architecture

### Services in docker-compose.yml

| Service | Port | Role | Status |
|---------|------|------|--------|
| **postgres** | 5432 | PostgreSQL database | ✓ Ready |
| **backend** | 8000 | FastAPI (Python) | ✓ Ready |
| **frontend** | 3000 | Next.js (TypeScript/React) | ✓ Ready |
| **redis** | 6379 | Redis cache (optional, for Phase 5+) | ✓ Ready |

All services auto-restart on failure and have health checks.

---

## Database Schema

### Core Tables (All Implemented in Phase 1)

| Table | Rows | Purpose | Key Fields |
|-------|------|---------|-----------|
| **merchants** | 1 | Tenant isolation | id, name, api_key |
| **customers** | 5K | Customer profiles | id, merchant_id, ltv, segment |
| **transactions** | 50K | Payment transactions | id, merchant_id, amount, status, payment_method, failure_reason |
| **refunds** | ~1.5K | Refund records | id, transaction_id, amount, reason, status |
| **settlements** | 90 | Daily settlements | id, merchant_id, amount, settlement_date |
| **checkout_events** | ~50K | Checkout funnel | id, customer_id, session_id, event (initiated/completed/abandoned) |
| **recovery_predictions** | ~5K | ML predictions | id, transaction_id, probability, expected_recovery |
| **agent_actions** | 0 (Phase 4) | Tool call audit | id, merchant_id, tool, input, result, status, approval |
| **audit_logs** | 0 (Phase 4) | Action audit trail | id, action, timestamp, result, approval_status |

All tables are indexed on common query filters: merchant_id, status, created_at, payment_method.

---

## API Endpoints (Phase 1)

### Implemented (Working)

```bash
# Health
GET  /health
GET  /api/v1/health

# Merchants
POST /api/v1/merchants
GET  /api/v1/merchants/{merchant_id}

# Transactions
GET  /api/v1/merchants/{merchant_id}/transactions
GET  /api/v1/merchants/{merchant_id}/transactions/{transaction_id}

# Analytics (return mock data in Phase 1)
GET  /api/v1/merchants/{merchant_id}/analytics/revenue
GET  /api/v1/merchants/{merchant_id}/analytics/success-rate
GET  /api/v1/merchants/{merchant_id}/analytics/failed-payments
```

### Stubbed (Phase 4)

```bash
POST /api/v1/merchants/{merchant_id}/agent/query
POST /api/v1/merchants/{merchant_id}/agent/approve-action
```

---

## Synthetic Data Overview

Generated by `data/generator.py`:

- **Baseline**: ~9L (₹900K) revenue/day
- **Duration**: 90 days of history
- **Transactions**: 50,000 across all customers
- **Customers**: 5,000 with realistic LTV distribution

### Injected Anomalies (Ground Truth)

| Anomaly | Days | Details | Purpose |
|---------|------|---------|---------|
| **Card failures** | 30-35 | 92% → 74% success, ~143 txns | Test failure detection |
| **UPI drop** | 45-50 | 95% → 82% success | Test payment-method-specific anomalies |
| **High-value failures** | Scattered | 10% of txns, exponential dist | Test high-impact detection |
| **Refund spike** | 60-65 | 5% → 15% refund rate | Test refund pattern detection |
| **Abandonment** | Throughout | 30% of checkouts abandoned | Test checkout funnel analysis |
| **Churn** | Throughout | Realistic LTV distribution | Test customer segmentation |
| **Weekend boost** | All weekends | +30% volume | Test seasonality |
| **Volume spike** | Day 70 | 1.8x normal | Test unusual spike detection |
| **Normal baseline** | Most days | No anomalies | Test false-positive rate |

---

## Development Phases

### Phase 1: Foundation ✓ COMPLETE
- Project init, Docker, schema, synthetic data
- **Status**: All requirements met, ready to move forward

### Phase 2: Analytics (NEXT)
- Revenue, anomaly detection, recovery scoring
- **Expected**: Core calculations + endpoints
- **Duration**: ~1-2 days

### Phase 3: ML
- Isolation Forest, Logistic Regression, feature engineering
- **Expected**: Trained models + evaluation
- **Duration**: ~1-2 days

### Phase 4: Agent
- LLM integration, tool calling, investigation loop
- **Expected**: Full investigation flow working
- **Duration**: ~2-3 days

### Phase 5: Actions
- Action proposals, approval flow, execution
- **Expected**: Mock + Razorpay test mode
- **Duration**: ~1-2 days

### Phase 6: UI
- Dashboard, chat, timeline, audit log
- **Expected**: All views functional
- **Duration**: ~2-3 days

### Phase 7: Testing & Demo
- Unit/integration tests, demo reliability
- **Expected**: All scenarios passing + reproducible demo
- **Duration**: ~1-2 days

### Phase 8: Deployment
- Migrations, production configs, security
- **Expected**: Ready for deployment
- **Duration**: ~1 day

---

## How to Contribute

### Adding a New Endpoint

1. Create route handler in `backend/app/routes/`
2. Add SQLAlchemy query in `backend/app/models.py` (if needed)
3. Register route in `backend/app/main.py`
4. Test via FastAPI Swagger UI: http://localhost:8000/docs

### Adding a Page/Component

1. Create `.tsx` file in `frontend/pages/` (for routes) or `frontend/components/`
2. Import Recharts (for charts) or custom components as needed
3. Call backend API with axios
4. Test in dev: http://localhost:3000

### Adding a Model

1. Define class in `backend/app/models.py` extending `Base`
2. Create indexes on common query filters
3. Update `data/generator.py` to populate it (if synthetic)
4. Add relationships to existing models

---

## Debugging

### Backend Errors
```bash
docker compose logs -f backend
```

### Database Issues
```bash
docker compose exec postgres psql -U revpilot_user -d revpilot -c "SELECT COUNT(*) FROM transactions"
```

### Frontend Build Issues
```bash
docker compose logs -f frontend
# or rebuild
docker compose up --build frontend
```

### Verify Data Generated
```bash
docker compose exec backend python -c "from app.database import SessionLocal; from app.models import Transaction; db = SessionLocal(); print(f'Transactions: {db.query(Transaction).count()}')"
```

---

## Key Design Decisions

1. **SQLAlchemy ORM**: Type-safe, works with any SQL DB, easy migrations
2. **FastAPI**: Modern async Python, auto-generated API docs, built-in validation
3. **Next.js**: Server-side rendering, TypeScript support, Vercel deployment-ready
4. **Synthetic Data**: Seeded for reproducibility, injected anomalies for testing
5. **Audit Logging**: Every tool call logged → compliance + debugging
6. **Approval Gate**: Sensitive actions require explicit human approval (server-side enforced)
7. **SSE Streaming**: Real-time investigation updates without WebSocket complexity

---

## FAQ

**Q: How do I reset the database?**  
A: `docker compose down -v && docker compose up` then run `python data/generator.py`

**Q: Where do I add the Anthropic API key?**  
A: Add `ANTHROPIC_API_KEY=...` to `.env`

**Q: How do I test an API endpoint?**  
A: Use Swagger UI at `http://localhost:8000/docs` or curl

**Q: Can I run this without Docker?**  
A: Yes, but you'll need to install PostgreSQL, Python 3.11+, and Node 18+ manually. Docker is easier.

**Q: What payment providers will be supported?**  
A: Phase 1 uses mock data. Phase 5 adds Razorpay test-mode integration.

---

## Next Immediate Steps

1. **Verify Phase 1**: Run `setup.bat` (or `bash setup.sh`) and confirm all services start
2. **Generate Data**: Run `python data/generator.py` and verify 50K transactions created
3. **Start Phase 2**: Build analytics functions (revenue, anomalies, recovery scoring)
4. **Plan Phase 3**: Define ML features and training pipeline

---

## Contact / Questions

See `README.md` for architecture overview, `QUICKSTART.md` for setup help, `PHASE_1_STATUS.md` for implementation details.

---

**RevPilot** | AI Revenue Intelligence & Action Agent | Powered by Claude + FastAPI + Next.js
