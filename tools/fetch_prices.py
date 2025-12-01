# backend/tools/fetch_prices.py

from pathlib import Path

import pandas as pd
import yfinance as yf


# 이 파일 기준으로 두 칸 위(= back_end 폴더)를 BASE_DIR로 사용
BASE_DIR = Path(__file__).resolve().parents[1]

# CSV를 저장할 폴더: back_end/data/prices
DATA_DIR = BASE_DIR / "data" / "prices"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_and_save(symbol: str, start: str, end: str, filename: str | None = None) -> None:
    """
    야후 파이낸스에서 특정 종목(symbol)의 주가를
    start ~ end 기간 동안 받아와서 CSV로 저장한다.

    - symbol: "TSLA", "ACHR", "GOOGL", "005930.KS" 같은 티커 문자열
    - start, end: "YYYY-MM-DD" 형식 문자열
    - filename: 저장할 CSV 파일 이름 (None이면 symbol.csv로 저장)
    """
    print(f"[INFO] Fetching {symbol} from {start} to {end} ...")

    # 1) 데이터 다운로드
    # auto_adjust=False 로 명시해서 경고도 없애고, OHLC 그대로 받기
    df = yf.download(
        symbol,
        start=start,
        end=end,
        progress=False,
        auto_adjust=False,
    )

    if df.empty:
        print(f"[WARN] {symbol} 에 대해 다운로드된 데이터가 없습니다.")
        return

    # 2) MultiIndex 컬럼이면 level 0(Open/High/...)만 남기기
    if isinstance(df.columns, pd.MultiIndex):
        # level 0: Open, High, Low, Close, Adj Close, Volume
        # level 1: 티커 이름(TSLA, ACHR ...)
        df.columns = df.columns.get_level_values(0)

    # 3) 우리가 쓸 컬럼들만 선택 + 이름 통일
    # yfinance 기본 컬럼: Open, High, Low, Close, Adj Close, Volume
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    # 인덱스(Date)를 컬럼으로 바꾸기
    df.reset_index(inplace=True)

    # 날짜를 "YYYY-MM-DD" 문자열로 통일
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # 컬럼명을 소문자로 통일
    df.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        },
        inplace=True,
    )

    # 4) CSV 저장
    if filename is None:
        filename = f"{symbol}.csv"

    csv_path = DATA_DIR / filename
    df.to_csv(csv_path, index=False, encoding="utf-8")

    print(f"[OK] Saved {len(df)} rows to {csv_path}")


if __name__ == "__main__":
    # 공통 기간
    start = "2024-03-04"
    end = "2024-03-22" #일단 14일로 만들어봄

    stocks = [
        ("TSLA", "tesla_2024_03.csv"),          # 1) 테슬라
        ("ACHR", "archer_2024_03.csv"),         # 2) 아처 에비에이션
        ("GOOGL", "google_2024_03.csv"),        # 3) 구글 (Alphabet A)
        ("005930.KS", "samsung_2024_03.csv"),   # 4) 삼성전자 (코스피)
    ]

    for symbol, fname in stocks:
        fetch_and_save(symbol=symbol, start=start, end=end, filename=fname)