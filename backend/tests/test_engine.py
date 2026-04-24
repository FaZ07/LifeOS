"""Sanity tests for the deterministic engine. Run with `pytest`."""
from __future__ import annotations

from backend.core.scoring_engine import score_ensemble
from backend.core.simulation_engine import simulate_many, simulate_once
from backend.core.state_model import LifeState
from backend.core.transition_engine import DailyInput, step


def _good_day() -> DailyInput:
    return DailyInput.from_user(
        sleep_hours=7.5, deep_work_hours=4.0,
        distraction_level="low", stress_level=3.0, learning_hours=1.0,
    )


def _bad_day() -> DailyInput:
    return DailyInput.from_user(
        sleep_hours=4.0, deep_work_hours=0.5,
        distraction_level="high", stress_level=9.0, learning_hours=0.0,
    )


def test_state_clamped():
    s = LifeState(energy=2.0, stress=-1.0, skill_level=1.5,
                  focus=0.4, consistency=0.3, remaining_time=10)
    c = s.clamped()
    assert 0 <= c.energy <= 1 and 0 <= c.stress <= 1 and 0 <= c.skill_level <= 1


def test_good_day_improves_skill_over_time():
    state = LifeState.from_deadline(21)
    for _ in range(21):
        state = step(state, _good_day())
    assert state.skill_level > 0.4
    assert state.stress < 0.6


def test_bad_day_burns_out():
    state = LifeState.from_deadline(21)
    for _ in range(21):
        state = step(state, _bad_day())
    assert state.stress > 0.5
    assert state.energy < 0.6


def test_monte_carlo_deterministic_with_seed():
    init = LifeState.from_deadline(21)
    a = simulate_many(init, _good_day(), horizon=21, n_sims=50, master_seed=42)
    b = simulate_many(init, _good_day(), horizon=21, n_sims=50, master_seed=42)
    assert [t.final_state.skill_level for t in a] == [t.final_state.skill_level for t in b]


def test_good_beats_bad_in_ensemble():
    init = LifeState.from_deadline(21)
    good = score_ensemble(simulate_many(init, _good_day(), horizon=21, n_sims=80, master_seed=1))
    bad = score_ensemble(simulate_many(init, _bad_day(), horizon=21, n_sims=80, master_seed=1))
    assert good.success_probability > bad.success_probability
    assert good.burnout_risk < bad.burnout_risk
    assert good.growth_score > bad.growth_score
