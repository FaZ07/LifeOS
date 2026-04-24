"""Deterministic transition functions.

Given a ``LifeState`` and a ``DailyInput`` the engine returns the next
``LifeState``. The functions are intentionally pure — no randomness, no I/O —
so the simulation engine can layer controlled noise on top and still reproduce
any individual trajectory.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from . import constants as C
from .state_model import LifeState, _clamp


@dataclass
class DailyInput:
    """One day's observed / proposed behaviour."""

    sleep_hours: float
    deep_work_hours: float
    distraction: float           # already numeric 0..1
    stress_level: float          # 1..10 scale as reported by the user
    learning_hours: float

    @classmethod
    def from_user(
        cls,
        sleep_hours: float,
        deep_work_hours: float,
        distraction_level: Union[str, float],
        stress_level: float,
        learning_hours: float,
    ) -> "DailyInput":
        """Normalize raw user-provided values into a ``DailyInput``."""
        if isinstance(distraction_level, str):
            key = distraction_level.strip().lower()
            if key not in C.DISTRACTION_MAP:
                raise ValueError(
                    f"distraction_level must be one of {list(C.DISTRACTION_MAP)}"
                )
            distraction = C.DISTRACTION_MAP[key]
        else:
            distraction = float(distraction_level)
            if not 0.0 <= distraction <= 1.0:
                raise ValueError("numeric distraction_level must be in [0, 1]")

        if not 0.0 <= float(sleep_hours) <= 24.0:
            raise ValueError("sleep_hours must be within [0, 24]")
        if not 0.0 <= float(deep_work_hours) <= 16.0:
            raise ValueError("deep_work_hours must be within [0, 16]")
        if not 1.0 <= float(stress_level) <= 10.0:
            raise ValueError("stress_level must be within [1, 10]")
        if not 0.0 <= float(learning_hours) <= 16.0:
            raise ValueError("learning_hours must be within [0, 16]")

        return cls(
            sleep_hours=float(sleep_hours),
            deep_work_hours=float(deep_work_hours),
            distraction=distraction,
            stress_level=float(stress_level),
            learning_hours=float(learning_hours),
        )


# ---------------------------------------------------------------------------
# Individual transition components (kept small and auditable).
# ---------------------------------------------------------------------------
def _energy_delta(state: LifeState, day: DailyInput) -> float:
    """Energy responds to sleep, stress and work volume."""
    if day.sleep_hours < C.SLEEP_LOW_THRESHOLD:
        sleep_term = -C.ENERGY_LOW_SLEEP_PENALTY
    elif day.sleep_hours <= C.SLEEP_HIGH_THRESHOLD:
        sleep_term = +C.ENERGY_OPTIMAL_GAIN
    else:
        sleep_term = +C.ENERGY_OVERSLEEP_GAIN

    stress_term = -C.ENERGY_STRESS_COEF * state.stress
    work_term = -C.ENERGY_WORK_COST * day.deep_work_hours
    return sleep_term + stress_term + work_term


def _stress_delta(state: LifeState, day: DailyInput) -> float:
    """Stress rises with workload/distractions and falls with recovery."""
    workload = C.STRESS_WORKLOAD_COEF * day.deep_work_hours
    distractions = C.STRESS_DISTRACTION_COEF * day.distraction
    recovery = C.STRESS_RECOVERY_SLEEP * max(0.0, day.sleep_hours - C.SLEEP_LOW_THRESHOLD)

    reported = (day.stress_level - 1.0) / 9.0  # -> [0,1]
    internal_delta = workload + distractions - recovery - C.STRESS_BASELINE_DECAY

    # Blend the model's own dynamics with what the user reports today.
    target = _clamp(state.stress + internal_delta)
    blended = (
        (1.0 - C.STRESS_USER_INPUT_WEIGHT) * target
        + C.STRESS_USER_INPUT_WEIGHT * reported
    )
    return blended - state.stress


def _focus_value(next_energy: float, next_stress: float, day: DailyInput) -> float:
    """Focus is an emergent quantity, not accumulated, so we recompute it."""
    base = next_energy * (1.0 - day.distraction)
    penalty = 1.0 - C.FOCUS_STRESS_PENALTY * next_stress
    return _clamp(base * penalty)


def _consistency_update(state: LifeState, day: DailyInput) -> float:
    """EMA over a boolean ``was_productive`` signal."""
    productive = 1.0 if day.deep_work_hours >= C.CONSISTENCY_PRODUCTIVE_DW else 0.0
    return (
        (1.0 - C.CONSISTENCY_ALPHA) * state.consistency
        + C.CONSISTENCY_ALPHA * productive
    )


def _skill_delta(state: LifeState, day: DailyInput, next_focus: float) -> float:
    """Skill compounds with focused deep-work and decays gently when idle."""
    gain = (
        C.SKILL_GAIN_COEF
        * day.deep_work_hours
        * next_focus
        * (0.5 + 0.5 * state.consistency)
    )
    passive = C.SKILL_LEARNING_COEF * day.learning_hours * next_focus
    decay = C.SKILL_DECAY if (day.deep_work_hours + day.learning_hours) < 0.5 else 0.0
    return gain + passive - decay


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def step(state: LifeState, day: DailyInput) -> LifeState:
    """Advance the state by one day and return the new, clamped state."""
    next_stress = _clamp(state.stress + _stress_delta(state, day))
    next_energy = _clamp(state.energy + _energy_delta(state, day))
    next_focus = _focus_value(next_energy, next_stress, day)
    next_consistency = _clamp(_consistency_update(state, day))
    next_skill = _clamp(state.skill_level + _skill_delta(state, day, next_focus))

    nxt = LifeState(
        energy=next_energy,
        focus=next_focus,
        skill_level=next_skill,
        stress=next_stress,
        consistency=next_consistency,
        remaining_time=max(0, state.remaining_time - 1),
    )
    return nxt.clamped()
