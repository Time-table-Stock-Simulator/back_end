#시나리오 / CSV 로딩
import json
import csv
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import List

from .models import DayPrice, Scenario #models.py 내용
from datetime import date

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCENARIO_DIR = DATA_DIR / "scenarios"
PRICE_DIR = DATA_DIR / "prices"

def load_scenarios() -> list[Scenario]:
    json_path = SCENARIO_DIR / "scenarios.json"
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)

    scenarios = []
    for item in raw:
        scenarios.append(
            Scenario(
                id=item["id"],
                symbol=item["symbol"],
                csv_file=item["csv_file"],
                start_date=item["start_date"],
                num_days=item["num_days"],
                title=item["title"],
                description=item["description"],
            )
        )
    return scenarios

def load_prices_for_scenario(scenario: Scenario) -> List[DayPrice]:
    """
    CSV 파일을 읽고 DayPrice 리스트로 변환하며,
    start_date 이후 num_days만 잘라내어 반환.
    """
    path = PRICE_DIR / scenario.csv_file
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # CSV 컬럼 이름이 반드시 "date, open, high, low, close, volume" 이어야 함
            rows.append(
                DayPrice(
                    date=r["date"],
                    open=float(r["open"]),
                    high=float(r["high"]),
                    low=float(r["low"]),
                    close=float(r["close"]),
                    volume=int(r["volume"]),
                )
            )

    # 날짜로 필터링
    start = datetime.fromisoformat(scenario.start_date).date()
    rows = [p for p in rows if datetime.fromisoformat(p.date).date() >= start]

    # num_days 만큼 자르기
    return rows[: scenario.num_days]

if __name__ == "__main__":
    print("=== 시나리오 목록 ===")
    scenarios = load_scenarios()
    for s in scenarios:
        print(f"- {s.id}: {s.title} ({s.symbol})")

    print("\n=== tesla_2024_03_14d 가격 슬라이스 ===")
    target_id = "tesla_2024_03_14d"

    # id로 Scenario 하나 찾기
    tesla_scenario = None
    for s in scenarios:
        if s.id == target_id:
            tesla_scenario = s
            break

    if tesla_scenario is None:
        print("해당 id의 시나리오를 찾을 수 없습니다:", target_id)
    else:
        prices = load_prices_for_scenario(tesla_scenario)
        print(f"총 {len(prices)} 거래일")
        for p in prices:
            print(p)