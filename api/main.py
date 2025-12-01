# api/main.py
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from game_logic.engine import StockEngine
from game_logic.scenario_loader import load_scenarios

app = FastAPI(title="Stock Sim API")

# -----------------------
#  전역 엔진 초기화
# -----------------------
# scenarios.json 에 있는 모든 시나리오를 로딩해서 엔진에 넣는다.
all_scenarios = load_scenarios()
scenario_ids = [s.id for s in all_scenarios]

engine = StockEngine(scenario_ids)


# -----------------------
#  Pydantic 모델
# -----------------------
class OrderRequest(BaseModel):
    symbol: str   # "TSLA", "GOOGL", "005930.KS" 같은 것
    side: str     # "BUY" or "SELL"
    quantity: int


# -----------------------
#  헬퍼 함수
# -----------------------
def build_state() -> Dict[str, Any]:
    """현재 전체 게임 상태를 딕셔너리로 만들어서 반환"""

    symbols_info: Dict[str, Any] = {}
    current_prices: Dict[str, float] = {}

    # 종목별 오늘 가격
    for symbol, state in engine.symbol_states.items():
        today = engine.get_today_price(symbol)
        symbols_info[symbol] = {
            "date": today.date,
            "open": round(today.open, 2),
            "high": round(today.high, 2),
            "low": round(today.low, 2),
            "close": round(today.close, 2),
        }
        current_prices[symbol] = today.close

    # 포트폴리오(잔고 + 보유 종목)
    portfolio = engine.portfolio
    holding_info = {
        sym: {
            "quantity": h.quantity,
            "avg_price": round(h.avg_price, 2),
        }
        for sym, h in portfolio.holding.items()
    }

    total_value = portfolio.evaluate(current_prices)

    return {
        "symbols": symbols_info,
        "portfolio": {
            "cash": round(portfolio.cash, 2),
            "holding": holding_info,
            "total_value": round(total_value, 2),
        },
    }


# -----------------------
#  API 엔드포인트
# -----------------------

@app.get("/scenarios")
def get_scenarios():
    """사용 가능한 시나리오 목록"""
    return [
        {
            "id": s.id,
            "symbol": s.symbol,
            "title": s.title,
            "description": s.description,
        }
        for s in all_scenarios
    ]


@app.get("/state")
def get_state():
    """현재 날짜, 각 종목 가격, 포트폴리오 상태"""
    return build_state()


@app.post("/order")
def submit_order(req: OrderRequest):
    """주문 제출 (여러 종목 가능)"""

    symbol = req.symbol
    side = req.side.upper()
    qty = req.quantity

    # 심볼 검증
    if symbol not in engine.symbol_states:
        raise HTTPException(status_code=400, detail=f"알 수 없는 심볼: {symbol}")

    if side not in ("BUY", "SELL"):
        raise HTTPException(status_code=400, detail="side는 BUY 또는 SELL 이어야 합니다.")

    if qty <= 0:
        raise HTTPException(status_code=400, detail="quantity는 1 이상이어야 합니다.")

    order = engine.submit_order(symbol=symbol, side=side, quantity=qty)

    return {
        "message": "주문이 접수되었습니다.",
        "order": {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "quantity": order.quantity,
            "submit_day": order.submit_day,
        },
    }


@app.post("/end-day")
def end_day():
    """
    오늘 하루를 마감하고,
    미체결 주문들을 모두 오늘 '종가'로 체결
    """
    engine.process_orders()
    return {
        "message": "오늘 주문이 모두 종가로 체결되었습니다.",
        "state": build_state(),
    }


@app.post("/next-day")
def next_day():
    """
    모든 종목을 다음 거래일로 이동
    """
    finished = engine.next_day()
    state = build_state()
    return {
        "message": "다음 날로 이동했습니다.",
        "finished_symbols": finished,  # 더 이상 데이터가 없는 종목 리스트
        "state": state,
    }
