#하루씩 진행하는 시뮬레이터
from dataclasses import dataclass
from typing import Optional, Dict

from game_logic.portfolio import Portfolio
from .scenario_loader import load_scenarios, load_prices_for_scenario
from .models import Scenario, DayPrice
from .order import OrderBook

@dataclass
class GameState:
    scenario: Scenario
    prices: list[DayPrice]
    day_index: int=0

class StockEngine:
    def __init__(self, scenario_ids:list[str]):
        all_scenarios = load_scenarios()
        self.symbol_states: Dict[str, dict] = {}

        KRW_PER_USD = 1460  # 1달러 = 1460원
        
        # 여러 종목 로딩
        for s_id in scenario_ids:
            sc = next((x for x in all_scenarios if x.id == s_id), None)
            if sc is None:
                raise ValueError(f"시나리오 ID '{s_id}'를 찾을 수 없습니다.")

            prices = load_prices_for_scenario(sc)

            if sc.symbol == "005930.KS":
                for p in prices:
                    p.open /= KRW_PER_USD
                    p.high /= KRW_PER_USD
                    p.low  /= KRW_PER_USD
                    p.close /= KRW_PER_USD
                    
                    
            self.symbol_states[sc.symbol] = {
                "scenario": sc,
                "prices": prices,
                "day_index": 0,
            }

        self.order_book = OrderBook()
        self.portfolio = Portfolio()

        # =======================
        # 가격 관련
        # =======================

    def get_today_price(self, symbol: str) -> DayPrice:
        state = self.symbol_states[symbol]
        return state["prices"][state["day_index"]]

        # =======================
        # 날짜 이동
        # =======================

    def next_day(self):
        finished = []

        for symbol, state in self.symbol_states.items():
            if state["day_index"] + 1 >= len(state["prices"]):
                finished.append(symbol)
            else:
                state["day_index"] += 1

        return finished  # 끝난 종목 목록


        # =======================
        # 주문
        # =======================

    def submit_order(self, symbol: str, side: str, quantity: int):
        """주문 제출 (사전에 유효성 검사)"""

        side = side.upper()

        # 심볼 체크
        if symbol not in self.symbol_states:
            raise ValueError(f"알 수 없는 심볼: {symbol}")

        if quantity <= 0:
            raise ValueError("quantity는 1 이상이어야 합니다.")

        today_price = self.get_today_price(symbol)
        close_price = today_price.close

        # 🔹 유효성 검사 (포트폴리오 상태 기준)
        if side == "BUY":
            cost = close_price * quantity
            if cost > self.portfolio.cash:
                # OrderBook에 넣기 전에 바로 에러
                raise ValueError("잔고 부족으로 매수할 수 없습니다.")
        elif side == "SELL":
            h = self.portfolio.holding.get(symbol)
            if h is None:
                raise ValueError("보유하지 않은 종목입니다.")
            if quantity > h.quantity:
                raise ValueError("보유 수량보다 많이 팔 수 없습니다.")
        else:
            raise ValueError("side는 BUY 또는 SELL 이어야 합니다.")

        # 🔹 여기까지 왔다는 건 유효한 주문이란 뜻 → 이제 OrderBook에 넣기
        return self.order_book.create_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            submit_day=self.symbol_states[symbol]["day_index"],
        )

    def process_orders(self):
        """오늘 모든 주문을 '종가'로 체결"""
        open_orders = self.order_book.get_open_orders()

        for o in open_orders:
            symbol = o.symbol
            today_price = self.get_today_price(symbol)
            close_price = today_price.close

            try:
                if o.side == "BUY":
                    self.portfolio.buy(symbol, o.quantity, close_price)
                else:
                    self.portfolio.sell(symbol, o.quantity, close_price)

                o.is_filled = True
                o.filled_price = close_price
                o.filled_day = self.symbol_states[symbol]["day_index"]

            except ValueError as e:
                # 안전 장치: 혹시라도 오류 나면 주문을 '실패 처리'하고 넘김
                print("[WARN] 주문 체결 실패:", e)
                o.is_filled = True
                o.filled_price = None
                o.filled_day = self.symbol_states[symbol]["day_index"]
                # 계속 다음 주문 처리



if __name__ == "__main__":
    engine = StockEngine([
        "tesla_2024_03_14d",
        "google_2024_03_14d",
        "samsung_2024_03_14d",
        "archer_2024_03_14d",
    ])

    # 첫날 가격 출력
    print("=== 첫날 가격들 ===")
    for sym in engine.symbol_states:
        p = engine.get_today_price(sym)
        print(sym, p.close)

    # 여러 종목 매수
    engine.submit_order("TSLA", "BUY", 1)
    engine.submit_order("GOOGL", "BUY", 2)
    engine.submit_order("SAMSUNG", "BUY", 3)
    engine.submit_order("ARCHER", "BUY", 4)

    print("\n=== 주문 처리 ===")
    engine.process_orders()

    print("잔고:", engine.portfolio.cash)
    print("보유:", engine.portfolio.holding)
