#하루씩 진행하는 시뮬레이터
from dataclasses import dataclass
from typing import Optional

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
    def __init__(self, scenario_id:str):
        self.scenario = self._find_scenario_by_id(scenario_id)
        self.prices = load_prices_for_scenario(self.scenario)
        self.state = GameState(self.scenario, self.prices)
        self.order_book = OrderBook()
        self.portfolio = Portfolio()

    def _find_scenario_by_id(self, scenario_id: str) -> Scenario:
        for s in load_scenarios():
            if s.id == scenario_id:
                return s
        raise ValueError(f"시나리오 ID '{scenario_id}'를 찾을 수 없습니다.")

    def get_today_price(self) -> DayPrice:
        return self.state.prices[self.state.day_index]

    def next_day(self) -> Optional[DayPrice]:
        """다음 날짜로 이동하고 가격 반환. 마지막 날이면 None."""
        if self.state.day_index + 1 >= len(self.state.prices):
            return None
        self.state.day_index += 1
        return self.get_today_price()
    def submit_order(self, symbol: str, side: str, quantity: int):
        """주문 제출"""
        return self.order_book.create_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            submit_day = self.state.day_index,

        )

    def process_orders(self):
        """오늘은 끝나는 금액으로 모든 주문 자동 체결"""
        today = self.get_today_price()
        close_price = today.close

        open_orders = self.order_book.get_open_orders()

        for o in open_orders:
            # 매수/매도 실행
            if o.side == "BUY":
                self.portfolio.buy(o.symbol, o.quantity, close_price)
            else:
                self.portfolio.sell(o.symbol, o.quantity, close_price)

            # 주문 완료 처리
            o.is_filled = True
            o.filled_price = close_price
            o.filled_day = self.state.day_index

if __name__ == "__main__":
    print("=== Engine 테스트 ===")
    engine = StockEngine("tesla_2024_03_14d")

    print("첫 날:", engine.get_today_price())

    for i in range(20):
        p = engine.next_day()
        if p is None:
            print("더 이상 날짜가 없습니다.")
            break
        print(f"{engine.state.day_index}일차:", p)
