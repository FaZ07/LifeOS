import React from "react";

const fmt = (v) => {
  if (v == null) return "—";
  const n = (v * 100).toFixed(1);
  const sign = v > 0 ? "+" : "";
  return `${sign}${n}%`;
};

export default function DecisionImpact({ data }) {
  if (!data) return null;
  const rows = data.counterfactuals || [];
  return (
    <div className="panel section">
      <h2>Decision impact <span className="pill">counterfactual deltas vs. baseline</span></h2>
      <table className="cf-table">
        <thead>
          <tr>
            <th>Change</th>
            <th>New success</th>
            <th>Δ success</th>
            <th>Δ burnout</th>
            <th>Δ growth</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.change}>
              <td>{r.change}</td>
              <td>{Math.round(r.new_success_probability * 100)}%</td>
              <td className={r.delta_success >= 0 ? "pos" : "neg"}>{fmt(r.delta_success)}</td>
              <td className={r.delta_burnout <= 0 ? "pos" : "neg"}>{fmt(r.delta_burnout)}</td>
              <td className={r.delta_growth >= 0 ? "pos" : "neg"}>{fmt(r.delta_growth)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
