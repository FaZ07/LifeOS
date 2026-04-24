import React, { useState } from "react";
import InputPanel from "./components/InputPanel.jsx";
import Metrics from "./components/Metrics.jsx";
import TrajectoryChart from "./components/TrajectoryChart.jsx";
import Strategy from "./components/Strategy.jsx";
import DecisionImpact from "./components/DecisionImpact.jsx";
import { simulate, decisionImpact } from "./api.js";

const DEFAULTS = {
  sleep_hours: 7.0,
  deep_work_hours: 3.5,
  distraction_level: "medium",
  stress_level: 5,
  learning_hours: 1.0,
  goal_deadline_days: 30,
  n_simulations: 120,
  horizon_days: 21,
};

export default function App() {
  const [form, setForm] = useState(DEFAULTS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [impact, setImpact] = useState(null);

  async function handleSimulate() {
    setLoading(true); setError(null);
    try {
      const res = await simulate(form);
      setResult(res); setImpact(null);
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }

  async function handleImpact() {
    setLoading(true); setError(null);
    try {
      const res = await decisionImpact(form);
      setResult(res.baseline); setImpact(res);
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <div className="tag">LifeOS <span className="badge-accent">·</span> Counterfactual Decision Engine</div>
          <h1>Simulate your future. Read the policy. Ship yourself.</h1>
        </div>
        <div className="muted">Deterministic · Monte-Carlo · Zero ML</div>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="grid">
        <InputPanel
          form={form}
          onChange={setForm}
          onSubmit={handleSimulate}
          onImpact={handleImpact}
          loading={loading}
        />

        <div>
          {result ? (
            <>
              <Metrics result={result} />
              <div className="panel">
                <h2>Sample trajectories</h2>
                <TrajectoryChart timelines={result.sample_timelines} />
              </div>
              <Strategy result={result} />
              <DecisionImpact data={impact} />
            </>
          ) : (
            <div className="panel">
              <h2>Results</h2>
              <div className="empty">
                Fill in your day and run a simulation — the engine will roll
                {" "}{form.n_simulations} possible futures forward {form.horizon_days} days.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
