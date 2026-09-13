import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import "./style.css";

const API = "http://127.0.0.1:8000";

function RiskBadge({level}) {
  return <span className={"badge " + level.toLowerCase()}>{level}</span>;
}

function App() {
  const [dash, setDash] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selected, setSelected] = useState(null);
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [role, setRole] = useState("Management");

  const load = async () => {
    const [d,p] = await Promise.all([
      fetch(API+"/api/dashboard").then(r=>r.json()),
      fetch(API+"/api/projects").then(r=>r.json())
    ]);
    setDash(d); setProjects(p); if(p.length) setSelected(p[0]);
  };

  useEffect(()=>{ load().catch(e=>console.error(e)); },[]);

  const ask = async () => {
    const r = await fetch(API+"/api/assistant?q="+encodeURIComponent(q));
    const x = await r.json(); setAnswer(x.answer);
  };

  if (!dash) return <div className="loading">Starting predictive monitoring dashboard…<br/><small>Make sure FastAPI is running on port 8000.</small></div>;

  return <div className="app">
    <header>
      <div>
        <div className="eyebrow">SIH26103 • SMART AUTOMATION</div>
        <h1>Predictive Project Monitoring</h1>
        <p>From descriptive monitoring → early warning → prescriptive action</p>
      </div>
      <select value={role} onChange={e=>setRole(e.target.value)}>
        <option>Management</option><option>Project Officer</option><option>Admin</option>
      </select>
    </header>

    <main>
      <section className="cards">
        <div className="card"><span>Total Projects</span><strong>{dash.total_projects}</strong></div>
        <div className="card"><span>High Risk</span><strong>{dash.high_risk}</strong></div>
        <div className="card"><span>Early Warnings</span><strong>{dash.early_warnings}</strong></div>
        <div className="card"><span>Average Risk</span><strong>{dash.average_risk}</strong></div>
        <div className="card wide"><span>Predicted Portfolio Final Cost</span><strong>₹{dash.predicted_final_cost_crore.toLocaleString()} Cr</strong></div>
      </section>

      <section className="grid">
        <div className="panel">
          <div className="panel-title"><h2>Project Risk Register</h2><span>{role} view</span></div>
          <div className="table-wrap">
            <table><thead><tr><th>ID</th><th>Project</th><th>Sector</th><th>Progress</th><th>Risk</th></tr></thead>
            <tbody>{projects.map(p=><tr key={p.project_id} onClick={()=>setSelected(p)}>
              <td>{p.project_id}</td><td><b>{p.project_name}</b><small>{p.ministry}</small></td><td>{p.sector}</td>
              <td>{p.physical_progress_pct}%</td><td><RiskBadge level={p.risk_level}/><small>{p.risk_score}/100</small></td>
            </tr>)}</tbody></table>
          </div>
        </div>

        {selected && <div className="panel detail">
          <div className="panel-title"><h2>{selected.project_name}</h2><RiskBadge level={selected.risk_level}/></div>
          <div className="metric"><span>Risk score</span><b>{selected.risk_score}/100</b></div>
          <div className="bar"><i style={{width:selected.risk_score+"%"}}/></div>
          <div className="two">
            <div><span>Predicted final cost</span><b>₹{selected.predicted_final_cost_crore} Cr</b></div>
            <div><span>Predicted delay</span><b>{selected.predicted_delay_months} months</b></div>
          </div>
          <h3>Risk drivers</h3>
          <ul>{selected.drivers.map(x=><li key={x}>{x}</li>)}</ul>
          <h3>Recommended actions</h3>
          <ul>{selected.recommendations.map(x=><li key={x}>{x}</li>)}</ul>
          <div className="meta">{selected.state} • {selected.sector} • Original ₹{selected.original_cost_crore} Cr</div>
        </div>}
      </section>

      <section className="panel assistant">
        <div><div className="eyebrow">PROJECT INTELLIGENCE ASSISTANT</div><h2>Ask the portfolio</h2></div>
        <div className="ask"><input value={q} onChange={e=>setQ(e.target.value)} placeholder="e.g. Which projects are high risk?"/>
        <button onClick={ask}>Ask</button></div>
        {answer && <div className="answer">{answer}</div>}
      </section>

      <section className="panel">
        <div className="panel-title"><h2>Early Warning Alerts</h2><button onClick={load}>Refresh</button></div>
        <div className="alerts">{projects.filter(p=>p.risk_level!=="Low").map(p=>
          <div className="alert" key={p.project_id}><RiskBadge level={p.risk_level}/><div><b>{p.project_id} — {p.project_name}</b><p>{p.drivers.join(" • ")}</p></div></div>
        )}</div>
      </section>
    </main>
    <footer>Prototype • Synthetic demo data • Replace with authorised PAIMANA/public data for deployment</footer>
  </div>
}

createRoot(document.getElementById("root")).render(<App />);
