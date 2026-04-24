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
          <h1>What if you lived this day, every day, for the next 3 weeks?</h1>
          <p className="muted" style={{ maxWidth: 680, marginTop: 6, fontSize: 13, lineHeight: 1.55 }}>
            Enter one typical day. LifeOS simulates 100+ slightly-different versions of it
            rolling forward, scores every future, and tells you <b>(1)</b> how likely you are
            to hit your goal, <b>(2)</b> your burnout risk, and <b>(3)</b> which single habit
            change would help most.
          </p>
        </div>
        <div className="muted">Deterministic · Monte-Carlo · Zero ML</div>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="panel" style={{ marginBottom: 20, padding: "14px 18px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, fontSize: 13 }}>
          <div>
            <b style={{ color: "var(--accent)" }}>1 · Describe your day</b>
            <div className="muted" style={{ marginTop: 2 }}>Sleep, deep work, distractions, stress, learning.</div>
          </div>
          <div>
            <b style={{ color: "var(--accent)" }}>2 · Run the simulator</b>
            <div className="muted" style={{ marginTop: 2 }}>We roll many noisy copies of your day into the future.</div>
          </div>
          <div>
            <b style={{ color: "var(--accent)" }}>3 · Read the policy</b>
            <div className="muted" style={{ marginTop: 2 }}>You get metrics, a chart, and the habit that winners share.</div>
          </div>
        </div>
      </div>

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
                <p className="muted" style={{ marginTop: -6, marginBottom: 10, fontSize: 12 }}>
                  Three representative futures: the <b style={{ color: "var(--good)" }}>best</b>,
                  a typical <b>average</b>, and the <b style={{ color: "var(--danger)" }}>worst</b> run.
                  Click a button below to switch. All values are 0–1 scale.
                </p>
                <TrajectoryChart timelines={result.sample_timelines} />
              </div>
              <Strategy result={result} />
              <DecisionImpact data={impact} />
            </>
          ) : (
            <div className="panel">
              <h2>Results appear here</h2>
              <div className="empty">
                <div style={{ fontSize: 15, color: "var(--text)", marginBottom: 6 }}>
                  Ready when you are.
                </div>
                <div>
                  Click <b style={{ color: "var(--accent)" }}>Run simulation</b> and the engine will
                  roll {form.n_simulations} possible versions of your day forward {form.horizon_days} days,
                  then show you metrics, a chart, and the habits that worked.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
