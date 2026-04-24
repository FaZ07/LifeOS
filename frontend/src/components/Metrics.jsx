import React from "react";

const pct = (v) => `${Math.round((v ?? 0) * 100)}%`;

function cls(value, { goodAbove, badAbove } = {}) {
  if (goodAbove !== undefined) return value >= goodAbove ? "good" : value >= goodAbove * 0.6 ? "warn" : "bad";
  if (badAbove !== undefined)  return value <= badAbove  ? "good" : value <= badAbove  * 1.7 ? "warn" : "bad";
  return "";
}

export default function Metrics({ result }) {
  return (
    <div className="metrics">
      <div className="metric">
        <div className="label">Success probability</div>
        <div className={`value ${cls(result.success_probability, { goodAbove: 0.6 })}`}>
          {pct(result.success_probability)}
        </div>
      </div>
      <div className="metric">
        <div className="label">Burnout risk</div>
        <div className={`value ${cls(result.burnout_risk, { badAbove: 0.25 })}`}>
          {pct(result.burnout_risk)}
        </div>
      </div>
      <div className="metric">
        <div className="label">Growth score</div>
        <div className={`value ${cls(result.growth_score, { goodAbove: 0.5 })}`}>
          {pct(result.growth_score)}
        </div>
      </div>
    </div>
  );
}
