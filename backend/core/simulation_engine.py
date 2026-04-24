"""Monte-Carlo simulation engine.

Given the user's baseline daily inputs, the engine rolls the state forward
``horizon`` days ``n_sims`` times while applying bounded uniform noise to the
controllable inputs. It returns every trajectory so the scoring/policy layers
can analyse them.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from . import constants as C
from .state_model import LifeState
from .transition_engine import DailyInput, step


@dataclass
class DaySnapshot:
    day: int
    state: LifeState
    inputs: DailyInput


@dataclass
class Trajectory:
    """One full simulated future."""

    seed: int
    snapshots: list[DaySnapshot] = field(default_factory=list)

    @property
    def final_state(self) -> LifeState:
        return self.snapshots[-1].state

    @property
    def initial_state(self) -> LifeState:
        return self.snapshots[0].state


def _perturb(base: DailyInput, rng: random.Random) -> DailyInput:
    """Apply bounded uniform noise to each controllable field."""
    sleep = base.sleep_hours + rng.uniform(-C.NOISE_SLEEP, C.NOISE_SLEEP)
    dw = base.deep_work_hours + rng.uniform(-C.NOISE_DEEP_WORK, C.NOISE_DEEP_WORK)
    dist = base.distraction + rng.uniform(-C.NOISE_DISTRACTION, C.NOISE_DISTRACTION)
    learn = base.learning_hours + rng.uniform(-C.NOISE_LEARNING, C.NOISE_LEARNING)
    stress = base.stress_level + rng.uniform(-C.NOISE_STRESS_INPUT, C.NOISE_STRESS_INPUT)

    return DailyInput(
        sleep_hours=max(0.0, min(24.0, sleep)),
        deep_work_hours=max(0.0, min(16.0, dw)),
        distraction=max(0.0, min(1.0, dist)),
        stress_level=max(1.0, min(10.0, stress)),
        learning_hours=max(0.0, min(16.0, learn)),
    )


def simulate_once(
    initial: LifeState,
    base_day: DailyInput,
    horizon: int,
    seed: int,
    noise: bool = True,
) -> Trajectory:
    """Run a single deterministic-given-seed trajectory."""
    rng = random.Random(seed)
    state = initial.clone()
    snapshots: list[DaySnapshot] = [DaySnapshot(day=0, state=state, inputs=base_day)]

    for day_idx in range(1, horizon + 1):
        day_input = _perturb(base_day, rng) if noise else base_day
        state = step(state, day_input)
        snapshots.append(DaySnapshot(day=day_idx, state=state, inputs=day_input))
        if state.remaining_time == 0:
            break

    return Trajectory(seed=seed, snapshots=snapshots)


def simulate_many(
    initial: LifeState,
    base_day: DailyInput,
    horizon: int = C.DEFAULT_HORIZON_DAYS,
    n_sims: int = C.DEFAULT_N_SIMULATIONS,
    master_seed: Optional[int] = None,
) -> list[Trajectory]:
    """Run a Monte-Carlo ensemble. Deterministic when ``master_seed`` is set."""
    n_sims = max(C.MIN_N_SIMULATIONS, min(C.MAX_N_SIMULATIONS, int(n_sims)))
    horizon = max(1, int(horizon))

    # A master RNG picks child seeds — this keeps full reproducibility.
    master = random.Random(master_seed if master_seed is not None else 0xC0FFEE)
    seeds = [master.randrange(1, 2**31 - 1) for _ in range(n_sims)]

    return [simulate_once(initial, base_day, horizon, seed=s) for s in seeds]
