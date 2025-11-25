# back_end/app.py
from dataclasses import asdict, is_dataclass
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 내부 모듈
from game_logic.scenario_loader import (
    load_scenarios,
    get_scenario,
    load_price_slice,
)
from game_logic.portfolio import (
    new_session,
    get_session,
    SESSIONS,
)


app = FastAPI(title="Stock Sim API", version="0.1.0")

# 프론트(Dash)에서 호출 편하게 CORS 열어둠(배포 시 allow_origins는 제한 권장)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def to_dict(obj: Any):
    """dataclass/Pydantic/일반객체를 dict로 통일"""
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "model_dump"):      # Pydantic v2
        return obj.model_dump()
    if hasattr(obj, "dict"):            # Pydantic v1
        return obj.dict()
    return obj

# -------------------------------
# Scenarios
# -------------------------------
@app.get("/scenarios")
def list_scenarios():
    items = load_scenarios()
    return [to_dict(s) for s in items]


@app.get("/scenarios/{scenario_id}")
def scenario_detail(scenario_id: str):
    try:
        s = get_scenario(scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return to_dict(s)


@app.get("/scenarios/{scenario_id}/prices")
def scenario_prices(scenario_id: str):
    try:
        days = load_price_slice(scenario_id)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    return [to_dict(d) for d in days]


# -------------------------------
# Session (시나리오 기반)
# -------------------------------
class InitSessionReq(BaseModel):
    session_id: str
    scenario_id: str
    initial_cash: float = 100_000.0


@app.post("/session/init")
def session_init(req: InitSessionReq):
    try:
        sess = new_session(
            session_id=req.session_id,
            scenario_id=req.scenario_id,
            initial_cash=req.initial_cash,
        )
        d0 = sess.current_day()
        return {
            "session_id": sess.session_id,
            "scenario_id": sess.scenario_id,
            "date": d0.date,
            "cash": round(sess.cash, 2),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state(session_id: str):
    try:
        s = get_session(session_id)
        d = s.current_day()
        return {
            "session_id": s.session_id,
            "scenario_id": s.scenario_id,
            "index": s.idx,
            "date": d.date,
            "cash": round(s.cash, 2),
            "positions": {k: to_dict(v) for k, v in s.positions.items()},
            "pnl_realized": round(s.pnl_realized, 2),
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/step")
def step(session_id: str):
    try:
        s = get_session(session_id)
        s.step()
        return {"date": s.current_day().date, "index": s.idx}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
