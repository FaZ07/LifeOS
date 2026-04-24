const BASE = import.meta.env.VITE_API_BASE || "/api";

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

export const simulate = (payload) => post("/simulate", payload);
export const decisionImpact = (payload) => post("/decision-impact", payload);
