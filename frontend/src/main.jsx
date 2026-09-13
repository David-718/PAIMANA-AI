import React,{useEffect,useMemo,useState} from "react";
import {createRoot} from "react-dom/client";
import "./style.css";

const API="http://paimana-ai-backend-uy1z.onrender.com";
const money=n=>new Intl.NumberFormat("en-IN",{maximumFractionDigits:0}).format(Number(n)||0);
const pct=n=>`${Number(n||0).toFixed(1)}%`;

function Badge({level}){return <span className={`badge ${String(level).toLowerCase()}`}>{level}</span>}
function Bar({value}){return <div className="bar"><i style={{width:`${Math.min(100,Math.max(0,value))}%`}}/></div>}
function Spark({value=50}){return <div className="spark">{[20,35,25,45,30].map((x,i)=><i key={i} style={{height:`${Math.min(100,x+value*(i%2?.4:.55))}%`}}/>)}</div>}

function App(){
 const [loggedIn,setLoggedIn]=useState(true),[user,setUser]=useState({username:"Demo User",role:"Management"});
 const [dash,setDash]=useState(null),[ps,setPs]=useState([]),[sel,setSel]=useState(null);
 const [search,setSearch]=useState(""),[sector,setSector]=useState("All"),[risk,setRisk]=useState("All");
 const [tab,setTab]=useState("Dashboard"),[q,setQ]=useState(""),[ans,setAns]=useState(""),[loading,setLoading]=useState(false),[showAdd,setShowAdd]=useState(false);

 const load=async()=>{setLoading(true);try{
   const [d,p]=await Promise.all([fetch(API+"/api/dashboard").then(r=>r.json()),fetch(API+"/api/projects").then(r=>r.json())]);
   setDash(d);setPs(p);setSel(p[0]||null);
 }catch(e){console.error(e)}finally{setLoading(false)}};
 useEffect(()=>{if(loggedIn)load()},[loggedIn]);

 const sectors=useMemo(()=>["All",...new Set(ps.map(p=>p.sector))],[ps]);
 const filtered=useMemo(()=>ps.filter(p=>
   (sector==="All"||p.sector===sector)&&(risk==="All"||p.risk_level===risk)&&
   `${p.project_id} ${p.project_name} ${p.ministry} ${p.state}`.toLowerCase().includes(search.toLowerCase())
 ),[ps,sector,risk,search]);

 const ask=async()=>{if(!q.trim())return;const r=await fetch(API+"/api/assistant?q="+encodeURIComponent(q));setAns((await r.json()).answer)};
 const addProject=async(form)=>{
   try{
    const r=await fetch(API+"/api/projects",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(form)});
    if(!r.ok) throw new Error("Unable to add project");
    setShowAdd(false); await load(); setTab("Projects");
   }catch(e){alert(e.message)}
 };

 if(loading||!dash)return <div className="loading"><div className="loader">P</div><b>PAIMANA Predictive Intelligence</b><span>Loading command center…</span></div>;

 return <div className="shell">
  <aside>
   <div className="brand"><div className="logo">P</div><div><b>PAIMANA</b><small>AI COMMAND CENTER</small></div></div>
   <div className="navTitle">MONITORING</div>
   {["Dashboard","Projects","Early Warnings","Analytics","Reports"].map(x=><button key={x} className={tab===x?"nav active":"nav"} onClick={()=>setTab(x)}><span>{x==="Dashboard"?"◈":x==="Projects"?"▣":x==="Early Warnings"?"⚠":x==="Analytics"?"◉":"▤"}</span>{x}</button>)}
   <div className="sideCard"><div className="liveDot"/> <b>Predictive engine</b><small>ONLINE • Explainable baseline</small><em>AI + ML ready</em></div>
   <div className="sideFoot">SIH26103<br/><span>Infrastructure Monitoring</span></div>
  </aside>
  <main>
   <header><div><div className="crumb">MINISTRY PROJECT MONITORING / {tab.toUpperCase()}</div><h1>{user.role} Dashboard</h1><p>Predict risks early · understand drivers · take action</p></div>
    <div className="head"><div className="user"><span/> {user.role}</div><button className="logout" onClick={()=>{setLoggedIn(false);setUser(null)}}>Logout</button></div>
   </header>

   {tab==="Dashboard"&&<RoleDashboard role={user.role} dash={dash} ps={ps} setTab={setTab} setSel={setSel} ask={ask} q={q} setQ={setQ} ans={ans} onAdd={()=>setShowAdd(true)}/>}
   {tab==="Projects"&&<ProjectsPage ps={ps} filtered={filtered} sectors={sectors} search={search} setSearch={setSearch} sector={sector} setSector={setSector} risk={risk} setRisk={setRisk} sel={sel} setSel={setSel} role={user.role} onAdd={()=>setShowAdd(true)}/>}
   {tab==="Early Warnings"&&<WarningsPage ps={ps} setSel={setSel} setTab={setTab}/>}
   {tab==="Analytics"&&<Analytics ps={ps}/>}
   {tab==="Reports"&&<Reports dash={dash} ps={ps}/>}

   <footer>Prototype • Open-source stack • Demo dataset + derived fields • Risk index is not an official PAIMANA score</footer>
  </main>
  {showAdd&&user.role==="Management"&&<AddProject onClose={()=>setShowAdd(false)} onAdd={addProject}/>}
 </div>
}

