from fastapi import FastAPI, Query
from backend.app.schemas import (
    LivePredictResponse,
    MatchPredictResponse,
    PlayerProfileResponse,
    TournamentSimResponse,
)
from backend.app.engine import (
    compute_live_prediction,
    compute_match_prediction,
    compute_player_profile,
    compute_tournament_simulation,
)

app = FastAPI(title="QuantumTerminal Pro T20 Prediction Engine")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/predict/match", response_model=MatchPredictResponse)
def predict_match(
    team_a_id: str = Query(...),
    team_b_id: str = Query(...),
    venue_id: str = Query(...),
    match_time: str = Query(...),
    toss_winner_id: str | None = Query(None),
    toss_decision: str | None = Query(None),
) -> MatchPredictResponse:
    return compute_match_prediction(
        team_a_id=team_a_id,
        team_b_id=team_b_id,
        venue_id=venue_id,
        match_time=match_time,
        toss_winner_id=toss_winner_id,
        toss_decision=toss_decision,
    )


@app.get("/predict/live", response_model=LivePredictResponse)
def predict_live(
    match_id: str = Query(...),
    innings: int = Query(..., ge=1, le=2),
    over: float = Query(..., ge=0.0, le=20.0),
    ball: int = Query(..., ge=0, le=6),
    score: int = Query(..., ge=0),
    wickets: int = Query(..., ge=0, le=10),
    target: int | None = Query(None, ge=0),
) -> LivePredictResponse:
    return compute_live_prediction(
        match_id=match_id,
        innings=innings,
        over=over,
        ball=ball,
        score=score,
        wickets=wickets,
        target=target,
    )


@app.get("/tournament/simulate", response_model=TournamentSimResponse)
def simulate_tournament(
    tournament_id: str = Query(...),
    n_sims: int = Query(10000, ge=100, le=200000),
) -> TournamentSimResponse:
    return compute_tournament_simulation(tournament_id=tournament_id, n_sims=n_sims)


@app.get("/player/{player_id}", response_model=PlayerProfileResponse)
def get_player_profile(player_id: str) -> PlayerProfileResponse:
    return compute_player_profile(player_id=player_id)
