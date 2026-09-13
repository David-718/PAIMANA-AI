# SIH26103 – Predictive Project Monitoring Platform

A hackathon-ready prototype for SIH26103: a web-based integrated project-monitoring platform focused on **predictive and prescriptive monitoring**, not merely project reporting.

## Core capabilities
- Project portfolio dashboard
- Project details and progress
- Cost-overrun prediction
- Time-overrun prediction
- Explainable risk score
- Early-warning alerts
- Driver analysis
- Prescriptive recommendations
- Role-based access (Admin / Project Officer / Management)
- REST API
- React frontend
- PostgreSQL-ready backend
- Synthetic demo dataset clearly labelled as synthetic

## Architecture
React → FastAPI → PostgreSQL/SQLite → ML prediction engine

For a fast demo, the backend defaults to SQLite. PostgreSQL can be configured through `DATABASE_URL`.

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open API docs at http://127.0.0.1:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## Demo accounts
These are demo-only credentials:
- Admin: `admin` / `admin123`
- Project Officer: `officer` / `officer123`
- Management: `manager` / `manager123`

## Important
`data/projects.csv` is synthetic demonstration data. It is NOT official PAIMANA data.

This prototype is designed so official/public data can be imported later without changing the prediction/dashboard architecture.
