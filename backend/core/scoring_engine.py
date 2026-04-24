"""Turn a population of trajectories into metrics.

Every metric is a pure function of the trajectory ensemble — easy to test,
easy to reason about, and completely free of black-box ML.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from . import constants as C
from .simulation_engine import Trajectory


@dataclass
class TrajectoryScore:
    """Per-trajectory breakdown. Kept around for downstream analysis."""

    success: float
    burnout: float
    growth: float
    overall: float
    critical_days: list[int]


def _success_score(traj: Trajectory) -> float:
    final = traj.final_state
    total_days = max(1, len(traj.snapshots) - 1)
    time_used_ratio = 1.0 - (final.remaining_time / max(1, traj.initial_state.remaining_time))
    # reward finishing with slack on the clock (time_remaining > 0 is good)
    time_component = final.remaining_time / max(1, traj.initial_state.remaining_time)

    return (
        C.SUCCESS_WEIGHT_SKILL * final.skill_level
        + C.SUCCESS_WEIGHT_CONSISTENCY * final.consistency
        + C.SUCCESS_WEIGHT_TIME * (0.5 * time_component + 0.5 * min(1.0, time_used_ratio * 1.2))
    )


def _burnout_score(traj: Trajectory) -> tuple[float, list[int]]:
    """Burnout = sustained high-stress / low-energy co-occurrence."""
    hits = 0
    critical_days: list[int] = []
    snaps = traj.snapshots[1:]  # skip day 0 (initial)
    for snap in snaps:
        st = snap.state
        if st.stress >= C.CRITICAL_STRESS and st.energy <= C.CRITICAL_ENERGY:
            hits += 1
            critical_days.append(snap.day)
    score = hits / max(1, len(snaps))

    # Soft penalty for running hot on stress even without low energy.
    avg_stress = sum(s.state.stress for s in snaps) / max(1, len(snaps))
    score = min(1.0, score + max(0.0, avg_stress - C.BURNOUT_STRESS_THRESHOLD) * 0.5)
    return score, critical_days


def _growth_score(traj: Trajectory) -> float:
    delta = traj.final_state.skill_level - traj.initial_state.skill_level
    # Map realistic per-horizon delta (~0 .. 0.6) into [0,1].
    return max(0.0, min(1.0, delta / 0.6))


def score_trajectory(traj: Trajectory) -> TrajectoryScore:
    success = _success_score(traj)
    burnout, critical_days = _burnout_score(traj)
    growth = _growth_score(traj)
    overall = max(0.0, min(1.0, 0.6 * success + 0.4 * growth - 0.35 * burnout))
    return TrajectoryScore(
        success=success,
        burnout=burnout,
        growth=growth,
        overall=overall,
        critical_days=critical_days,
    )


@dataclass
class EnsembleScore:
    success_probability: float   # fraction of runs whose overall >= SUCCESS_CUTOFF
    burnout_risk: float          # mean burnout score
    growth_score: float          # mean growth
    mean_overall: float
    per_trajectory: list[TrajectoryScore]


def score_ensemble(trajectories: Sequence[Trajectory]) -> EnsembleScore:
    per = [score_trajectory(t) for t in trajectories]
    n = max(1, len(per))
    successes = sum(1 for p in per if p.overall >= C.SUCCESS_CUTOFF)
    return EnsembleScore(
        success_probability=successes / n,
        burnout_risk=sum(p.burnout for p in per) / n,
        growth_score=sum(p.growth for p in per) / n,
        mean_overall=sum(p.overall for p in per) / n,
        per_trajectory=per,
    )
