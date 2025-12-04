from game_logic.game_controller import GameController

if __name__ == "__main__":
    game = GameController("tesla_2024_03_14d")

    print("=== GameController 테스트 시작 ===")

    for _ in range(20):
        state = game.get_state()
        print("\n=== 오늘 상태 ===")
        print(state)

        print("→ TSLA 1주 매수")
        game.submit_order("BUY", 1)

        print("→ 하루 종료, 주문 체결")
        game.end_day()

        if game.next_day() is None:
            print("\n=== 마지막 날 도달: 종료 ===")
            break