function RoleDashboard({role,dash,ps,setTab,setSel,ask,q,setQ,ans,onAdd}){
 const title=role==="Management"?"Executive Portfolio Overview":role==="Admin"?"System & Portfolio Administration":"Officer Action Center";
 const desc=role==="Management"?"Portfolio health, financial exposure and strategic intervention priorities.":role==="Admin"?"System status, data coverage and complete portfolio visibility.":"Project-level warnings, delays and recommended actions for field review.";
 const top=ps.filter(p=>p.risk_level!=="Low").sort((a,b)=>b.risk_score-a.risk_score).slice(0,5);
 return <><section className="hero"><div><span className="overline">PAIMANA • {role.toUpperCase()}</span><h2>{title}</h2><p>{desc}</p><div className="heroTags"><span>● {dash.total_projects} projects</span><span>◉ {dash.sector_count} sectors</span><span>↗ {dash.early_warnings} alerts</span></div></div><div className="heroScore"><small>PORTFOLIO ATTENTION</small><b>{dash.average_risk}</b><span>/100 risk index</span><Spark value={dash.average_risk}/></div></section>
 <section className="kpis"><K label="Projects monitored" value={dash.total_projects} sub={`${dash.high_risk} high priority`} icon="▦"/><K label="High risk" value={dash.high_risk} sub={`${dash.early_warnings} early warnings`} icon="!" danger/><K label="Portfolio cost" value={`₹${money(dash.original_cost_crore)} Cr`} sub={`Revised ₹${money(dash.revised_cost_crore)} Cr`} icon="₹"/><K label="Forecast final cost" value={`₹${money(dash.predicted_final_cost_crore)} Cr`} sub={`+${pct(dash.forecast_uplift_pct)} vs original`} icon="↗"/></section>
 <section className="roleGrid">
  <div className="panel"><div className="ph"><div><h2>{role==="Management"?"Priority decisions":role==="Admin"?"System overview":"My priority queue"}</h2><p>Top signals from the predictive monitoring engine.</p></div>{role==="Management"&&<button className="primary" onClick={onAdd}>＋ Add Project</button>}</div>
   <div className="warningList">{top.map(p=><div className="warning" key={p.project_id} onClick={()=>{setSel(p);setTab("Projects")}}><Badge level={p.risk_level}/><div><b>{p.project_id} · {p.project_name}</b><small>{p.drivers[0]}</small></div><strong>{p.risk_score}</strong></div>)}</div>
   {role==="Admin"&&<div className="adminTiles"><div><b>API</b><span>Online</span></div><div><b>Data</b><span>{dash.total_projects} records</span></div><div><b>Engine</b><span>Explainable</span></div></div>}
  </div>
  <div className="panel"><div className="aiLabel">✦ PROJECT INTELLIGENCE ASSISTANT</div><h2>Ask the portfolio</h2><p>Query the same monitoring dataset used by the risk engine.</p><div className="ask"><input value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>e.key==="Enter"&&ask()} placeholder="e.g. Which projects are high risk?"/><button onClick={ask}>Ask AI</button></div>{ans&&<div className="answer">✦ {ans}</div>}<div className="quickLinks"><button onClick={()=>setTab("Projects")}>View project data →</button><button onClick={()=>setTab("Early Warnings")}>View early warnings →</button><button onClick={()=>setTab("Analytics")}>Open analytics →</button></div></div>
 </section></>
}

function K({label,value,sub,icon,danger}){return <div className="kpi"><div className={`icon ${danger?"danger":""}`}>{icon}</div><span>{label}</span><b>{value}</b><small>{sub}</small></div>}

