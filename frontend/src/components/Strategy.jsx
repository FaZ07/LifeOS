import React from "react";

export default function Strategy({ result }) {
  const r = result.recommended_ranges || {};
  return (
    <div className="panel section">
      <h2>Optimal strategy <span className="pill">from top {result.meta?.policy_sample_size} runs</span></h2>
      <ul className="clean">
        {(result.optimal_strategy || []).map((s, i) => <li key={i}>{s}</li>)}
      </ul>

      <div className="section">
        <h2>Recommended ranges</h2>
        <table className="cf-table">
          <thead>
            <tr><th>Field</th><th>Min</th><th>Mean</th><th>Max</th></tr>
          </thead>
          <tbody>
            {Object.entries(r).map(([k, v]) => (
              <tr key={k}>
                <td>{k.replace(/_/g, " ")}</td>
                <td>{v.min}</td>
                <td>{v.mean}</td>
                <td>{v.max}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {result.critical_decisions?.length > 0 && (
        <div className="section">
          <h2>Critical decision days</h2>
          <ul className="clean">
            {result.critical_decisions.map((c) => (
              <li key={c.day}>
                Day {c.day}: {Math.round(c.risk_ratio * 100)}% of simulations hit burnout threshold.
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
