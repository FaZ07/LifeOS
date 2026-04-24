import React from "react";

const pct = (v) => `${Math.round((v ?? 0) * 100)}%`;

const tone = (v, { good = [], warn = [] }) => {
  if (good.length && v >= good[0]) return "good";
  if (warn.length && v >= warn[0]) return "warn";
  return "bad";
};
const toneInv = (v, { good = [], warn = [] }) => {
  if (good.length && v <= good[0]) return "good";
  if (warn.length && v <= warn[0]) return "warn";
  return "bad";
};

const verdict = (p, cases) => {
  for (const [threshold, text] of cases) if (p >= threshold) return text;
  return cases[cases.length - 1][1];
};
const verdictInv = (p, cases) => {
  for (const [threshold, text] of cases) if (p <= threshold) return text;
  return cases[cases.length - 1][1];
};

export default function Metrics({ result }) {
  const s = result.success_probability;
  const b = result.burnout_risk;
  const g = result.growth_score;

  return (
    <div className="metrics">
      <div className="metric">
        <div className="label" title="% of simulated futures that hit the goal">Success probability</div>
        <div className={`value ${tone(s, { good: [0.6], warn: [0.3] })}`}>{pct(s)}</div>
        <div className="metric-note">
          {verdict(s, [
            [0.8, "You're on track — this lifestyle works."],
            [0.6, "Good odds, but thin margin. Protect consistency."],
            [0.3, "Risky. Check the What-if panel below."],
            [0,   "Very unlikely to hit goal. Something needs to change."],
          ])}
        </div>
      </div>

      <div className="metric">
        <div className="label" title="% of days simulated where stress is high AND energy is low">Burnout risk</div>
        <div className={`value ${toneInv(b, { good: [0.15], warn: [0.35] })}`}>{pct(b)}</div>
        <div className="metric-note">
          {verdictInv(b, [
            [0.1, "Sustainable pace. You can keep this up."],
            [0.3, "Watch it — recovery days matter."],
            [0.5, "High. Sleep more or lower workload."],
            [1,   "Severe — this pace breaks you."],
          ])}
        </div>
      </div>

      <div className="metric">
        <div className="label" title="How much your skill level grows over the horizon">Growth score</div>
        <div className={`value ${tone(g, { good: [0.5], warn: [0.2] })}`}>{pct(g)}</div>
        <div className="metric-note">
          {verdict(g, [
            [0.7, "Compounding fast — keep shipping."],
            [0.4, "Solid, steady growth."],
            [0.15, "Slow. More deep-work hours would help."],
            [0,   "Flat — you're maintaining, not improving."],
          ])}
        </div>
      </div>
    </div>
  );
}
