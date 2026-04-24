import React from "react";

export default function InputPanel({ form, onChange, onSubmit, onImpact, loading }) {
  const set = (k) => (e) => onChange({ ...form, [k]: e.target.type === "number" ? parseFloat(e.target.value) : e.target.value });

  return (
    <div className="panel">
      <h2>Daily inputs</h2>

      <div className="row-2">
        <label className="field">
          <span>Sleep hours</span>
          <input type="number" step="0.1" min="0" max="24" value={form.sleep_hours} onChange={set("sleep_hours")} />
        </label>
        <label className="field">
          <span>Deep work hours</span>
          <input type="number" step="0.1" min="0" max="16" value={form.deep_work_hours} onChange={set("deep_work_hours")} />
        </label>
      </div>

      <div className="row-2">
        <label className="field">
          <span>Distraction</span>
          <select value={form.distraction_level} onChange={set("distraction_level")}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
        <label className="field">
          <span>Stress level (1–10)</span>
          <input type="number" step="1" min="1" max="10" value={form.stress_level} onChange={set("stress_level")} />
        </label>
      </div>

      <div className="row-2">
        <label className="field">
          <span>Learning hours</span>
          <input type="number" step="0.1" min="0" max="16" value={form.learning_hours} onChange={set("learning_hours")} />
        </label>
        <label className="field">
          <span>Goal deadline (days)</span>
          <input type="number" step="1" min="1" max="365" value={form.goal_deadline_days} onChange={set("goal_deadline_days")} />
        </label>
      </div>

      <div className="row-2">
        <label className="field">
          <span>Simulations</span>
          <input type="number" step="10" min="50" max="400" value={form.n_simulations} onChange={set("n_simulations")} />
        </label>
        <label className="field">
          <span>Horizon (days)</span>
          <input type="number" step="1" min="1" max="180" value={form.horizon_days} onChange={set("horizon_days")} />
        </label>
      </div>

      <button className="primary" disabled={loading} onClick={onSubmit}>
        {loading ? "Simulating…" : "Run simulation"}
      </button>
      <button className="ghost" disabled={loading} onClick={onImpact}>
        Run decision-impact analysis
      </button>
      <p className="muted" style={{ marginTop: 10 }}>
        Runs Monte-Carlo on a deterministic state model. No ML, no external APIs — just math.
      </p>
    </div>
  );
}
