from typing import Dict, List, Tuple
from pydantic import BaseModel


class MatchPredictResponse(BaseModel):
    match_id: str
    win_prob: Dict[str, float]
    expected_runs: Dict[str, float]
    upset_risk: str
    drivers: List[str]


class LivePredictResponse(BaseModel):
    win_prob: float
    cwp_curve: List[Tuple[float, float]]
    xR_remaining: float
    xW_remaining: float


class TournamentSimResponse(BaseModel):
    team_probs: Dict[str, Dict[str, float]]


class PlayerProfileResponse(BaseModel):
    player_id: str
    name: str
    xR_delta: float
    xW_delta: float
    impact_score: float
