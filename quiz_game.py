"""퀴즈 게임 전체(메뉴, 진행)를 관리하는 QuizGame 클래스."""

from input_utils import read_number

LINE = "=" * 40


class QuizGame:
    """메뉴를 보여 주고 사용자가 고른 기능을 실행한다."""

    MENU_ITEMS = ["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "종료"]

    def run(self):
        """프로그램의 메인 반복. 종료를 고를 때까지 메뉴를 계속 보여 준다."""
        print(LINE)
        print("🎯 파이썬 상식 퀴즈 게임 🎯")
        try:
            while True:
                self.show_menu()
                choice = read_number("선택: ", 1, len(self.MENU_ITEMS))
                if choice == len(self.MENU_ITEMS):
                    break
                self.handle_choice(choice)
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️ 입력이 중단되어 프로그램을 종료합니다.")
        print("👋 게임을 종료합니다. 다음에 또 만나요!")

    def show_menu(self):
        """메뉴 목록을 번호와 함께 출력한다."""
        print(LINE)
        for number, item in enumerate(self.MENU_ITEMS, start=1):
            print(f"{number}. {item}")
        print(LINE)

    def handle_choice(self, choice):
        """선택한 번호에 맞는 기능을 실행한다."""
        print(f"\n🚧 '{self.MENU_ITEMS[choice - 1]}' 기능은 준비 중입니다.\n")
