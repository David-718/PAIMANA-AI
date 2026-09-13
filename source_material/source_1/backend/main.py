from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import csv

DATA=Path(__file__).resolve().parent.parent/"data"/"projects.csv"
app=FastAPI(title="SIH26103 Predictive Project Monitoring",version="2.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

USERS={"admin":("admin123","Admin"),"officer":("officer123","Project Officer"),"manager":("manager123","Management")}
class Login(BaseModel):
    username:str
    password:str

def load():
    with open(DATA,newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def analyse(p):
    o=float(p["original_cost_crore"]); r=float(p["revised_cost_crore"]); e=float(p["expenditure_crore"]); prog=float(p["physical_progress_pct"])
    esc=max(0,(r-o)/o*100) if o else 0
    util=e/r*100 if r else 0
    score=min(100,round(esc*4+(100-prog)*.55+max(0,35-util)*.35,1))
    level="High" if score>=65 else "Medium" if score>=35 else "Low"
    drivers=[]
    if esc>5: drivers.append("Cost escalation")
    if prog<50: drivers.append("Low physical progress")
    if prog<80: drivers.append("Progress gap")
    if util<25: drivers.append("Low expenditure utilisation")
    if not drivers: drivers=["No dominant indicator"]
    actions=[]
    if "Cost escalation" in drivers: actions.append("Review cost escalation drivers and validate the latest estimate.")
    if "Low physical progress" in drivers: actions.append("Review critical activities and prepare a recovery schedule.")
    if "Progress gap" in drivers: actions.append("Check milestone dependencies and assign accountable owners.")
    if "Low expenditure utilisation" in drivers: actions.append("Review procurement, approvals and fund-utilisation bottlenecks.")
    if not actions: actions=["Continue monthly monitoring and verify the next milestone."]
    predicted=round(o*(1+min(.35,esc/100+score/400)),2)
    return {"cost_escalation_pct":round(esc,2),"expenditure_ratio_pct":round(util,2),"risk_score":score,"risk_level":level,"predicted_final_cost_crore":predicted,"predicted_delay_months":round(score/25,1),"drivers":drivers,"recommendations":actions}

@app.get("/")
def home(): return {"status":"running","project":"SIH26103"}

@app.post("/api/login")
def login(x:Login):
    u=USERS.get(x.username)
    if not u or u[0]!=x.password: raise HTTPException(401,"Invalid credentials")
    return {"username":x.username,"role":u[1]}

@app.get("/api/projects")
def projects(): return [{**p,**analyse(p)} for p in load()]

@app.get("/api/projects/{pid}")
def project(pid:str):
    for p in load():
        if p["project_id"]==pid:return {**p,**analyse(p)}
    raise HTTPException(404,"Project not found")

@app.get("/api/dashboard")
def dashboard():
    ps=projects(); o=sum(float(p["original_cost_crore"]) for p in ps); r=sum(float(p["revised_cost_crore"]) for p in ps)
    return {"total_projects":len(ps),"high_risk":sum(p["risk_level"]=="High" for p in ps),"medium_risk":sum(p["risk_level"]=="Medium" for p in ps),"low_risk":sum(p["risk_level"]=="Low" for p in ps),"original_cost_crore":round(o,2),"revised_cost_crore":round(r,2),"expenditure_crore":round(sum(float(p["expenditure_crore"]) for p in ps),2),"cost_escalation_pct":round(max(0,(r-o)/o*100),2),"average_progress":round(sum(float(p["physical_progress_pct"]) for p in ps)/len(ps),1),"early_warnings":sum(p["risk_level"]!="Low" for p in ps)}

@app.get("/api/alerts")
def alerts(): return sorted([p for p in projects() if p["risk_level"]!="Low"],key=lambda x:x["risk_score"],reverse=True)

@app.get("/api/assistant")
def assistant(q:str=""):
    ps=projects(); q=q.lower()
    if "high" in q or "risk" in q:
        top=sorted(ps,key=lambda x:x["risk_score"],reverse=True)[:5]
        return {"answer":"Top attention projects: "+"; ".join(f'{p["project_id"]} – {p["project_name"]} ({p["risk_level"]}, {p["risk_score"]})' for p in top)}
    if "cost" in q:return {"answer":f'Portfolio original cost: ₹{sum(float(p["original_cost_crore"]) for p in ps):,.2f} crore; revised cost: ₹{sum(float(p["revised_cost_crore"]) for p in ps):,.2f} crore.'}
    if "sector" in q:
        d={}
        for p in ps:d[p["sector"]]=d.get(p["sector"],0)+1
        return {"answer":"Projects by sector: "+", ".join(f"{k}: {v}" for k,v in sorted(d.items(),key=lambda x:x[1],reverse=True))}
    return {"answer":"Try: Which projects are high risk? | What is the portfolio cost? | Show sector distribution."}
