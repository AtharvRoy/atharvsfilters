from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Dict

DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class Environment:
    humidity: float
    wind_speed: float
    temperature: float


@dataclass(frozen=True)
class Surface:
    friction: float
    grass_pct: float
    crack_score: float


@dataclass(frozen=True)
class MatchState:
    score: int
    wickets: int
    overs: float
    target: int | None


@dataclass(frozen=True)
class FeatureBundle:
    pressure_index: float
    dew_bias: float
    surface_factor: float
    venue_run_rate: float
    boundary_size: float


def _load_json(name: str) -> Dict:
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_pressure_index(score: int, overs: float, venue_run_rate: float) -> float:
    if overs <= 0:
        return 0.0
    current_rr = score / overs
    return (current_rr - venue_run_rate) / max(venue_run_rate, 0.1)


def compute_dew_bias(humidity: float, chasing: bool) -> float:
    humidity = max(0.0, min(humidity, 1.0))
    return 0.08 * humidity if chasing else 0.0


def compute_surface_factor(surface: Surface) -> float:
    return 0.04 * (1 - surface.friction) + 0.02 * (surface.grass_pct) - 0.03 * surface.crack_score


def build_features(
    *,
    venue_name: str,
    env: Environment,
    surface: Surface,
    match_state: MatchState,
    chasing: bool,
) -> FeatureBundle:
    venue_data = _load_json("venue_baselines.json")
    baseline = venue_data.get(venue_name, venue_data["default"])
    pressure = compute_pressure_index(match_state.score, match_state.overs, baseline["run_rate"])
    dew_bias = compute_dew_bias(env.humidity, chasing)
    surface_factor = compute_surface_factor(surface)
    return FeatureBundle(
        pressure_index=pressure,
        dew_bias=dew_bias,
        surface_factor=surface_factor,
        venue_run_rate=baseline["run_rate"],
        boundary_size=baseline["boundary_size"],
    )
