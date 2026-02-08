from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Tuple
import uuid

import numpy as np

from backend.app.features import Environment, MatchState, Surface, build_features
from backend.app.sde_engine import simulate_remaining


@dataclass(frozen=True)
class MatchContext:
    team_a_id: str
    team_b_id: str
    venue_id: str
    match_time: str
    toss_winner_id: str | None
    toss_decision: str | None


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _phase_from_over(over: float) -> str:
    if over <= 6:
        return "powerplay"
    if over <= 15:
        return "middle"
    return "death"


def _team_strength(team_rating: float, opponent_rating: float) -> float:
    return (team_rating - opponent_rating) / 400.0


def compute_match_prediction(
    *,
    team_a_id: str,
    team_b_id: str,
    venue_id: str,
    match_time: str,
    toss_winner_id: str | None,
    toss_decision: str | None,
) -> Dict:
    context = MatchContext(
        team_a_id=team_a_id,
        team_b_id=team_b_id,
        venue_id=venue_id,
        match_time=match_time,
        toss_winner_id=toss_winner_id,
        toss_decision=toss_decision,
    )
    team_ratings = _load_team_ratings()
    team_a_rating = team_ratings.get(team_a_id, team_ratings["default"])
    team_b_rating = team_ratings.get(team_b_id, team_ratings["default"])
    toss_bias = 0.035 if toss_winner_id == team_a_id and toss_decision == "bat" else 0.0
    strength_delta = _team_strength(team_a_rating, team_b_rating)
    base_prob = _logistic(0.9 * strength_delta + toss_bias)
    match_id = str(uuid.uuid4())
    expected_runs = {
        team_a_id: 165.0 + 14.0 * base_prob,
        team_b_id: 165.0 + 14.0 * (1 - base_prob),
    }
    upset_risk = "medium" if 0.4 < base_prob < 0.65 else "low"
    return {
        "match_id": match_id,
        "win_prob": {team_a_id: base_prob, team_b_id: 1 - base_prob},
        "expected_runs": expected_runs,
        "upset_risk": upset_risk,
        "drivers": ["elo_delta", "toss_bias", "venue_baseline"],
    }


def compute_live_prediction(
    *,
    match_id: str,
    innings: int,
    over: float,
    ball: int,
    score: int,
    wickets: int,
    target: int | None,
) -> Dict:
    phase = _phase_from_over(over)
    remaining_overs = max(0.0, 20.0 - over)
    env = Environment(humidity=0.65, wind_speed=3.0, temperature=28.0)
    surface = Surface(friction=0.72, grass_pct=0.18, crack_score=0.12)
    match_state = MatchState(score=score, wickets=wickets, overs=max(over, 0.1), target=target)
    features = build_features(
        venue_name="default",
        env=env,
        surface=surface,
        match_state=match_state,
        chasing=bool(target),
    )
    drift_adjust = 0.6 * features.pressure_index + 0.8 * features.dew_bias + 0.4 * features.surface_factor
    volatility_adjust = 1.0 + min(0.4, abs(features.pressure_index))
    xR_remaining, xW_remaining = simulate_remaining(
        remaining_overs=remaining_overs,
        wickets_in_hand=max(0, 10 - wickets),
        phase=phase,
        drift_adjust=drift_adjust,
        volatility_adjust=volatility_adjust,
    )
    projected_total = score + xR_remaining
    if target is None:
        win_prob = _logistic((projected_total - 165) / 11.0)
    else:
        win_prob = _logistic((projected_total - target) / 9.5)
    curve = _make_cwp_curve(over, win_prob)
    return {
        "win_prob": float(np.clip(win_prob, 0.01, 0.99)),
        "cwp_curve": curve,
        "xR_remaining": float(round(xR_remaining, 2)),
        "xW_remaining": float(round(xW_remaining, 2)),
    }


def compute_tournament_simulation(*, tournament_id: str, n_sims: int) -> Dict:
    rng = np.random.default_rng(abs(hash(tournament_id)) % (2**32))
    team_ratings = _load_team_ratings()
    teams = ["IND", "AUS", "ENG", "PAK", "NZ", "SA", "WI", "SL"]
    probs = {team: {"super8": 0.0, "semi": 0.0, "final": 0.0, "win": 0.0} for team in teams}

    for _ in range(n_sims):
        qualifiers = _simulate_group_stage(teams, team_ratings, rng)
        semi_winners = _simulate_knockout(qualifiers, team_ratings, rng)
        finalists = semi_winners[:2]
        champion = _simulate_match(finalists[0], finalists[1], team_ratings, rng)

        for team in qualifiers:
            probs[team]["super8"] += 1
        for team in semi_winners:
            probs[team]["semi"] += 1
        for team in finalists:
            probs[team]["final"] += 1
        probs[champion]["win"] += 1

    for team in teams:
        for stage in probs[team]:
            probs[team][stage] = probs[team][stage] / n_sims

    return {"team_probs": probs}


def compute_player_profile(*, player_id: str) -> Dict:
    return {
        "player_id": player_id,
        "name": "Player " + player_id[-4:],
        "xR_delta": 10.6,
        "xW_delta": -0.4,
        "impact_score": 1.12,
    }


def _make_cwp_curve(current_over: float, win_prob: float) -> List[Tuple[float, float]]:
    anchors = [0.0, 5.0, 10.0, 15.0, 20.0]
    curve = []
    for anchor in anchors:
        delta = (anchor - current_over) / 20.0
        curve.append((anchor, float(np.clip(win_prob + delta * 0.04, 0.01, 0.99))))
    return curve


def _simulate_group_stage(teams: List[str], ratings: Dict[str, float], rng: np.random.Generator) -> List[str]:
    standings = {team: 0 for team in teams}
    for i, team in enumerate(teams):
        for opponent in teams[i + 1:]:
            winner = _simulate_match(team, opponent, ratings, rng)
            standings[winner] += 2
    sorted_teams = sorted(standings.keys(), key=lambda t: standings[t], reverse=True)
    return sorted_teams[:4]


def _simulate_knockout(teams: List[str], ratings: Dict[str, float], rng: np.random.Generator) -> List[str]:
    winners = []
    for i in range(0, len(teams), 2):
        winners.append(_simulate_match(teams[i], teams[i + 1], ratings, rng))
    return winners


def _simulate_match(team_a: str, team_b: str, ratings: Dict[str, float], rng: np.random.Generator) -> str:
    strength = _team_strength(ratings.get(team_a, 1750), ratings.get(team_b, 1750))
    win_prob = _logistic(1.1 * strength)
    return team_a if rng.random() < win_prob else team_b


def _load_team_ratings() -> Dict[str, float]:
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parent / "data" / "team_ratings.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
