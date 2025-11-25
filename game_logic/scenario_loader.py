from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .models import DayPrice, Scenario #models.py 내용
from datetime import date

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PRICES_DIR = DATA_DIR / "prices"
SCENARIOS_PATH = DATA_DIR / "scenarios" / "scenarios.json"


def load_scenarios() -> List[Scenario]:
    """
    scenarios.json 전체를 읽어서 Scenario 객체 리스트로 반환.
    """
    with SCENARIOS_PATH.open(encoding="utf-8") as f:
        raw_list = json.load(f)

    scenarios: List[Scenario] = [Scenario(**item) for item in raw_list]
    return scenarios

def get_scenario(scenario_id: str) -> Scenario:
    """
    ID로 특정 시나리오 한 개 찾기.
    """
    for s in load_scenarios():
        if s.id == scenario_id:
            return s
    raise ValueError(f"시나리오를 찾을 수 없습니다: {scenario_id}")


def load_price_slice(scenario_id: str) -> List[DayPrice]:
    """
    주어진 시나리오 ID 기준으로
    - 해당 csv 파일을 읽고
    - start_date부터 num_days(거래일) 만큼 잘라서 DayPrice 리스트로 반환.
    """
    scenario = get_scenario(scenario_id)
    csv_path = PRICES_DIR / scenario.csv_file

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 파일이 없습니다: {csv_path}")

    days: List[DayPrice] = []

    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)

        started = False

        for row in reader:
            row_date = row["date"]

            # 아직 시작 날짜 전이면 스킵
            if not started:
                if row_date < scenario.start_date:
                    continue
                # start_date 이상이 처음 나타난 순간
                started = True

            # 여기에 오면 start_date 이상
            if started and len(days) < scenario.num_days:
                days.append(
                    DayPrice(
                        date=row_date,
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=int(float(row["volume"])),
                    )
                )

            # 원하는 일수만큼 모였으면 끝
            if len(days) >= scenario.num_days:
                break

    return days


if __name__ == "__main__":
    print("=== 시나리오 목록 ===")
    for s in load_scenarios():
        print(f"- {s.id}: {s.title} ({s.symbol})")

    print("\n=== tesla_2024_03_14d 가격 슬라이스 ===")
    prices = load_price_slice("tesla_2024_03_14d")
    print(f"총 {len(prices)} 거래일")
    for p in prices:
        print(p)