from game_logic.engine import StockEngine

class GameController:
    def __init__(self, scenario_id:str):
        self.engine = StockEngine([scenario_id])

    #오늘 상태 조회
    def get_state(self) -> dict:
        symbol = list(self.engine.symbol_states.keys())[0]
        today = self.engine.get_today_price(symbol)

        return {
            "day_index": self.engine.symbol_states[symbol]["day_index"],
            "date": today.date,
            "symbol": symbol,
            "price": {
                "open": round(today.open, 2),
                "high": round(today.high, 2),
                "low": round(today.low, 2),
                "close": round(today.close, 2),
            },
            "portfolio": {
                "cash": round(self.engine.portfolio.cash, 2),
                "holding": {
                    sym: {
                        "quantity": h.quantity,
                        "avg_price": round(h.avg_price, 2)
                    }
                    for sym, h in self.engine.portfolio.holding.items()
                }
            }
        }

    #주문 제출
    def submit_order(self, side: str, quantity: int):
        symbol = list(self.engine.symbol_states.keys())[0]
        return self.engine.submit_order(symbol=symbol, side=side, quantity=quantity)

    # 하루 종료 → 주문 체결
    def end_day(self):
        self.engine.process_orders()

    # 다음날로 이동
    def next_day(self):
        return self.engine.next_day()