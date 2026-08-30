# RevPilot Quick Start

## One-Command Start (Recommended)

### Windows
```bash
setup.bat
```

### macOS / Linux
```bash
bash setup.sh
```

This will:
1. Copy `.env` from template
2. Start Docker Compose
3. Wait for PostgreSQL
4. Create database tables
5. Generate synthetic data (50K transactions, injected anomalies)

**Total time**: ~60 seconds on first run, ~30 seconds on subsequent runs.

---

## Manual Step-by-Step

### 1. Start Services
```bash
docker compose up -d
```

Wait ~15 seconds for all services to be healthy.

### 2. Check Backend Health
```bash
curl http://localhost:8000/api/v1/health
```

Expected: `{"status": "healthy", ...}`

### 3. Generate Synthetic Data
```bash
python data/generator.py
```

Expected: ~50,000 transactions inserted, ~5,000 customers, with injected anomalies.

### 4. Access the App

- **Frontend**: http://localhost:3000 (should show "✓ Backend: healthy")
- **API Docs**: http://localhost:8000/docs (FastAPI Swagger UI)
- **Logs**: `docker compose logs -f`

---

## Common Commands

### Restart Services
```bash
docker compose restart
```

### Stop Everything
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f backend    # Backend only
docker compose logs -f frontend   # Frontend only
docker compose logs -f postgres   # Database only
```

### Connect to Database Directly
```bash
psql postgresql://revpilot_user:revpilot_password@localhost:5432/revpilot
```

### Regenerate Data
```bash
# Drop and recreate database
docker compose down -v
docker compose up -d
# Wait 10 seconds
python data/generator.py
```

### Build Frontend Only (after changes)
```bash
docker compose up --build frontend
```

### Build Backend Only (after changes)
```bash
docker compose up --build backend
```

---

## Testing Phase 1

After setup, run these sanity checks:

```bash
# 1. Health check
curl http://localhost:8000/api/v1/health

# 2. Create a merchant and get its ID
MERCHANT_ID=$(curl -s -X POST "http://localhost:8000/api/v1/merchants?name=Test%20Merchant" | jq -r '.id')

# 3. Query transactions
curl http://localhost:8000/api/v1/merchants/$MERCHANT_ID/transactions

# 4. Get revenue analytics
curl http://localhost:8000/api/v1/merchants/$MERCHANT_ID/analytics/revenue

# 5. Get success rate
curl http://localhost:8000/api/v1/merchants/$MERCHANT_ID/analytics/success-rate

# 6. View frontend
open http://localhost:3000
```

---

## Project Layout

```
.
├── frontend/               # Next.js app
│   ├── pages/             # Page components
│   ├── styles/            # Global CSS + Tailwind
│   └── package.json
├── backend/               # FastAPI app
│   ├── app/
│   │   ├── routes/        # API endpoints
│   │   ├── models.py      # SQLAlchemy ORM models
│   │   ├── database.py    # DB connection & session
│   │   ├── config.py      # Settings from env
│   │   └── main.py        # FastAPI app entry
│   └── requirements.txt
├── data/
│   └── generator.py       # Synthetic data generator
├── docker-compose.yml     # All services
├── .env.example           # Environment template
└── README.md              # Full documentation
```

---

## Environment Variables

Key variables in `.env`:

```
DATABASE_URL=postgresql://revpilot_user:revpilot_password@postgres:5432/revpilot
ENVIRONMENT=development
ANTHROPIC_API_KEY=your_api_key_here    # Needed for Phase 4 (Agent)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## What's Next?

1. **Phase 2 (Analytics)**: Build revenue, anomaly, and recovery-scoring functions
2. **Phase 3 (ML)**: Train Isolation Forest and recovery probability models
3. **Phase 4 (Agent)**: Integrate Claude LLM, tool calling, investigation loop
4. **Phase 5 (Actions)**: Implement approval flow and payment operations
5. **Phase 6 (UI)**: Build dashboard, chat, timeline, audit log
6. **Phase 7 (Testing)**: Validate agent against 5 test scenarios + demo reliability
7. **Phase 8 (Deploy)**: Finalize Docker, docs, security

---

## Troubleshooting

### Backend won't start
```bash
docker compose logs backend
# Check if DATABASE_URL is correct
# Check if Postgres is healthy: docker compose logs postgres
```

### Frontend shows "Failed to connect to backend"
```bash
# Ensure backend is running and healthy
curl http://localhost:8000/api/v1/health

# Check NEXT_PUBLIC_API_URL in .env
cat .env | grep NEXT_PUBLIC_API_URL

# Restart frontend
docker compose restart frontend
```

### Data generation fails
```bash
# Ensure backend is running
docker compose logs backend

# Ensure .env has DATABASE_URL set correctly
# Run with verbose output:
python data/generator.py 2>&1 | tail -50
```

### Database connection issues
```bash
# Test connection directly
psql postgresql://revpilot_user:revpilot_password@localhost:5432/revpilot -c "SELECT 1"

# Or from Docker
docker compose exec postgres psql -U revpilot_user -d revpilot -c "SELECT 1"
```

---

## Questions?

See **README.md** for:
- Full architecture overview
- API examples
- Data model details
- Security & compliance notes
- Phase roadmap

See **PHASE_1_STATUS.md** for:
- What's implemented vs. stubbed
- Injected anomalies in synthetic data
- Testing approach
- Known limitations
