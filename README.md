# LifeOS — Counterfactual Decision Engine

> Deterministic simulation of your life as a dynamical system.
> No ML. No API calls. No black boxes. Just math you can read.

---

## Vision

Most "AI coaches" hand you an opinion from a language model and hope it
sounds wise. LifeOS takes the opposite bet: **model behaviour as a
dynamical system, roll it forward hundreds of times, and let the winning
trajectories tell you the policy.**

You give it one day of inputs. It simulates **120+ possible futures** over
the next 3 weeks, scores each one on success / burnout / growth, and then
extracts the behavioural *pattern* shared by the top 20% of runs. It also
runs a **counterfactual analysis** — "what if I slept +1h?" — to tell you
which single change moves the needle most.

## Why deterministic > black-box AI

| Black-box LLM coach        | LifeOS Decision Engine                 |
| -------------------------- | -------------------------------------- |
| Non-reproducible           | Seeded → bit-identical reproduction    |
| Can't explain its logic    | Every coefficient is in `constants.py` |
| Needs an API key & network | Runs offline, on a laptop CPU          |
| Tunes itself on your data  | You tune it. It never changes silently |
| Hallucinates ranges        | Ranges come from actual winning runs   |

If you don't trust the numbers, open `core/transition_engine.py`. It's
~100 lines of clamped arithmetic.

## Architecture

```
┌──────────────────────── Frontend (React + Vite) ────────────────────────┐
│  InputPanel → /api/simulate → Metrics · TrajectoryChart · Strategy      │
│              /api/decision-impact → counterfactual deltas table         │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │ JSON
┌──────────────────────────────────────▼──────────────────────────────────┐
│                     FastAPI  (backend/api/routes.py)                    │
├─────────────────────────────────────────────────────────────────────────┤
│  core/state_model.py       — LifeState vector (energy, focus, skill,    │
│                               stress, consistency, remaining_time)     │
│  core/transition_engine.py — pure, clamped day-step function           │
│  core/simulation_engine.py — Monte-Carlo ensemble with bounded noise   │
│  core/scoring_engine.py    — success / burnout / growth metrics        │
│  core/policy_extractor.py  — "what did the winners actually do?"       │
│  core/constants.py         — every threshold & weight in one file      │
│  memory/storage.py         — SQLite run history                        │
└─────────────────────────────────────────────────────────────────────────┘
```

## State model

Every day the engine updates a 6-dimensional state:

```
energy        ∈ [0,1]   — function of sleep, stress, workload
focus         ∈ [0,1]   — emergent: energy · (1 - distraction) · (1 - stress_penalty)
skill_level   ∈ [0,1]   — compounds with deep-work · focus · consistency
stress        ∈ [0,1]   — workload + distraction - recovery, blended with self-report
consistency   ∈ [0,1]   — EMA of "productive days"
remaining_time ∈ ℕ      — days until goal deadline
```

## Simulation

For each of N runs (default 120):

1. clone the initial state
2. for each day in the horizon (default 21), apply **bounded uniform noise**
   to sleep / deep-work / distraction / learning / stress
3. step the state through `transition_engine.step(...)`
4. record the trajectory

The master seed controls every child seed → results are 100% reproducible.

## Scoring

```
success  = 0.55·skill_final + 0.25·consistency_final + 0.20·time_component
burnout  = fraction of days with stress≥0.70 AND energy≤0.30 (+ sustained-stress penalty)
growth   = Δ skill_level, normalised
overall  = 0.60·success + 0.40·growth − 0.35·burnout
```

`success_probability` = fraction of runs whose `overall ≥ 0.62`.

## Policy extraction

We take the top 20% of runs by `overall` and report the (mean ± 1σ) range of
each input variable. That's your policy. Not a guess — the distilled signature
of every simulated future that actually worked.

## Counterfactual decision impact

`/api/decision-impact` re-runs the ensemble under each perturbation
(`+1h sleep`, `-1h sleep`, `+1h deep work`, lower distraction, …) and
returns the delta in success / burnout / growth. You instantly see which
single change has leverage for *your* current state.

## Example run

```bash
curl -X POST http://127.0.0.1:8000/api/simulate -H 'content-type: application/json' -d '{
  "sleep_hours": 5.5, "deep_work_hours": 2.0, "distraction_level": "high",
  "stress_level": 7, "learning_hours": 0.5, "goal_deadline_days": 30, "seed": 1
}'
```

Abridged response:

```json
{
  "success_probability": 0.17,
  "burnout_risk": 0.61,
  "growth_score": 0.22,
  "optimal_strategy": [
    "Sleep 6.4–7.1 h (mean 6.8).",
    "Protect 2.1–3.0 h of deep work (mean 2.5).",
    "Allow MEDIUM distraction but no higher."
  ],
  "critical_decisions": [{"day": 5, "risk_ratio": 0.42}, {"day": 12, "risk_ratio": 0.38}]
}
```

## Setup — local

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate     # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --app-dir ..
```

Open http://127.0.0.1:8000/docs for the interactive OpenAPI UI.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. Vite proxies `/api/*` to the FastAPI server.

### Tests

```bash
cd LifeOS
pytest backend/tests
```

## Project layout

```
LifeOS/
├── backend/
│   ├── api/routes.py
│   ├── core/
│   │   ├── constants.py
│   │   ├── state_model.py
│   │   ├── transition_engine.py
│   │   ├── simulation_engine.py
│   │   ├── scoring_engine.py
│   │   └── policy_extractor.py
│   ├── memory/storage.py       # SQLite run history
│   ├── utils/helpers.py
│   ├── tests/test_engine.py
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   ├── components/ (InputPanel, Metrics, TrajectoryChart, Strategy, DecisionImpact)
    │   └── styles.css
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Engineering principles

- Every coefficient lives in one file — `core/constants.py`. No magic numbers
  scattered through the logic.
- `transition_engine.step()` is **pure** — no I/O, no randomness. Noise is a
  separate concern, layered in by the simulator.
- Seeded RNG: two runs with the same `seed` produce byte-identical output.
- Clamp at every boundary. A simulation should never blow up because a
  coefficient nudged a value out of [0, 1].
- Persistence is optional and never allowed to fail a simulation.

## License

MIT.
