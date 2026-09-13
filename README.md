# SIH26103 — PAIMANA AI Predictive Monitoring Command Center

## What this final prototype combines
This package combines the stronger parts of the two supplied prototypes:

- The **larger PAIMANA-style project portfolio dataset** from the Green Dashboard prototype.
- The **predictive + prescriptive monitoring engine** from the Predictive Project Monitoring prototype.
- A more polished **PAIMANA command-center UI** with navigation, portfolio KPIs, risk register, project drill-down, early-warning queue and analytics.
- Explainable risk drivers and recommended interventions.
- Cost and delay forecasts.
- Search + sector + risk filtering.
- Portfolio Intelligence Assistant.
- Sector benchmarking / comparative analytics.
- Separate role-based dashboards for Management, Project Officer and Admin.
- Simple prototype login page: any entered username/password is accepted and opens the selected role dashboard.
- Descriptive project data is available directly under the left-side Projects menu.
- Early Warnings is a dedicated full-page alert queue, opened from the left-side menu.
- Management can add a new project from the dashboard or Projects page; the new project is immediately analysed by the prototype engine.
- Optional open-source ML comparison experiment.

## Important data note
The included CSV is a demo snapshot supplied in the project materials. Because the supplied snapshot does not contain every CUF field needed for a validated predictive model, some monitoring features (planned duration, elapsed months, milestone pressure, open issues and contractual exposure) are **deterministically derived for demonstration**.

The resulting risk score is a **prototype analytical indicator**, not an official PAIMANA score. Do not present demo metrics as government/production model accuracy. For the hackathon, explain that the architecture is ready to replace these derived features with authorised historical OCMS/PAIMANA records.

## Architecture

React/Vite frontend
        ↓ REST
FastAPI backend
        ↓
CSV demo dataset
        ↓
Explainable predictive feature engine
        ↓
Risk score + cost forecast + delay forecast + early warnings + recommendations

Optional:
Historical OCMS/PAIMANA → feature store → statistical baseline vs ML models → model registry → API

## Run locally

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API: http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## Demo flow for judges

1. Start the backend and frontend.
2. Show the **Portfolio Attention** score and four executive KPIs.
3. Open the **Project Risk Register**.
4. Filter to **High** risk and click the top project.
5. Explain:
   - risk score,
   - forecast final cost,
   - predicted delay,
   - risk drivers,
   - recommended intervention.
6. Show the **Early Warning Queue** and explain prioritisation.
7. Open **Analytics** and demonstrate sector benchmarking.
8. Ask the Project Intelligence Assistant:
   - “Which projects are high risk?”
   - “What is the portfolio cost?”
   - “Which projects face delays?”
   - “Which sectors need attention?”
   - “What actions should officers take?”
9. Explain the production roadmap: replace demo-derived fields with authorised OCMS/PAIMANA history and evaluate statistical baselines against ML models.

## How this maps to the problem statement

| Requirement | Prototype component |
|---|---|
| Cost overrun prediction | Forecast final cost |
| Time overrun prediction | Predicted delay months |
| Project risk scoring | 0–100 explainable attention score |
| Early warning | Priority queue + risk filters |
| Benchmarking | Sector risk analytics |
| Cost escalation drivers | Driver chips + cost delta |
| AI dashboard | Command-center UI |
| LLM assistant | Dataset-grounded assistant endpoint |
| Open-source stack | React, Vite, FastAPI, scikit-learn |
| Model comparison | `ml/train_model.py` |
| Documentation/deployment | This README + docs |

## Production upgrade roadmap

- Import monthly CUF/PAIMANA records into PostgreSQL.
- Create time-aware project snapshots instead of one-row-per-project data.
- Define labels such as “cost overrun > X% within next N months” and “schedule overrun > Y months”.
- Train leakage-safe models using historical cut-off dates.
- Compare statistical baselines, gradient boosting / random forest and calibrated risk models.
- Add SHAP or permutation importance for explainability.
- Add drift monitoring, model versioning and audit logs.
- Connect an open-source LLM through retrieval over approved project records and reports.
- Add authenticated RBAC and government-network deployment controls.

## Demo credentials
The UI role selector is intentionally lightweight for the hackathon. The backend also contains demo-only credentials:
- `admin / admin123`
- `officer / officer123`
- `manager / manager123`

Never use these credentials in production.


## Updated hackathon demo flow

1. Open the frontend and start at the **Login** page.
2. Enter any username and password, select **Management**, **Project Officer**, or **Admin**, then click **Login**.
3. **Management Dashboard:** show executive KPIs and use **＋ Add Project** to demonstrate project creation.
4. **Project Officer Dashboard:** show the priority queue, project drill-down and recommended interventions.
5. **Admin Dashboard:** show portfolio/system overview and complete monitoring access.
6. Click **Projects** in the left navigation to view descriptive data including ministry, sector, state, original/revised cost, expenditure and physical progress.
7. Click **Early Warnings** to open the dedicated active-warning queue. Select any warning to jump to its detailed project record.
8. Use **Analytics** for sector benchmarking and **Reports** for a printable management summary.

### Login note
This is intentionally a **prototype-only login**. No credentials are validated. The selected role determines which dashboard is displayed. Do not use this authentication approach in production.

### Project addition note
Projects added through the Management UI are held in backend memory for the running prototype session and are automatically passed through the same descriptive/predictive/prescriptive enrichment logic. Restarting the backend resets added demo projects; production should persist projects in an authorised database.
