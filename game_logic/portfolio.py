#매수, 매도 금액 계산
from dataclasses import dataclass, field


@dataclass
class Holding:
    symbol: str
    quantity: int
    avg_price: float  # 매입 평균 단가


@dataclass
class Portfolio:
    balance: float = 10_000_000.0  # 초기 자금
    holdings: dict[str, Holding] = field(default_factory=dict)

    # 매수
    def buy(self, symbol: str, quantity: int, price: float):
        cost = quantity * price
        if cost > self.balance:
            raise ValueError("잔고 부족으로 매수할 수 없습니다.")

        self.balance -= cost

        if symbol not in self.holdings:
            self.holdings[symbol] = Holding(symbol, quantity, price)
        else:
            h = self.holdings[symbol]
            new_total_cost = h.avg_price * h.quantity + cost
            h.quantity += quantity
            h.avg_price = new_total_cost / h.quantity

    # 매도
    def sell(self, symbol: str, quantity: int, price: float):
        if symbol not in self.holdings:
            raise ValueError("보유하지 않은 종목입니다.")

        h = self.holdings[symbol]
        if quantity > h.quantity:
            raise ValueError("보유 수량보다 많이 팔 수 없습니다.")

        h.quantity -= quantity
        self.balance += quantity * price

        # 수량 0이면 제거
        if h.quantity == 0:
            del self.holdings[symbol]

    # 평가금액 계산
    def evaluate(self, current_prices: dict[str, float]):
        total = self.balance
        for symbol, h in self.holdings.items():
            if symbol in current_prices:
                total += h.quantity * current_prices[symbol]
        return total

if __name__ == "__main__":
    p = Portfolio()

    print("초기 잔고:", p.balance)

    p.buy("TSLA", 3, 200.0)
    print("TSLA 3주 매수 후 잔고:", p.balance)
    print("보유:", p.holdings)

    p.sell("TSLA", 1, 220.0)
    print("TSLA 1주 매도 후 잔고:", p.balance)
    print("보유:", p.holdings)

    prices = {"TSLA": 210}
    print("총 평가금액:", p.evaluate(prices))