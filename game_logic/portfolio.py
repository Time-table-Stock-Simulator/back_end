# back_end/game_logic/portfolio.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

from .models import DayPrice
from .scenario_loader import load_price_slice, get_scenario


@dataclass
class Position:
    """
    단일 종목 보유 상태.
    향후 /order 구현 시 qty/avg(평단)만 있어도 계산 가능.
    """
    qty: float = 0.0
    avg: float = 0.0


@dataclass
class Session:
    """
    한 번의 게임 세션(특정 시나리오에 대한 14거래일 플레이).
    """
    session_id: str
    scenario_id: str
    days: List[DayPrice]
    idx: int = 0  # 현재 거래일 인덱스(0-based)
    cash: float = 100_000.0
    positions: Dict[str, Position] = field(default_factory=dict)
    pnl_realized: float = 0.0  # 실현손익(시장가 매도 시 갱신 예정)

    # ---- 조회/진행 기본기 ----
    def current_day(self) -> DayPrice:
        """현재 거래일의 DayPrice 반환"""
        return self.days[self.idx]

    def step(self) -> None:
        """하루 전진(마지막 날이면 더 진행하지 않음)"""
        if self.idx < len(self.days) - 1:
            self.idx += 1

    # ---- (다음 단계에서 붙일 예정) 주문/평가 로직 ----
    # def place_order(...): pass
    # def mark_to_market(...): pass


# 인-메모리 세션 저장소
SESSIONS: Dict[str, Session] = {}


def new_session(session_id: str, scenario_id: str, initial_cash: float = 100_000.0) -> Session:
    """
    시나리오 기반으로 새 세션 생성:
    - 시나리오 유효성 확인(get_scenario)
    - 가격 슬라이스 로드(load_price_slice)
    - Session을 생성해 SESSIONS에 등록 후 반환
    """
    # 시나리오 존재 여부만 먼저 확인(메타 사용처 있을 시 활용 가능)
    _ = get_scenario(scenario_id)

    # 가격 슬라이스 로드(예: 14거래일)
    days = load_price_slice(scenario_id)
    if not days:
        raise ValueError(f"시나리오에 해당하는 가격 데이터가 비었습니다: {scenario_id}")

    sess = Session(
        session_id=session_id,
        scenario_id=scenario_id,
        days=days,
        cash=float(initial_cash),
    )
    SESSIONS[session_id] = sess
    return sess


def get_session(session_id: str) -> Session:
    """세션 조회(없으면 KeyError)"""
    if session_id not in SESSIONS:
        raise KeyError("세션 없음")
    return SESSIONS[session_id]
