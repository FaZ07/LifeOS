"""Small helpers shared across layers."""
from __future__ import annotations

from typing import Any

from ..core.simulation_engine import Trajectory


def trajectory_to_series(traj: Trajectory) -> list[dict[str, Any]]:
    """Convert a trajectory into a JSON-serialisable time series for the UI."""
    return [
        {
            "day": snap.day,
            "energy": round(snap.state.energy, 4),
            "focus": round(snap.state.focus, 4),
            "skill_level": round(snap.state.skill_level, 4),
            "stress": round(snap.state.stress, 4),
            "consistency": round(snap.state.consistency, 4),
            "remaining_time": snap.state.remaining_time,
            "inputs": {
                "sleep_hours": round(snap.inputs.sleep_hours, 2),
                "deep_work_hours": round(snap.inputs.deep_work_hours, 2),
                "distraction": round(snap.inputs.distraction, 2),
                "stress_level": round(snap.inputs.stress_level, 2),
                "learning_hours": round(snap.inputs.learning_hours, 2),
            },
        }
        for snap in traj.snapshots
    ]


def representative_trajectories(
    trajectories: list[Trajectory],
    overall_scores: list[float],
) -> dict[str, Trajectory]:
    """Pick best, worst and median trajectories for display."""
    assert len(trajectories) == len(overall_scores) and trajectories
    paired = sorted(zip(overall_scores, range(len(trajectories))))
    worst_idx = paired[0][1]
    best_idx = paired[-1][1]
    median_idx = paired[len(paired) // 2][1]
    return {
        "best_case": trajectories[best_idx],
        "average_case": trajectories[median_idx],
        "worst_case": trajectories[worst_idx],
    }
