"""FastAPI routes for LifeOS."""
from __future__ import annotations

from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..core import constants as C
from ..core.policy_extractor import extract_policy
from ..core.scoring_engine import score_ensemble
from ..core.simulation_engine import simulate_many, simulate_once
from ..core.state_model import LifeState
from ..core.transition_engine import DailyInput
from ..memory import storage
from ..utils.helpers import representative_trajectories, trajectory_to_series

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class SimulateRequest(BaseModel):
    sleep_hours: float = Field(..., ge=0, le=24)
    deep_work_hours: float = Field(..., ge=0, le=16)
    distraction_level: Literal["low", "medium", "high"] = "medium"
    stress_level: float = Field(..., ge=1, le=10)
    learning_hours: float = Field(..., ge=0, le=16)
    goal_deadline_days: int = Field(..., ge=1, le=365)

    horizon_days: Optional[int] = Field(default=None, ge=1, le=180)
    n_simulations: Optional[int] = Field(default=None, ge=C.MIN_N_SIMULATIONS, le=C.MAX_N_SIMULATIONS)
    seed: Optional[int] = Field(default=None, ge=0)

    # Optional overrides of the initial state — otherwise defaults are used.
    initial_energy: Optional[float] = Field(default=None, ge=0, le=1)
    initial_focus: Optional[float] = Field(default=None, ge=0, le=1)
    initial_skill: Optional[float] = Field(default=None, ge=0, le=1)
    initial_stress: Optional[float] = Field(default=None, ge=0, le=1)
    initial_consistency: Optional[float] = Field(default=None, ge=0, le=1)


def _build_initial_state(req: SimulateRequest) -> LifeState:
    base = LifeState.from_deadline(req.goal_deadline_days)
    if req.initial_energy is not None: base.energy = req.initial_energy
    if req.initial_focus is not None: base.focus = req.initial_focus
    if req.initial_skill is not None: base.skill_level = req.initial_skill
    if req.initial_stress is not None: base.stress = req.initial_stress
    if req.initial_consistency is not None: base.consistency = req.initial_consistency
    return base.clamped()


def _run_engine(req: SimulateRequest) -> dict[str, Any]:
    """Shared pipeline used by /simulate and /decision-impact."""
    try:
        base_day = DailyInput.from_user(
            sleep_hours=req.sleep_hours,
            deep_work_hours=req.deep_work_hours,
            distraction_level=req.distraction_level,
            stress_level=req.stress_level,
            learning_hours=req.learning_hours,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    initial = _build_initial_state(req)
    horizon = min(req.horizon_days or C.DEFAULT_HORIZON_DAYS, req.goal_deadline_days)
    n_sims = req.n_simulations or C.DEFAULT_N_SIMULATIONS

    trajectories = simulate_many(
        initial=initial,
        base_day=base_day,
        horizon=horizon,
        n_sims=n_sims,
        master_seed=req.seed,
    )
    ensemble = score_ensemble(trajectories)
    policy = extract_policy(trajectories, ensemble.per_trajectory)

    overall = [p.overall for p in ensemble.per_trajectory]
    reps = representative_trajectories(trajectories, overall)

    # Aggregate critical days across ensemble
    critical_hits: dict[int, int] = {}
    for ts in ensemble.per_trajectory:
        for d in ts.critical_days:
            critical_hits[d] = critical_hits.get(d, 0) + 1
    critical_decisions = [
        {"day": day, "risk_count": count, "risk_ratio": round(count / len(trajectories), 3)}
        for day, count in sorted(critical_hits.items())
        if count / len(trajectories) >= 0.20
    ]

    return {
        "success_probability": round(ensemble.success_probability, 4),
        "burnout_risk": round(ensemble.burnout_risk, 4),
        "growth_score": round(ensemble.growth_score, 4),
        "mean_overall": round(ensemble.mean_overall, 4),
        "optimal_strategy": policy.top_behaviors,
        "recommended_ranges": policy.recommended_ranges,
        "critical_decisions": critical_decisions,
        "sample_timelines": {
            "best_case": trajectory_to_series(reps["best_case"]),
            "average_case": trajectory_to_series(reps["average_case"]),
            "worst_case": trajectory_to_series(reps["worst_case"]),
        },
        "meta": {
            "horizon_days": horizon,
            "n_simulations": len(trajectories),
            "success_cutoff": C.SUCCESS_CUTOFF,
            "policy_sample_size": policy.sample_size,
        },
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "LifeOS"}


@router.post("/simulate")
def simulate(req: SimulateRequest) -> dict[str, Any]:
    result = _run_engine(req)
    try:
        run_id = storage.save_run(req.model_dump(), result)
        result["run_id"] = run_id
    except Exception:
        # Persistence must never break a successful simulation.
        result["run_id"] = None
    return result


class DecisionImpactRequest(SimulateRequest):
    """Same as SimulateRequest — we counterfactually perturb each input."""


@router.post("/decision-impact")
def decision_impact(req: DecisionImpactRequest) -> dict[str, Any]:
    """For each counterfactual (e.g. +1h sleep) compute the delta in success_probability."""
    baseline = _run_engine(req)
    baseline_prob = baseline["success_probability"]

    deltas = []
    for cf in C.COUNTERFACTUALS:
        perturbed = req.model_copy()
        field = cf["field"]
        delta = cf["delta"]

        if field == "distraction":
            ladder = ["low", "medium", "high"]
            idx = ladder.index(perturbed.distraction_level)
            new_idx = max(0, min(len(ladder) - 1, idx - 1 if delta < 0 else idx + 1))
            perturbed.distraction_level = ladder[new_idx]  # type: ignore[assignment]
        else:
            current = getattr(perturbed, field)
            setattr(perturbed, field, max(0.0, current + delta))

        try:
            out = _run_engine(perturbed)
            deltas.append({
                "change": cf["name"],
                "new_success_probability": out["success_probability"],
                "delta_success": round(out["success_probability"] - baseline_prob, 4),
                "delta_burnout": round(out["burnout_risk"] - baseline["burnout_risk"], 4),
                "delta_growth": round(out["growth_score"] - baseline["growth_score"], 4),
            })
        except HTTPException:
            continue

    deltas.sort(key=lambda d: d["delta_success"], reverse=True)
    return {"baseline": baseline, "counterfactuals": deltas}


@router.get("/history")
def history(limit: int = 25) -> dict[str, Any]:
    return {"runs": storage.list_runs(limit=limit)}


@router.get("/runs/{run_id}")
def get_run(run_id: int) -> dict[str, Any]:
    run = storage.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run
