# QuantumTerminal Pro T20 Prediction Engine (MVP)

## Overview
A Python-first, mobile-ready prediction service for the ICC Men’s T20 World Cup 2026.
This repo ships a FastAPI backend with SDE-inspired modeling, seeded simulations,
relational schema scaffolding, and analytics-friendly endpoints.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

## Core endpoints
- `GET /predict/match`
- `GET /predict/live`
- `GET /tournament/simulate`
- `GET /player/{id}`

## Model stack (MVP)
- **Phase-based SDE** with correlated noise for runs/wickets (`backend/app/sde_engine.py`).
- **Feature fusion** for pressure, dew, and surface factors (`backend/app/features.py`).
- **Tournament simulation** using rating-based Monte Carlo.

## Notes
- This is an MVP scaffold that prioritizes deterministic, testable outputs.
- Replace the stubbed ratings/venue baselines in `backend/app/data/` with live data.
