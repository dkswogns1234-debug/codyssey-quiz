"""퀴즈 게임 전체(메뉴, 진행)를 관리하는 QuizGame 클래스."""

from default_quizzes import get_default_quizzes
from input_utils import read_number

LINE = "=" * 40


class QuizGame:
    """메뉴를 보여 주고 사용자가 고른 기능을 실행한다."""

    MENU_ITEMS = ["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "종료"]

    def __init__(self):
        self.quizzes = get_default_quizzes()  # Quiz 인스턴스 목록

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
        if choice == 1:
            self.play_quiz()
        else:
            print(f"\n🚧 '{self.MENU_ITEMS[choice - 1]}' 기능은 준비 중입니다.\n")

    def play_quiz(self):
        """저장된 퀴즈를 차례로 출제하고 결과를 보여 준다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다. 먼저 '퀴즈 추가'로 퀴즈를 등록하세요.\n")
            return

        total = len(self.quizzes)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)\n")

        correct = 0
        for number, quiz in enumerate(self.quizzes, start=1):
            print("-" * 40)
            quiz.display(number)
            user_answer = read_number("정답 입력: ", 1, quiz.CHOICE_COUNT)
            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!\n")
                correct += 1
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer_text()}입니다.\n")

        self.show_result(correct, total)

    def show_result(self, correct, total):
        """맞힌 개수와 100점 만점 점수를 출력하고 점수를 반환한다."""
        score = round(correct / total * 100)
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        print(LINE)
        return score
