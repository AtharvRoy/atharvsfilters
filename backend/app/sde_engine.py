from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Tuple
import numpy as np


@dataclass(frozen=True)
class SDEPhaseParams:
    mu_runs: float
    sigma_runs: float
    mu_wkts: float
    sigma_wkts: float


def phase_params(phase: str) -> SDEPhaseParams:
    if phase == "powerplay":
        return SDEPhaseParams(mu_runs=9.4, sigma_runs=2.6, mu_wkts=0.38, sigma_wkts=0.2)
    if phase == "death":
        return SDEPhaseParams(mu_runs=10.8, sigma_runs=3.4, mu_wkts=0.5, sigma_wkts=0.28)
    return SDEPhaseParams(mu_runs=7.8, sigma_runs=1.7, mu_wkts=0.28, sigma_wkts=0.14)


def simulate_remaining(
    *,
    remaining_overs: float,
    wickets_in_hand: int,
    phase: str,
    drift_adjust: float,
    volatility_adjust: float,
    rho: float = 0.35,
    n_paths: int = 4000,
) -> Tuple[float, float]:
    params = phase_params(phase)
    dt = 0.1
    steps = max(1, int(math.ceil(remaining_overs / dt)))
    rng = np.random.default_rng(2026)
    runs = np.zeros(n_paths)
    wkts = np.zeros(n_paths)
    cov = np.array([[1.0, rho], [rho, 1.0]])
    chol = np.linalg.cholesky(cov)

    for _ in range(steps):
        z = rng.standard_normal((n_paths, 2)) @ chol.T
        d_runs = (params.mu_runs + drift_adjust) * dt + (params.sigma_runs * volatility_adjust) * math.sqrt(dt) * z[:, 0]
        d_wkts = (params.mu_wkts + 0.02 * drift_adjust) * dt + (params.sigma_wkts * volatility_adjust) * math.sqrt(dt) * z[:, 1]
        runs += d_runs
        wkts += np.clip(d_wkts, 0, None)

    runs = np.clip(runs, 0, None)
    wkts = np.clip(wkts, 0, wickets_in_hand)
    return float(np.mean(runs)), float(np.mean(wkts))
