#주문
from dataclasses import dataclass
from .models import Order

class OrderBook:
    def __init__(self):
        self.orders: list[Order] = []
        self.next_id = 1

    def create_order(self, symbol: str, side: str, quantity: int, submit_day: int) -> Order:
        order = Order(
            order_id=self.next_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            submit_day=submit_day,

        )
        self.orders.append(order)
        self.next_id += 1
        return order

    def get_open_orders(self):
        """아직 체결되지 않은 주문들만 반환"""
        return [o for o in self.orders if not o.is_filled]

if __name__ in ("__main__", "game_logic.order"):
    # 테스트 코드
    print("=== OrderBook 테스트 실행 ===")
    ob = OrderBook()
    o1 = ob.create_order("TSLA", "BUY", 3, submit_day=0)
    o2 = ob.create_order("TSLA", "SELL", 1, submit_day=1)
    print("전체 주문:", ob.orders)
    print("미체결 주문:", ob.get_open_orders())