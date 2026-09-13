from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import csv, math, os, sqlite3

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "projects.csv"
DB = BASE / "data" / "sih26103.db"

app = FastAPI(
    title="SIH26103 Predictive Project Monitoring API",
    description="Predictive and prescriptive monitoring prototype for infrastructure projects.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEMO_USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "officer": {"password": "officer123", "role": "Project Officer"},
    "manager": {"password": "manager123", "role": "Management"},
}

class Login(BaseModel):
    username: str
    password: str

def load_projects():
    with open(DATA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def score_project(p):
    # Transparent rule-based baseline that can later be replaced/combined with ML.
    cost = float(p["original_cost_crore"])
    revised = float(p["revised_cost_crore"])
    planned = float(p["planned_duration_months"])
    elapsed = float(p["elapsed_months"])
    physical = float(p["physical_progress_pct"])
    financial = float(p["financial_progress_pct"])
    milestones = int(p["delayed_milestones"])
    issues = int(p["open_issues"])
    contract = int(p["contractual_risk"])

    cost_overrun = max(0, (revised - cost) / cost * 100)
    schedule_gap = max(0, elapsed / planned * 100 - physical)

    risk = (
        0.28 * min(cost_overrun * 3, 100)
        + 0.30 * min(schedule_gap * 2, 100)
        + 0.12 * min(milestones * 12, 100)
        + 0.10 * min(issues * 10, 100)
        + 0.12 * contract
        + 0.08 * max(0, financial - physical)
    )
    risk = round(min(max(risk, 0), 100), 1)

    predicted_cost = round(cost * (1 + min(0.45, (risk / 100) * 0.45)), 2)
    predicted_delay = round(max(0, (risk / 100) * planned * 0.45), 1)

    if risk >= 70:
        level = "High"
    elif risk >= 40:
        level = "Medium"
    else:
        level = "Low"

    drivers = []
    if cost_overrun > 5: drivers.append("Cost escalation")
    if schedule_gap > 10: drivers.append("Physical progress lag")
    if milestones >= 2: drivers.append("Milestone delays")
    if issues >= 3: drivers.append("Open implementation issues")
    if contract >= 60: drivers.append("Contractual risk")
    if not drivers: drivers.append("No dominant driver")

    recommendations = []
    if "Physical progress lag" in drivers:
        recommendations.append("Review the critical path and recover delayed activities.")
    if "Milestone delays" in drivers:
        recommendations.append("Escalate overdue milestones and assign accountable owners.")
    if "Cost escalation" in drivers:
        recommendations.append("Review escalation drivers and validate remaining-cost estimates.")
    if "Contractual risk" in drivers:
        recommendations.append("Initiate contract/claim review and mitigation planning.")
    if "Open implementation issues" in drivers:
        recommendations.append("Create an issue-resolution plan with target closure dates.")
    if not recommendations:
        recommendations.append("Continue monthly monitoring and verify the next milestone.")

    return {
        "risk_score": risk,
        "risk_level": level,
        "predicted_final_cost_crore": predicted_cost,
        "predicted_delay_months": predicted_delay,
        "drivers": drivers,
        "recommendations": recommendations,
    }

@app.get("/")
def root():
    return {"project": "SIH26103", "status": "running"}

@app.post("/api/login")
def login(data: Login):
    u = DEMO_USERS.get(data.username)
    if not u or u["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid demo credentials")
    return {"username": data.username, "role": u["role"], "message": "Login successful"}

@app.get("/api/projects")
def projects():
    result = []
    for p in load_projects():
        result.append({**p, **score_project(p)})
    return result

@app.get("/api/projects/{project_id}")
def project(project_id: str):
    for p in load_projects():
        if p["project_id"] == project_id:
            return {**p, **score_project(p)}
    raise HTTPException(status_code=404, detail="Project not found")

@app.get("/api/dashboard")
def dashboard():
    projects = [{**p, **score_project(p)} for p in load_projects()]
    total = len(projects)
    high = sum(x["risk_level"] == "High" for x in projects)
    medium = sum(x["risk_level"] == "Medium" for x in projects)
    low = total - high - medium
    total_cost = sum(float(x["original_cost_crore"]) for x in projects)
    predicted = sum(x["predicted_final_cost_crore"] for x in projects)
    avg_risk = round(sum(x["risk_score"] for x in projects) / total, 1) if total else 0

    return {
        "total_projects": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "original_cost_crore": round(total_cost, 2),
        "predicted_final_cost_crore": round(predicted, 2),
        "average_risk": avg_risk,
        "early_warnings": high + medium,
    }

@app.get("/api/alerts")
def alerts():
    items = []
    for p in load_projects():
        s = score_project(p)
        if s["risk_level"] in ("High", "Medium"):
            items.append({
                "project_id": p["project_id"],
                "project_name": p["project_name"],
                "risk_level": s["risk_level"],
                "risk_score": s["risk_score"],
                "drivers": s["drivers"],
                "recommendations": s["recommendations"],
            })
    return sorted(items, key=lambda x: x["risk_score"], reverse=True)

@app.get("/api/assistant")
def assistant(q: str = ""):
    projects = [{**p, **score_project(p)} for p in load_projects()]
    ql = q.lower()
    if "high" in ql or "risk" in ql:
        ranked = sorted(projects, key=lambda x: x["risk_score"], reverse=True)[:5]
        return {
            "answer": "Top projects requiring attention: " +
            "; ".join(f'{x["project_id"]} ({x["risk_level"]}, {x["risk_score"]})' for x in ranked)
        }
    if "cost" in ql:
        return {
            "answer": f'Portfolio original cost is ₹{sum(float(x["original_cost_crore"]) for x in projects):,.2f} crore. '
                      f'Predicted final cost is ₹{sum(x["predicted_final_cost_crore"] for x in projects):,.2f} crore.'
        }
    if "delay" in ql:
        return {
            "answer": f'The current demo model identifies {sum(x["predicted_delay_months"] > 1 for x in projects)} '
                      'projects with predicted delay above one month.'
        }
    return {
        "answer": "Ask about high-risk projects, cost escalation, or delay risk. "
                  "This prototype assistant uses the same project-monitoring API and can later be connected to an open-source LLM."
    }