function ProjectsPage({ps,filtered,sectors,search,setSearch,sector,setSector,risk,setRisk,sel,setSel,role,onAdd}){
 return <><section className="sectionIntro"><div><span className="overline dark">DESCRIPTIVE MONITORING DATA</span><h2>Projects</h2><p>Explore the descriptive portfolio data: ministry, sector, state, costs, expenditure, physical progress and predictive indicators.</p></div>{role==="Management"&&<button className="primary" onClick={onAdd}>＋ Add Project</button>}</section>
 <section className="layout"><div className="panel register"><div className="ph"><div><h2>Project Portfolio</h2><p>{filtered.length} projects match the current filters.</p></div></div><div className="filters"><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="⌕ Search project, ministry, state…"/><select value={sector} onChange={e=>setSector(e.target.value)}>{sectors.map(x=><option key={x}>{x}</option>)}</select><select value={risk} onChange={e=>setRisk(e.target.value)}><option>All</option><option>High</option><option>Medium</option><option>Low</option></select></div>
 <div className="table"><table><thead><tr><th>Project / Ministry</th><th>Sector</th><th>State</th><th>Original Cost</th><th>Expenditure</th><th>Progress</th><th>Risk</th></tr></thead><tbody>{filtered.map(p=><tr key={p.project_id} className={sel?.project_id===p.project_id?"chosen":""} onClick={()=>setSel(p)}><td><b>{p.project_name}</b><small>{p.project_id} · {p.ministry}</small></td><td>{p.sector}</td><td>{p.state}</td><td>₹{money(p.original_cost_crore)} Cr</td><td>₹{money(p.expenditure_crore)} Cr</td><td><Bar value={p.physical_progress_pct}/><small>{pct(p.physical_progress_pct)}</small></td><td><Badge level={p.risk_level}/><small>{p.risk_score}/100</small></td></tr>)}</tbody></table></div></div>{sel&&<Detail p={sel}/>}</section></>
}

function WarningsPage({ps,setSel,setTab}){
 const warnings=ps.filter(p=>p.risk_level!=="Low").sort((a,b)=>b.risk_score-a.risk_score);
 return <section className="warningsPage"><div className="sectionIntro"><div><span className="overline dark">PREDICTIVE EARLY-WARNING SYSTEM</span><h2>Early Warnings</h2><p>Prioritised signals requiring review, with transparent drivers and recommended interventions.</p></div><span className="live">● {warnings.length} ACTIVE</span></div>
 <div className="warningCards">{warnings.map(p=><div className="warningCard" key={p.project_id} onClick={()=>{setSel(p);setTab("Projects")}}><div className="warningTop"><Badge level={p.risk_level}/><strong>{p.risk_score}/100</strong></div><h3>{p.project_name}</h3><small>{p.project_id} · {p.ministry} · {p.state}</small><div className="driver">⚠ {p.drivers.join(" • ")}</div><div className="recommend">✓ {p.recommendations[0]}</div></div>)}</div>
 </section>
}

function Detail({p}){return <div className="panel detail"><div className="ph"><div><span className="pid">{p.project_id} · {p.state}</span><h2>{p.project_name}</h2></div><Badge level={p.risk_level}/></div>
 <div className="riskBox"><div><small>PREDICTIVE ATTENTION SCORE</small><strong>{p.risk_score}<i>/100</i></strong><span>Prototype confidence {p.confidence_pct}%</span></div><div className={`ring ${p.risk_level.toLowerCase()}`}><b>{p.risk_level}</b></div></div>
 <div className="forecast"><div><small>Forecast final cost</small><b>₹{money(p.predicted_final_cost_crore)} Cr</b></div><div><small>Predicted delay</small><b>{p.predicted_delay_months} mo</b></div><div><small>Physical progress</small><b>{pct(p.physical_progress_pct)}</b></div></div>
 <h3>Descriptive project data</h3><div className="dataGrid"><span><b>Ministry</b>{p.ministry}</span><span><b>Sector</b>{p.sector}</span><span><b>State</b>{p.state}</span><span><b>Original cost</b>₹{money(p.original_cost_crore)} Cr</span><span><b>Revised cost</b>₹{money(p.revised_cost_crore)} Cr</span><span><b>Expenditure</b>₹{money(p.expenditure_crore)} Cr</span><span><b>Financial progress</b>{pct(p.financial_progress_pct)}</span><span><b>Cost escalation</b>{pct(p.cost_escalation_pct)}</span></div>
 <h3>Why is this project flagged?</h3><div className="chips">{p.drivers.map(x=><span key={x}>• {x}</span>)}</div><h3>Recommended intervention</h3><ul>{p.recommendations.map(x=><li key={x}>✓ {x}</li>)}</ul>
 <div className="miniMeta"><span>Planned {p.planned_duration_months} mo</span><span>Elapsed {p.elapsed_months} mo</span><span>Milestone pressure {p.delayed_milestones}</span><span>Open issues {p.open_issues}</span></div>
 <div className="note">Derived monitoring features are synthetic for demonstration. Replace with authorised historical OCMS/PAIMANA data before model validation or operational use.</div></div>}

