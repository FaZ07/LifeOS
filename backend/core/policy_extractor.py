"""Extract behavioural policy from the top-performing trajectories.

The idea: the simulator has already ranked thousands of possible futures.
The policy layer looks at the *winners* and reports the shared behavioural
pattern — the one that actually works for this specific user state.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Sequence

from .scoring_engine import TrajectoryScore, score_ensemble
from .simulation_engine import Trajectory


@dataclass
class PolicyReport:
    top_behaviors: list[str]
    recommended_ranges: dict[str, dict[str, float]]
    sample_size: int


def _range(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "max": 0.0, "mean": 0.0}
    mu = mean(values)
    sd = pstdev(values) if len(values) > 1 else 0.0
    return {
        "min": round(max(0.0, mu - sd), 3),
        "max": round(mu + sd, 3),
        "mean": round(mu, 3),
    }


def extract_policy(
    trajectories: Sequence[Trajectory],
    scores: Sequence[TrajectoryScore],
    top_fraction: float = 0.20,
) -> PolicyReport:
    """Look at the top N% of simulations and describe what they did differently."""
    paired = sorted(zip(trajectories, scores), key=lambda p: p[1].overall, reverse=True)
    top_k = max(3, int(len(paired) * top_fraction))
    winners = [t for t, _ in paired[:top_k]]

    sleeps: list[float] = []
    deep_work: list[float] = []
    distraction: list[float] = []
    learning: list[float] = []

    for traj in winners:
        for snap in traj.snapshots[1:]:  # skip day 0
            sleeps.append(snap.inputs.sleep_hours)
            deep_work.append(snap.inputs.deep_work_hours)
            distraction.append(snap.inputs.distraction)
            learning.append(snap.inputs.learning_hours)

    ranges = {
        "sleep_hours": _range(sleeps),
        "deep_work_hours": _range(deep_work),
        "distraction": _range(distraction),
        "learning_hours": _range(learning),
    }

    behaviors = _describe(ranges)

    return PolicyReport(
        top_behaviors=behaviors,
        recommended_ranges=ranges,
        sample_size=top_k,
    )


def _describe(r: dict[str, dict[str, float]]) -> list[str]:
    """Translate the numeric ranges into short, actionable sentences."""
    out: list[str] = []
    s = r["sleep_hours"]
    out.append(f"Sleep {s['min']:.1f}–{s['max']:.1f} h (mean {s['mean']:.1f}).")
    d = r["deep_work_hours"]
    out.append(
        f"Protect {d['min']:.1f}–{d['max']:.1f} h of deep work (mean {d['mean']:.1f})."
    )
    dist = r["distraction"]
    if dist["mean"] < 0.25:
        out.append("Keep distraction LOW — winners stay in flow state.")
    elif dist["mean"] < 0.5:
        out.append("Allow MEDIUM distraction but no higher.")
    else:
        out.append("Unusual: high-distraction trajectories scored well — check inputs.")
    lh = r["learning_hours"]
    out.append(
        f"Supplement with {lh['min']:.1f}–{lh['max']:.1f} h of passive learning."
    )
    return out


def summarize(trajectories: Sequence[Trajectory]) -> PolicyReport:
    """Convenience wrapper when you haven't scored the ensemble yet."""
    ens = score_ensemble(trajectories)
    return extract_policy(trajectories, ens.per_trajectory)
