from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fast api.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel, Field
import csv, math, statistics

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "projects.csv"
FRONTEND_DIST = BASE / "fronten" / "dist"

app = FastAPI(
    title="PAIMANA AI Predictive Monitoring API",
    version="3.0.0",
    description="Hackathon prototype for predictive, explainable and prescriptive infrastructure monitoring."
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DEMO_USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "officer": {"password": "officer123", "role": "Project Officer"},
    "manager": {"password": "manager123", "role": "Management"},
}

class Login(BaseModel):
    username: str
    password: str

class ProjectCreate(BaseModel):
    project_name: str = Field(min_length=1)
    ministry: str = Field(min_length=1)
    sector: str = Field(min_length=1)
    state: str = Field(min_length=1)
    original_cost_crore: float = 0
    revised_cost_crore: float = 0
    expenditure_crore: float = 0
    physical_progress_pct: float = 0

ADDED_PROJECTS = []

def load_raw():
    with open(DATA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def enrich(p):
    """Transparent demo feature engineering.
    The source CSV is the uploaded project dataset; fields not present in it
    are derived deterministically for prototype demonstration and are NOT
    official PAIMANA values.
    """
    cost = float(p["original_cost_crore"])
    revised = float(p["revised_cost_crore"])
    expenditure = float(p["expenditure_crore"])
    progress = float(p["physical_progress_pct"])
    escalation = max(0.0, (revised-cost)/cost*100) if cost else 0.0
    financial = clamp(expenditure/cost*100) if cost else 0
    # Demo-only derived monitoring features.
    planned = 24 + (int(p["project_id"]) % 37)
    elapsed = max(6, round(planned * (progress/100) + (int(p["project_id"]) % 13) * 0.7))
    milestone_delay = max(0, round((elapsed/planned*100 - progress)/8))
    open_issues = max(0, round((100-progress)/18) + int(p["project_id"]) % 3)
    contractual = clamp(round(escalation*5 + (100-progress)*0.42 + (int(p["project_id"])%17)))
    schedule_gap = max(0, elapsed/planned*100-progress)

    # Explainable predictive baseline: cost + schedule + delivery + implementation.
    risk = (
        0.26*clamp(escalation*3.2) +
        0.27*clamp(schedule_gap*2.4) +
        0.14*clamp(milestone_delay*18) +
        0.11*clamp(open_issues*16) +
        0.12*contractual +
        0.10*clamp(max(0, financial-progress)*2)
    )
    # A small low-progress penalty catches stalled large projects early.
    risk += 6 if progress < 10 and elapsed > planned*0.25 else 0
    risk = round(clamp(risk), 1)
    level = "High" if risk >= 70 else ("Medium" if risk >= 40 else "Low")

    # Scenario forecast: current run-rate + risk premium, capped for demo stability.
    risk_premium = min(0.42, risk/100*0.42)
    predicted_final = round(max(revised, cost*(1+risk_premium)), 2)
    predicted_delay = round(max(0, (risk/100)*planned*0.55), 1)

    drivers=[]
    if escalation > 5: drivers.append(f"Cost escalation ({escalation:.1f}%)")
    if schedule_gap > 10: drivers.append(f"Physical progress lag ({schedule_gap:.1f} pts)")
    if milestone_delay >= 2: drivers.append(f"Milestone pressure ({milestone_delay} delayed)")
    if open_issues >= 3: drivers.append(f"Open implementation issues ({open_issues})")
    if contractual >= 60: drivers.append(f"Contractual exposure ({contractual}/100)")
    if not drivers: drivers=["No dominant risk driver"]

    actions=[]
    if schedule_gap > 10: actions.append("Review critical path and create a recovery schedule.")
    if escalation > 5: actions.append("Validate escalation drivers and remaining-cost estimate.")
    if milestone_delay >= 2: actions.append("Escalate overdue milestones with named accountable owners.")
    if contractual >= 60: actions.append("Start contract/claim review and mitigation planning.")
    if open_issues >= 3: actions.append("Create issue-resolution plan with target closure dates.")
    if not actions: actions=["Continue monthly monitoring and verify the next milestone."]

    # Confidence is deliberately framed as prototype confidence, not model accuracy.
    confidence = round(clamp(62 + progress*0.18 - abs(50-risk)*0.08), 0)

    return {
        **p,
        "cost_escalation_pct": round(escalation,2),
        "financial_progress_pct": round(financial,2),
        "planned_duration_months": planned,
        "elapsed_months": elapsed,
        "schedule_gap_pct": round(schedule_gap,2),
        "delayed_milestones": milestone_delay,
        "open_issues": open_issues,
        "contractual_risk": contractual,
        "risk_score": risk,
        "risk_level": level,
        "predicted_final_cost_crore": predicted_final,
        "predicted_delay_months": predicted_delay,
        "confidence_pct": confidence,
        "drivers": drivers,
        "recommendations": actions,
        "data_note": "Derived demo features; not official PAIMANA fields."
    }

def portfolio():
    return [enrich(p) for p in load_raw()] + [enrich(p) for p in ADDED_PROJECTS]

@app.get("/")
def root():
    return FileResponse(FRONTEND_DIST / "index.html")

@app.post("/api/login")
def login(data: Login):
    # Prototype requirement: accept any entered credentials.
    role = next((r for r in ("Management","Admin","Project Officer") if r.lower() in data.username.lower()), "Management")
    return {"username": data.username or "Demo User", "role": role}

@app.get("/api/projects")
def projects():
    return portfolio() + [enrich(p) for p in ADDED_PROJECTS]

@app.post("/api/projects")
def add_project(data: ProjectCreate):
    next_id = str(800000 + len(ADDED_PROJECTS) + 1)
    p = {"project_id": next_id, **data.model_dump()}
    ADDED_PROJECTS.append(p)
    return enrich(p)

@app.get("/api/projects/{project_id}")
def project(project_id: str):
    for p in portfolio():
        if p["project_id"] == project_id:
            return p
    raise HTTPException(status_code=404, detail="Project not found")

@app.get("/api/dashboard")
def dashboard():
    ps=portfolio()
    original=sum(float(p["original_cost_crore"]) for p in ps)
    revised=sum(float(p["revised_cost_crore"]) for p in ps)
    expenditure=sum(float(p["expenditure_crore"]) for p in ps)
    forecast=sum(p["predicted_final_cost_crore"] for p in ps)
    return {
        "total_projects":len(ps),
        "high_risk":sum(p["risk_level"]=="High" for p in ps),
        "medium_risk":sum(p["risk_level"]=="Medium" for p in ps),
        "low_risk":sum(p["risk_level"]=="Low" for p in ps),
        "early_warnings":sum(p["risk_level"]!="Low" for p in ps),
        "original_cost_crore":round(original,2),
        "revised_cost_crore":round(revised,2),
        "expenditure_crore":round(expenditure,2),
        "predicted_final_cost_crore":round(forecast,2),
        "forecast_uplift_pct":round(max(0,(forecast-original)/original*100),2),
        "average_progress":round(statistics.mean(float(p["physical_progress_pct"]) for p in ps),1),
        "average_risk":round(statistics.mean(p["risk_score"] for p in ps),1),
        "sector_count":len(set(p["sector"] for p in ps)),
    }

@app.get("/api/alerts")
def alerts():
    return sorted([
        {"project_id":p["project_id"],"project_name":p["project_name"],"risk_level":p["risk_level"],
         "risk_score":p["risk_score"],"drivers":p["drivers"],"recommendations":p["recommendations"]}
        for p in portfolio() if p["risk_level"]!="Low"
    ], key=lambda x:x["risk_score"], reverse=True)

@app.get("/api/analytics")
def analytics():
    ps=portfolio()
    sectors={}
    for p in ps:
        s=p["sector"]
        sectors.setdefault(s, {"sector":s,"projects":0,"high":0,"medium":0,"low":0,"cost":0,"progress":0,"risk":0})
        x=sectors[s]; x["projects"]+=1; x["cost"]+=float(p["original_cost_crore"]); x["progress"]+=float(p["physical_progress_pct"]); x["risk"]+=p["risk_score"]
        x[p["risk_level"].lower()]+=1
    rows=[]
    for x in sectors.values():
        x["cost"]=round(x["cost"],2); x["progress"]=round(x["progress"]/x["projects"],1); x["risk"]=round(x["risk"]/x["projects"],1)
        rows.append(x)
    return {"sectors":sorted(rows,key=lambda x:x["risk"],reverse=True),
            "top_cost_drivers":sorted(ps,key=lambda p:p["cost_escalation_pct"],reverse=True)[:8],
            "top_risk":sorted(ps,key=lambda p:p["risk_score"],reverse=True)[:8]}

@app.get("/api/assistant")
def assistant(q: str=""):
    ps=portfolio(); ql=q.lower().strip()
    if not ql:
        return {"answer":"Ask about high-risk projects, cost escalation, delays, sectors, or recommended actions."}
    if "high" in ql or "risk" in ql:
        top=sorted(ps,key=lambda p:p["risk_score"],reverse=True)[:6]
        return {"answer":"Priority queue: " + "; ".join(f'{p["project_id"]} {p["project_name"]} — {p["risk_level"]} ({p["risk_score"]}/100)' for p in top)}
    if "cost" in ql or "escalat" in ql:
        d=sum(float(p["original_cost_crore"]) for p in ps); r=sum(float(p["revised_cost_crore"]) for p in ps); f=sum(p["predicted_final_cost_crore"] for p in ps)
        return {"answer":f"Portfolio original cost is ₹{d:,.0f} Cr, revised cost is ₹{r:,.0f} Cr and the prototype forecast is ₹{f:,.0f} Cr. Highest escalation is {max(ps,key=lambda p:p['cost_escalation_pct'])['project_name']}."}
    if "delay" in ql or "time" in ql:
        top=sorted(ps,key=lambda p:p["predicted_delay_months"],reverse=True)[:5]
        return {"answer":"Largest predicted delays: " + "; ".join(f'{p["project_id"]} ({p["predicted_delay_months"]} months)' for p in top)}
    if "sector" in ql or "benchmark" in ql:
        a=analytics()["sectors"]
        return {"answer":"Highest average risk sectors: " + "; ".join(f'{x["sector"]} ({x["risk"]}/100)' for x in a[:5])}
    if "action" in ql or "intervention" in ql:
        p=max(ps,key=lambda p:p["risk_score"])
        return {"answer":f"First intervention candidate: {p['project_name']}. Recommended actions: " + " ".join(p["recommendations"])}
    return {"answer":"I can answer: Which projects are high risk? What is the portfolio cost? Which projects face delays? Which sectors need attention? What actions should officers take?"}
    if FRONTEND_DIST.exists():
        app.mount("/assets",StaticFiles(directory=FRONTEND_DIST / "assets"),name="assets")
