# Portfolio, Order 같은 도메인 객체
from dataclasses import dataclass
from typing import Optional
@dataclass
class DayPrice:
    """
    하루치 가격 정보
    """
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class Scenario:
    """
    시나리오 메타데이터
    - 어떤 종목(csv_file)에서
    - 어느 날짜(start_date)부터
    - 몇 거래일(num_days)을 쓸지
    """
    id: str
    symbol: str
    csv_file: str
    start_date: str
    num_days: int
    title: str
    description: str

@dataclass
class Order:
    order_id: int
    symbol: str
    side: str              # "BUY" or "SELL"
    quantity: int
    submit_day: int        # 몇 번째 시뮬레이션 날짜에 제출했는지
    is_filled: bool = False
    filled_price: Optional[float] = None
    filled_day: Optional[int] = None