from fastapi import FastAPI
from pydantic import BaseModel

from game_logic.game_controller import GameController

app = FastAPI()
# 전역 게임 컨트롤러 (게임 한 판을 유지하기 위해,일단은 한개)
controller = GameController("tesla_2024_03_14d")

class OrderRequest(BaseModel):
    side: str
    quantity: int

@app.get("/state")
def get_state():
    """현재 날짜, 가격, 포트폴리오 조회"""
    return controller.get_state()

@app.post("/order")
def make_order(req: OrderRequest):
    """주문 제출"""
    order = controller.submit_order(req.side, req.quantity)
    return {
        "message": "주문 접수됨",
        "order": order.__dict__
    }

@app.post("/end-day")
def end_day():
    """하루 종료 → 주문 체결"""
    controller.end_day()
    return {"message": "오늘 주문 모두 체결됨"}


@app.post("/next-day")
def next_day():
    """다음날로 이동"""
    result = controller.next_day()
    if result is None:
        return {"message": "마지막 날입니다. 더 이동할 수 없음"}

    return {"message": "다음 날로 이동했습니다.", "date": result.date}