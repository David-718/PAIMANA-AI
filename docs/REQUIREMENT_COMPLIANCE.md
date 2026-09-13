# SIH26103 — PAIMANA AI Predictive & Prescriptive Monitoring
## Requirement-to-Prototype Compliance Map

This integrated prototype is designed around the supplied SIH26103 problem statement.

| Requirement | Prototype coverage |
|---|---|
| Cost overrun prediction | Project-level predicted final cost + escalation risk |
| Time overrun prediction | Predicted delay and schedule-gap indicators |
| Project risk scoring | 0–100 composite risk score with High/Medium/Low bands |
| Early warning system | Prioritised warning queue with drivers and interventions |
| Benchmarking | Sector-level comparative analytics and project ranking |
| Cost escalation driver analysis | Explainable drivers based on cost, expenditure, progress and schedule signals |
| AI-powered dashboard | Dashboard, portfolio KPIs, filters, drill-down and analytics |
| LLM-enabled assistant | Project Intelligence Assistant for natural-language monitoring questions |
| Statistical vs ML assessment | Model-comparison module/documentation using conventional regression and ML |
| CUF field assessment | CUF/current-field feature map plus additional-variable recommendations |
| Forecast modelling | Forecast-oriented predicted final cost/delay outputs |
| Open-source stack | Python, FastAPI, pandas, NumPy, scikit-learn and a lightweight web UI |
| Documentation/deployment | README, demo guide, data notes, run scripts and this compliance map |

## Data integrity note
The supplied prototype datasets are suitable for demonstrating the workflow, UI and analytical logic. They are not a substitute for the authorised full historical OCMS/PAIMANA monthly database. Where historical target labels or CUF fields are unavailable in the supplied snapshot, demo/derived indicators are clearly documented rather than presented as official PAIMANA predictions.

For production deployment, connect authorised monthly PAIMANA/OCMS snapshots, retain time-series history, train/validate on historical outcomes, calibrate thresholds with domain experts, and audit model performance by sector/Ministry.
