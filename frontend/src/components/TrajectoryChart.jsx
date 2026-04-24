import React, { useMemo, useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
} from "recharts";

const FIELDS = [
  { key: "skill_level", color: "#5eead4", label: "Skill" },
  { key: "energy",      color: "#7ee787", label: "Energy" },
  { key: "focus",       color: "#8bb4ff", label: "Focus" },
  { key: "stress",      color: "#f97068", label: "Stress" },
  { key: "consistency", color: "#f5b067", label: "Consistency" },
];

export default function TrajectoryChart({ timelines }) {
  const [scenario, setScenario] = useState("best_case");
  const data = useMemo(() => timelines?.[scenario] ?? [], [timelines, scenario]);

  if (!data.length) return <div className="empty">No trajectory yet — run a simulation.</div>;

  return (
    <>
      <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
        {["best_case", "average_case", "worst_case"].map((key) => (
          <button
            key={key}
            className={scenario === key ? "primary" : "ghost"}
            style={{ width: "auto", padding: "6px 12px", marginTop: 0, fontSize: 12 }}
            onClick={() => setScenario(key)}
          >
            {key.replace("_case", "").toUpperCase()}
          </button>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: -10 }}>
          <CartesianGrid stroke="#242c36" strokeDasharray="3 3" />
          <XAxis dataKey="day" stroke="#8b98a5" fontSize={11} />
          <YAxis domain={[0, 1]} stroke="#8b98a5" fontSize={11} />
          <Tooltip
            contentStyle={{ background: "#14181d", border: "1px solid #242c36", borderRadius: 8 }}
            labelStyle={{ color: "#8b98a5" }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {FIELDS.map((f) => (
            <Line
              key={f.key}
              type="monotone"
              dataKey={f.key}
              stroke={f.color}
              strokeWidth={2}
              dot={false}
              name={f.label}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </>
  );
}
