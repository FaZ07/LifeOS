import React from "react";

function Field({ label, hint, children }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small className="hint">{hint}</small>}
    </label>
  );
}

export default function InputPanel({ form, onChange, onSubmit, onImpact, loading }) {
  const set = (k) => (e) => onChange({ ...form, [k]: e.target.type === "number" ? parseFloat(e.target.value) : e.target.value });

  return (
    <div className="panel">
      <h2>Your typical day</h2>
      <p className="muted" style={{ marginTop: -8, marginBottom: 14, fontSize: 12 }}>
        Be honest — this is the day that gets repeated in every simulation.
      </p>

      <Field label="Sleep hours" hint="How long you usually sleep. Below 6h drains energy; 7–8h is the sweet spot.">
        <input type="number" step="0.1" min="0" max="24" value={form.sleep_hours} onChange={set("sleep_hours")} />
      </Field>

      <Field label="Deep work hours" hint="Focused work with no context-switching. 3–5h/day is elite.">
        <input type="number" step="0.1" min="0" max="16" value={form.deep_work_hours} onChange={set("deep_work_hours")} />
      </Field>

      <Field label="Distraction level" hint="Low = phone away, notifications off. High = social media + constant pings.">
        <select value={form.distraction_level} onChange={set("distraction_level")}>
          <option value="low">Low — in flow</option>
          <option value="medium">Medium — some pings</option>
          <option value="high">High — always on phone</option>
        </select>
      </Field>

      <Field label="Stress level (1–10)" hint="How you actually feel. 1 = calm, 10 = on edge.">
        <input type="number" step="1" min="1" max="10" value={form.stress_level} onChange={set("stress_level")} />
      </Field>

      <Field label="Learning hours" hint="Passive study — reading, courses, tutorials. Supplements deep work.">
        <input type="number" step="0.1" min="0" max="16" value={form.learning_hours} onChange={set("learning_hours")} />
      </Field>

      <Field label="Goal deadline (days)" hint="How many days until your goal? The clock counts down.">
        <input type="number" step="1" min="1" max="365" value={form.goal_deadline_days} onChange={set("goal_deadline_days")} />
      </Field>

      <details style={{ marginTop: 8, marginBottom: 14 }}>
        <summary className="muted" style={{ cursor: "pointer", fontSize: 12 }}>Advanced — simulator knobs</summary>
        <div className="row-2" style={{ marginTop: 10 }}>
          <Field label="Simulations" hint="How many possible futures to roll out. More = smoother stats.">
            <input type="number" step="10" min="50" max="400" value={form.n_simulations} onChange={set("n_simulations")} />
          </Field>
          <Field label="Horizon (days)" hint="How far into the future each run simulates.">
            <input type="number" step="1" min="1" max="180" value={form.horizon_days} onChange={set("horizon_days")} />
          </Field>
        </div>
      </details>

      <button className="primary" disabled={loading} onClick={onSubmit}>
        {loading ? "Simulating…" : "▶  Run simulation"}
      </button>
      <button className="ghost" disabled={loading} onClick={onImpact}>
        🧪  What-if analysis (try +1h sleep, –1h work, etc.)
      </button>
      <p className="muted" style={{ marginTop: 10, fontSize: 11, lineHeight: 1.5 }}>
        Pure math — no AI, no data sent anywhere. Every coefficient is in
        <code style={{ color: "var(--accent)" }}> constants.py</code>.
      </p>
    </div>
  );
}
