"""Deterministic parameters for LifeOS v2 simulation engine.

All thresholds, weights and ranges live here so the behaviour of the
system is transparent, auditable and tunable without touching logic.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# State bounds (every field in LifeState is clamped to [0, 1] except
# remaining_time which is counted in whole days).
# ---------------------------------------------------------------------------
STATE_MIN: float = 0.0
STATE_MAX: float = 1.0

# ---------------------------------------------------------------------------
# Distraction mapping (categorical -> numeric 0..1).
# ---------------------------------------------------------------------------
DISTRACTION_MAP: dict[str, float] = {
    "low": 0.15,
    "medium": 0.40,
    "high": 0.75,
}

# ---------------------------------------------------------------------------
# Energy dynamics (per-day deltas).
# ---------------------------------------------------------------------------
SLEEP_LOW_THRESHOLD: float = 6.0      # hours
SLEEP_HIGH_THRESHOLD: float = 8.0
ENERGY_LOW_SLEEP_PENALTY: float = 0.10
ENERGY_OPTIMAL_GAIN: float = 0.05
ENERGY_OVERSLEEP_GAIN: float = 0.08
ENERGY_STRESS_COEF: float = 0.08      # high stress drains energy
ENERGY_WORK_COST: float = 0.012       # per deep-work hour

# ---------------------------------------------------------------------------
# Stress dynamics.
# ---------------------------------------------------------------------------
STRESS_WORKLOAD_COEF: float = 0.025   # per deep-work hour
STRESS_DISTRACTION_COEF: float = 0.05
STRESS_RECOVERY_SLEEP: float = 0.04   # per hour above threshold
STRESS_BASELINE_DECAY: float = 0.01   # life regresses to calm without input
STRESS_USER_INPUT_WEIGHT: float = 0.5 # blend between internal and reported stress

# ---------------------------------------------------------------------------
# Focus dynamics.
# ---------------------------------------------------------------------------
FOCUS_STRESS_PENALTY: float = 0.35    # focus = energy * (1 - distraction) * (1 - FOCUS_STRESS_PENALTY * stress)

# ---------------------------------------------------------------------------
# Skill growth.
# ---------------------------------------------------------------------------
SKILL_GAIN_COEF: float = 0.020        # base per (deep_work_hour * focus * consistency)
SKILL_LEARNING_COEF: float = 0.008    # passive learning hours contribution
SKILL_DECAY: float = 0.002            # gentle atrophy per idle day

# ---------------------------------------------------------------------------
# Consistency update (exponential moving average).
# ---------------------------------------------------------------------------
CONSISTENCY_ALPHA: float = 0.25
CONSISTENCY_PRODUCTIVE_DW: float = 2.0   # deep-work hours counted as "a productive day"

# ---------------------------------------------------------------------------
# Monte-Carlo simulation.
# ---------------------------------------------------------------------------
DEFAULT_N_SIMULATIONS: int = 120
MIN_N_SIMULATIONS: int = 50
MAX_N_SIMULATIONS: int = 400
DEFAULT_HORIZON_DAYS: int = 21

# Noise bounds applied daily when simulating futures (uniform noise).
NOISE_SLEEP: float = 0.6        # ± hours
NOISE_DEEP_WORK: float = 0.6    # ± hours
NOISE_DISTRACTION: float = 0.08 # ± units (0..1)
NOISE_LEARNING: float = 0.3     # ± hours
NOISE_STRESS_INPUT: float = 0.8 # ± units (1..10 scale)

# ---------------------------------------------------------------------------
# Scoring weights.
# ---------------------------------------------------------------------------
SUCCESS_WEIGHT_SKILL: float = 0.55
SUCCESS_WEIGHT_CONSISTENCY: float = 0.25
SUCCESS_WEIGHT_TIME: float = 0.20

BURNOUT_STRESS_THRESHOLD: float = 0.65
BURNOUT_ENERGY_THRESHOLD: float = 0.35

# A trajectory is considered "successful" if overall_score >= this cutoff.
SUCCESS_CUTOFF: float = 0.62

# ---------------------------------------------------------------------------
# Critical point detection.
# ---------------------------------------------------------------------------
CRITICAL_STRESS: float = 0.70
CRITICAL_ENERGY: float = 0.30

# ---------------------------------------------------------------------------
# Decision-impact analysis: counterfactual perturbations to try.
# ---------------------------------------------------------------------------
COUNTERFACTUALS: list[dict] = [
    {"name": "+1h sleep",        "field": "sleep_hours",     "delta": +1.0},
    {"name": "-1h sleep",        "field": "sleep_hours",     "delta": -1.0},
    {"name": "+1h deep work",    "field": "deep_work_hours", "delta": +1.0},
    {"name": "-1h deep work",    "field": "deep_work_hours", "delta": -1.0},
    {"name": "lower distraction","field": "distraction",     "delta": -0.20},
    {"name": "+1h learning",     "field": "learning_hours",  "delta": +1.0},
]
