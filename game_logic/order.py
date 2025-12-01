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
