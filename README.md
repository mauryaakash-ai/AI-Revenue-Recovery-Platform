# RevPilot — AI Revenue Intelligence & Action Agent

RevPilot is an AI-powered revenue intelligence platform for online merchants. It investigates payment/transaction data to detect anomalies, quantify financial impact, recommend recovery actions, obtain human approval, execute safely, and measure outcomes.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (included in Docker)

### Setup

1. **Clone and navigate**
```bash
cd g:\project_Razorpay
```

2. **Copy environment template**
```bash
cp .env.example .env
```

3. **Start the stack**
```bash
docker compose up
```

This brings up:
- **PostgreSQL** on `localhost:5432`
- **FastAPI Backend** on `localhost:8000`
- **Next.js Frontend** on `localhost:3000`
- **Redis** on `localhost:6379` (optional, for caching)

### Generate Synthetic Data

In a separate terminal:
```bash
python data/generator.py
```

This creates:
- 5,000 customers
- 50,000 transactions across 90 days
- Injected anomalies for testing (card failures, UPI drops, refund spikes, etc.)
- A "normal day" baseline for false-positive validation

### Access the App

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## Architecture

### Frontend (Next.js + React + Tailwind)
- **Dashboard**: KPI cards (Revenue Today, Revenue at Risk, Success Rate)
- **Chat Interface**: Natural-language Q&A with the agent
- **Investigation Timeline**: Live SSE stream of agent steps
- **Audit Log**: Timestamped feed of tool calls and approvals
- **Approval Modal**: Gate for sensitive actions

### Backend (FastAPI + SQLAlchemy)
- **Analytics Layer**: Revenue, success rate, failed payments, refunds, anomalies
- **Agent Orchestration**: Intent detection → investigation → root cause → recommendation
- **Action Engine**: Tool registry + approval flow + execution
- **Audit & Logging**: Every tool call, approval, and outcome tracked

### Database (PostgreSQL)
- Merchants, Customers, Transactions, Refunds, Settlements
- CheckoutEvents, RecoveryPredictions, AgentActions, AuditLogs
- Indexed for performance on common queries (merchant_id, status, created_at, payment_method)

## Key Features (by Phase)

### Phase 1: Foundation ✓
- Project structure, Docker setup
- Database schema & migrations
- Synthetic data generator
- Basic API endpoints

### Phase 2: Analytics (next)
- Revenue calculations & anomaly detection
- Success rate & failure analysis
- Revenue-at-risk & recovery scoring
- Customer segmentation

### Phase 3: ML
- Isolation Forest anomaly detection
- Logistic Regression recovery probability model
- Feature engineering for transaction classification
- Priority scoring & ranking

### Phase 4: Agent
- LLM tool-calling integration
- Investigation planner
- Root-cause analysis
- Structured recommendation generation

### Phase 5: Actions
- Action proposal & approval flow
- Mock payment provider
- Razorpay test-mode integration
- Campaign execution

### Phase 6: UI
- Live investigation timeline (SSE)
- Approval cards with financial context
- Audit log viewer
- Dashboard + chat interface

### Phase 7: Testing & Demo
- Unit tests for analytics/ML
- Integration tests for agent workflows
- Demo scenario (reproducible, full flow)
- Evaluation metrics

### Phase 8: Deployment
- Docker Compose finalization
- Environment docs
- Security hardening

## Project Structure

```
g:\project_Razorpay/
├── frontend/               # Next.js app
│   ├── pages/
│   ├── components/
│   ├── styles/
│   └── package.json
├── backend/                # FastAPI app
│   ├── app/
│   │   ├── routes/
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── database.py
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── data/
│   └── generator.py        # Synthetic data
├── migrations/             # Alembic (future)
├── docker-compose.yml
├── .env.example
└── README.md
```

## Development Workflow

### Adding Analytics Functions
1. Create a deterministic function in `backend/app/analytics/`
2. Add SQLAlchemy queries to pull merchant/transaction data
3. Return labeled, confidence-bounded estimates (e.g., "expected_recovery")
4. Unit test with synthetic data
5. Expose via FastAPI route

### Adding Agent Tools
1. Define tool signature (input/output schema) in `backend/app/tools/`
2. Implement deterministic logic (no LLM math)
3. Register in tool registry (JSON schema + callable)
4. Gate sensitive tools behind approval layer
5. Log all calls to `agent_actions` table

