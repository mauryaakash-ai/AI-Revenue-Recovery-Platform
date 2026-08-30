# RevPilot — AI Revenue Intelligence & Action Agent

**Version**: 1.0.0 | **Status**: Production Ready | **Phases**: All Complete (1-8)

RevPilot is an AI-powered revenue intelligence platform for online merchants. It investigates payment/transaction data, detects anomalies, identifies root causes, calculates financial impact, ranks recovery opportunities, proposes actions, obtains human approval, executes safely, and measures outcomes—all automatically.

## Features

### Core Capabilities
- **Real-time Anomaly Detection**: Identifies revenue drops, payment method failures, and unusual patterns via statistical deviation + Isolation Forest
- **Root Cause Analysis**: Attributes anomalies to specific payment methods, customer segments, or checkout issues
- **Financial Impact Quantification**: Calculates confirmed losses and at-risk revenue with confidence bounds
- **Recovery Ranking**: Prioritizes recovery candidates by expected value, probability, and urgency
- **Human-in-Loop Approval**: Blocks sensitive actions (refunds, payouts) pending merchant approval
- **Audit Trail**: Logs every tool call, approval, and outcome for compliance + debugging
- **Multi-Merchant Isolation**: Per-merchant data segregation with API-level access control

### Tech Stack
| Layer | Tech |
|-------|------|
| **Frontend** | Next.js 14 + React + TypeScript + Tailwind CSS + Recharts |
| **Backend** | FastAPI + SQLAlchemy + Pydantic + Async |
| **Database** | PostgreSQL 15 + Strategic Indexes |
| **ML** | scikit-learn (Isolation Forest, Logistic Regression) |
| **Payments** | Mock Provider (test) + Razorpay Test API integration |
| **Real-time** | Server-Sent Events (SSE) for streaming investigations |
| **Container** | Docker + Docker Compose (all-in-one) |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (if running locally)
- Node.js 18+ (if running locally)

### 1. Clone & Setup
```bash
cd g:\project_Razorpay
cp .env.example .env
docker compose up
```

Wait ~30 seconds for all services to be healthy.

### 2. Generate Synthetic Data
In a separate terminal:
```bash
python data/generator.py
```

### 3. Access the App
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health

---

## Project Structure

```
g:\project_Razorpay/
├── frontend/                    # Next.js + React UI
│   ├── pages/
│   │   ├── index.tsx           # Home (navigation hub)
│   │   ├── dashboard.tsx       # KPIs, leaks, recommendations
│   │   ├── chat.tsx            # Agent Q&A with live timeline
│   │   └── audit-log.tsx       # Action audit trail
│   └── styles/globals.css
│
├── backend/                    # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── models.py          # SQLAlchemy ORM (9 tables)
│   │   ├── analytics.py       # Revenue, anomalies, recovery scoring
│   │   ├── ml.py              # Isolation Forest, recovery model
│   │   ├── agent.py           # Agent orchestration
│   │   ├── tools.py           # Tool registry + execution
│   │   ├── providers.py       # Mock & Razorpay providers
│   │   └── routes/
│   │       ├── merchants.py
│   │       ├── transactions.py
│   │       ├── analytics.py
│   │       └── agent.py
│   ├── tests/
│   │   ├── test_analytics.py
│   │   └── test_agent_scenarios.py
│   └── requirements.txt
│
├── data/
│   └── generator.py            # Synthetic data generator
│
├── docker-compose.yml          # Full stack
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## Test Scenarios (All Passing)

1. ✅ **Card failure spike** (92% → 74%, ₹1.8L impact)
2. ✅ **UPI success drop** (95% → 82%)
3. ✅ **High-value failures** (recovery ranking)
4. ✅ **Checkout abandonment** (value estimation)
5. ✅ **Refund spike** (pattern detection)
6. ✅ **Normal day** (no false positives)

---

## Deployment

### Docker Compose (Current)
```bash
docker compose up
```

### Run Tests
```bash
cd backend
pytest tests/ -v
```

---

## Documentation

- **QUICKSTART.md** → Setup commands
- **PHASE_1_STATUS.md** → Foundation details
- **INDEX.md** → Project navigation
- **API Docs** → http://localhost:8000/docs

---

**RevPilot**: Complete AI revenue intelligence system. All 8 phases delivered. Production ready.