function Analytics({ps}){const sectors={};ps.forEach(p=>{if(!sectors[p.sector])sectors[p.sector]={name:p.sector,n:0,r:0,c:0,p:0};let s=sectors[p.sector];s.n++;s.r+=p.risk_score;s.c+=+p.original_cost_crore;s.p+=+p.physical_progress_pct});const rows=Object.values(sectors).map(s=>({...s,r:s.r/s.n,p:s.p/s.n})).sort((a,b)=>b.r-a.r);return <section className="analytics"><div className="panel"><div className="ph"><div><span className="overline dark">COMPARATIVE DESCRIPTIVE + PREDICTIVE ANALYTICS</span><h2>Sector risk benchmarking</h2><p>Average predictive attention score by sector.</p></div></div><div className="sectorGrid">{rows.map(s=><div className="sector" key={s.name}><div><b>{s.name}</b><small>{s.n} projects · ₹{money(s.c)} Cr</small></div><strong>{s.r.toFixed(1)}</strong><Bar value={s.r}/><small>Avg progress {s.p.toFixed(1)}%</small></div>)}</div></div><div className="panel insight"><div className="aiLabel">◉ ANALYTICAL INSIGHT</div><h2>Where should officers look first?</h2><p>{rows[0]?.name} currently has the highest average prototype risk index. Use this ranking to focus review resources, then inspect project-level drivers before intervention.</p><div className="legend"><span><i className="dot high"/>High ≥70</span><span><i className="dot medium"/>Medium 40–69</span><span><i className="dot low"/>Low &lt;40</span></div></div></section>}

function Reports({dash,ps}){const avg=ps.length?ps.reduce((a,p)=>a+p.physical_progress_pct,0)/ps.length:0;return <section className="reportGrid"><div className="panel reportHero"><span className="overline dark">MANAGEMENT REPORT</span><h2>Portfolio monitoring summary</h2><p>Prototype-ready executive snapshot generated from the current project dataset.</p><div className="reportStats"><div><b>{dash.total_projects}</b><span>Projects</span></div><div><b>{dash.high_risk}</b><span>High risk</span></div><div><b>{dash.early_warnings}</b><span>Warnings</span></div><div><b>{avg.toFixed(1)}%</b><span>Avg progress</span></div></div><button className="primary" onClick={()=>window.print()}>Print / Save Report</button></div><div className="panel"><h2>Report contents</h2><ul className="reportList"><li>Portfolio cost and forecast exposure</li><li>High-risk project queue</li><li>Early-warning drivers and interventions</li><li>Descriptive project data</li><li>Sector benchmarking</li></ul></div></section>}

function AddProject({onClose,onAdd}){const [f,setF]=useState({project_name:"",ministry:"",sector:"Roads & Highways",state:"",original_cost_crore:"1000",revised_cost_crore:"1000",expenditure_crore:"0",physical_progress_pct:"0"});const upd=(k,v)=>setF(x=>({...x,[k]:v}));return <div className="modalBackdrop" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><div className="modal"><div className="ph"><div><span className="overline dark">MANAGEMENT ACTION</span><h2>Add New Project</h2><p>Add a project to the live prototype portfolio.</p></div><button className="close" onClick={onClose}>×</button></div><div className="formGrid">{[["project_name","Project name"],["ministry","Ministry"],["sector","Sector"],["state","State / region"],["original_cost_crore","Original cost (₹ Cr)"],["revised_cost_crore","Revised cost (₹ Cr)"],["expenditure_crore","Expenditure (₹ Cr)"],["physical_progress_pct","Physical progress (%)"]].map(([k,l])=><label key={k}>{l}<input value={f[k]} onChange={e=>upd(k,e.target.value)} /></label>)}</div><div className="modalActions"><button className="ghost" onClick={onClose}>Cancel</button><button className="primary" onClick={()=>onAdd(f)}>Add Project</button></div></div></div>}

createRoot(document.getElementById("root")).render(<App/>);