### Adding UI Pages
1. Create `.tsx` component in `frontend/pages/`
2. Use Recharts for charts, Tailwind for layout
3. Call backend API endpoints with axios
4. Show real-time SSE updates if applicable

## Data Model Highlights

### Transactions
- **Status**: pending, success, failed, cancelled
- **Indexed on**: merchant_id, status, created_at, payment_method
- **Failure reasons**: specific ("insufficient_funds") for root-cause analysis

### AgentActions
- **tool_tier**: read, analyze, recommend, low_risk_action, sensitive_action
- **Only sensitive_action requires blocking approval**
- **Status**: pending → approved/rejected → executed/failed
- **Every input/output logged** for audit trail

### AuditLogs
- **Captures**: user/agent initiator, action, result, approval
- **Used for**: compliance, debugging, understanding merchant behavior

## Security & Compliance

1. **No Real Money**: Mock provider + Razorpay test mode only
2. **Approval Gate**: Sensitive actions unreachable without explicit approval token
3. **Audit Trail**: Every tool call, approval, and outcome timestamped
4. **Data Isolation**: Each merchant sees only their own data
5. **API Keys**: Server-side environment variables only
6. **Input Validation**: All endpoints validate merchant_id, amounts, etc.

## API Examples

### Get Revenue Analytics
```bash
curl http://localhost:8000/api/v1/merchants/{merchant_id}/analytics/revenue?days=7
```

### Get Failed Payments
```bash
curl http://localhost:8000/api/v1/merchants/{merchant_id}/analytics/failed-payments?days=7
```

### Submit Agent Query (Phase 4)
```bash
curl -X POST http://localhost:8000/api/v1/merchants/{merchant_id}/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Why is revenue down today?"}'
```

## Testing & Evaluation

### Test Scenarios (Ground Truth from Synthetic Data)
1. **Card failure spike**: Detect 92%→74% drop on day 30-35, quantify ₹1.8L impact
2. **UPI success drop**: Detect 95%→82% drop on day 45-50
3. **High-value failures**: Identify & rank recovery candidates
4. **Refund spike**: Day 60-65, quantify volume & affected products
5. **Normal day**: Verify no false alarms on days with no injected anomaly

### Metrics
- Anomaly detection: precision, recall, F1
- Root-cause accuracy: did agent correctly attribute to payment method/time/customer?
- Revenue-at-risk estimation error: absolute vs. calculated
- Recovery probability: model calibration (predicted 60% → actual 58%)
- Action approval rate: % of recommendations approved by human
- Investigation latency: end-to-end time from query to recommendation

## Demo Flow (Phase 7)

```
1. Open http://localhost:3000
2. Dashboard shows: ₹7.1L revenue (vs. ₹9L baseline), 74% card success rate
3. Ask: "Why is revenue down?"
4. Watch live investigation timeline (SSE):
   ✓ Compared today's revenue
   ✓ Detected card payment anomaly
   ✓ Estimated ₹1.8L impact
   ⏳ Finding recovery candidates...
5. Agent proposes: "Send payment link to 61 customers, recover up to ₹86K"
6. Click Approve
7. See campaign results, updated dashboard
```

This demo is seeded and reproducible.

## Troubleshooting

### Backend won't start
```bash
docker compose logs backend
# Check DATABASE_URL and Postgres health
```

### Synthetic data won't generate
```bash
# Ensure backend is running and DB is ready
docker compose logs postgres
# Check if migrations ran
```

### Frontend can't reach backend
```bash
# Verify NEXT_PUBLIC_API_URL in .env
# Check backend health: http://localhost:8000/api/v1/health
```

## Next Steps

1. **Finish Phase 1**: Verify Docker Compose + synthetic data
2. **Build Phase 2**: Analytics functions (revenue, anomalies, recovery scoring)
3. **Build Phase 3**: ML models (Isolation Forest, Logistic Regression)
4. **Build Phase 4**: Agent orchestration & tool calling
5. **Build Phase 5**: Action engine & approval flow

## License

Proprietary. Internal use only.

---

**Built with:** Next.js, FastAPI, PostgreSQL, Claude LLM, Tailwind CSS, Recharts
