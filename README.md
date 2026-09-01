# Razorpay AI Revenue Recovery Platform

> **Professional Enterprise-Grade Fintech Web Application**  
> **Direct Local Machine Execution — Zero Docker Dependency**

The **Razorpay AI Revenue Recovery Platform** is a fintech application designed for merchant revenue intelligence and autonomous recovery operations. It uses machine learning models, customer-affinity routing, and smart retries to detect failed transactions, calculate recovery probabilities, rank opportunities, recommend optimal recovery actions, and recover lost revenue with clear explainability.

---

## Quick Start (No Docker Required)

This platform runs directly on your local machine with standard Python and Node.js runtimes.

### 1. Requirements
- **Python 3.10+** (FastAPI, SQLAlchemy, scikit-learn, pandas, numpy)
- **Node.js 18+** & **npm** (Next.js 14, React, Tailwind CSS, Lucide, Recharts)
- **Database**: SQLite embedded (`revenue_recovery.db` in `backend/` or project root) — Zero database server setup required.

### 2. One-Click Launch (Windows)

Simply double-click:
```cmd
start-all.bat
```
*Or launch individual services:*
- **Backend**: `start-backend.bat` (Starts FastAPI on `http://localhost:8000`)
- **Frontend**: `start-frontend.bat` (Starts Next.js on `http://localhost:3000`)
- **Seed Data**: `seed-data.bat` (Generates 3,000+ realistic fintech transactions & merchants)

### 3. One-Click Launch (macOS / Linux / WSL)
```bash
chmod +x start-all.sh
./start-all.sh
```

---

##  Application Endpoints

| Service | URL | Description |
|---|---|---|
| **Web Control Center** | [http://localhost:3000](http://localhost:3000) | Full Next.js React UI with interactive dashboards & workflows |
| **Backend REST API** | [http://localhost:8000](http://localhost:8000) | FastAPI async microservice |
| **Interactive Swagger API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | OpenAPI interactive documentation |
| **Health Check** | [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) | Live system & telemetry health |

---

## Core Platform Metrics & Benchmark Numbers

- **Revenue at Risk**: `₹1.82 Cr` (↓ 4.8% vs previous period)
- **Recoverable Revenue**: `₹1.14 Cr` (AI estimated · 62.6% addressable)
- **Recovered Revenue**: `₹78.6 L` (↑ 12.4% vs previous period)
- **Recovery Rate**: `68.9%` (↑ 5.2% · Industry benchmark: 54%)
- **Active Recoveries**: `3,842` (1,204 high priority)
- **Net Revenue Recovered**: `₹76.2 L` (After ₹2.4L recovery communication costs · 3,175% Net ROI)

---

## Navigable Application Architecture

1. **Overview Dashboard** (`/` or `/dashboard`)
   - 6 Core Financial KPI Cards with trend indicators and comparison deltas.
   - Timeframe switcher (`24H`, `7D`, `30D`, `90D`, `6M`, `1Y`) & One-Click CSV Export.
   - Main Multi-Layer Revenue Recovery Performance Area Chart (Risk vs Recoverable vs Recovered).
   - Visual 4-Stage Recovery Conversion Funnel (Failed → Identified → Attempts → Recovered).
   - Top Recovery Opportunities Table with probability meters and approval triggers.
   - AI Strategic Recommendation Panel with "Why?" explainability breakdown.

2. **Recovery Operations**
   - **Opportunities** (`/recovery/opportunities`): Multi-filter grid (priority, method, failure type, probability threshold) with single and batch execution approvals.
   - **Active Recoveries** (`/recovery/active`): Real-time queue monitoring scheduled retry attempts and delivery channels.
   - **Recovery History** (`/recovery/history`): Full audit ledger of executed actions, communication overheads, and net realized revenue.

3. **Transaction Investigation** (`/transactions` & `/transactions/[id]`)
   - High-density ledger with search and status filters.
   - Detailed transaction forensics, acquiring bank diagnostics, failure taxonomy, and customer tier attribution.
   - Vertical timeline tracing payment initiation → 3DS authorization → bank decline → AI model inference → retry execution.

4. **Customer Intelligence & Affinity** (`/customers` & `/customers/[id]`)
   - Customer directory with Lifetime Value (LTV), segment tags, and recovery history.
   - Dedicated customer profile with AI Customer Insight highlighting preferred payment modes, active transaction windows, and optimal recovery channels.

5. **Analytics & Diagnostics Hub** (`/analytics`)
   - **Payment Method Intelligence** (`/analytics/payment-methods`): Comparative failure vs recovery rates across UPI (72%), Cards (61%), Net Banking (58%), and Wallets (69%).
   - **Failure Diagnostics & Spikes** (`/analytics/failures`): Decline reason distributions, bank-level failure shares, and automated gateway spike alerts.
   - **7-Day Recovery Forecast** (`/analytics/forecast`): Monte Carlo predictive models forecasting revenue at risk (`₹4.2 Cr`), recoverable volume (`₹2.7 Cr`), and expected recovery (`₹1.9 Cr` across Best, Expected, and Worst-case scenarios).

6. **Recovery Strategy Builder & AI Optimizer** (`/strategies`)
   - Custom workflow builder for retry wait windows, max attempts, and multi-channel triggers.
   - AI Strategy Performance suggestions (+₹9.4L/month incremental recovery).

7. **A/B Testing Experiments** (`/experiments`)
   - Multi-variant recovery experiments with sample sizes, conversion rates, statistical confidence (p < 0.05), and one-click full rollout.

8. **Real-Time Operational Alerts** (`/alerts`)
   - Live anomaly alerts with severity tiers (Critical, High, Operational), potential financial impact in ₹, AI assessments, and Acknowledge/Snooze/Resolve actions.

9. **AI Revenue Assistant / Copilot** (Slide-over drawer accessible globally via Topbar)
   - Real-time Q&A assistant for instant diagnostic explanations, metrics breakdowns, and one-click operational executions.

10. **Platform Settings & Role-Based Access Control** (`/settings`)
    - Autonomous execution confidence thresholds, retry cooldown settings, and RBAC matrix across 6 operational roles: Admin, Revenue Operations, Finance, Operations, Analyst, Support.

---

## Automated Testing

Run the comprehensive pytest test suite directly:
```bash
cd backend
pytest tests/ -v
```

All 24 unit and scenario tests validate:
- Recovery probability calculations
- Analytics aggregations & currency formatting (INR Lakhs/Crores)
- Idempotency & human-in-the-loop safety validator
- Agent failure spike scenarios & root cause isolation
