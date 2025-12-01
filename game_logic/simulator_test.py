from game_logic.engine import StockEngine

if __name__ == "__main__":
    engine = StockEngine("tesla_2024_03_14d")

    print("=== 시뮬레이터 시작 ===")

    while True:
        today = engine.get_today_price()
        print(f"\n오늘 날짜: {today.date}, 종가 {today.close}")

        # 예시: 매일 TSLA 1주씩 자동 매수 (테스트용)
        engine.submit_order(symbol=engine.scenario.symbol, side="BUY", quantity=1)
        print(" → 오늘 주문: TSLA 1주 매수")

        # 오늘 주문 체결
        engine.process_orders()

        # 포트폴리오 출력
        print(engine.portfolio)

        # 내일로 이동
        next_price = engine.next_day()
        if next_price is None:
            print("=== 시뮬레이터 종료: 마지막 날짜 도달 ===")
            break
