"""LifeState: the normalized vector the simulator evolves day by day."""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from typing import Any

from .constants import STATE_MAX, STATE_MIN


def _clamp(value: float, lo: float = STATE_MIN, hi: float = STATE_MAX) -> float:
    """Clamp *value* into [lo, hi]. Used everywhere to keep the state sane."""
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


@dataclass
class LifeState:
    """Normalized snapshot of a user's life at a point in time.

    All fields except ``remaining_time`` live in [0, 1].
    ``remaining_time`` is counted in whole days until the goal deadline.
    """

    energy: float = 0.70
    focus: float = 0.60
    skill_level: float = 0.30
    stress: float = 0.30
    consistency: float = 0.50
    remaining_time: int = 30

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def clamped(self) -> "LifeState":
        """Return a copy with every [0,1] field clamped and time floored at 0."""
        return LifeState(
            energy=_clamp(self.energy),
            focus=_clamp(self.focus),
            skill_level=_clamp(self.skill_level),
            stress=_clamp(self.stress),
            consistency=_clamp(self.consistency),
            remaining_time=max(0, int(self.remaining_time)),
        )

    def clone(self) -> "LifeState":
        return replace(self)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_deadline(cls, goal_deadline_days: int) -> "LifeState":
        """Build a sensible starting state anchored to the user's deadline."""
        return cls(remaining_time=max(1, int(goal_deadline_days)))
