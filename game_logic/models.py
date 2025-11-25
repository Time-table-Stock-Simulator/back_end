# back_end/game_logic/models.py
from dataclasses import dataclass
from typing import List
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