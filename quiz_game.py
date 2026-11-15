"""퀴즈 게임 전체(메뉴, 진행)를 관리하는 QuizGame 클래스."""

import random

from default_quizzes import get_default_quizzes
from input_utils import read_number, read_text
from quiz import Quiz

LINE = "=" * 40


class QuizGame:
    """메뉴를 보여 주고 사용자가 고른 기능을 실행한다."""

    MENU_ITEMS = ["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "종료"]

    def __init__(self):
        self.quizzes = get_default_quizzes()  # Quiz 인스턴스 목록
        self.best_score = None   # 최고 점수(100점 만점). 아직 안 풀었으면 None
        self.best_correct = 0    # 최고 점수를 냈을 때 맞힌 문제 수
        self.best_total = 0      # 최고 점수를 냈을 때 푼 문제 수

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
        elif choice == 2:
            self.add_quiz()
        elif choice == 3:
            self.list_quizzes()
        elif choice == 4:
            self.show_best_score()

    def play_quiz(self):
        """저장된 퀴즈를 차례로 출제하고 결과를 보여 준다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다. 먼저 '퀴즈 추가'로 퀴즈를 등록하세요.\n")
            return

        # 보너스: 풀 문제 수를 고르고, 문제 순서를 무작위로 섞는다.
        total = read_number(f"\n몇 문제를 풀까요? (1-{len(self.quizzes)}): ", 1, len(self.quizzes))
        selected = random.sample(self.quizzes, total)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)\n")

        correct = 0
        for number, quiz in enumerate(selected, start=1):
            print("-" * 40)
            quiz.display(number)
            user_answer = read_number("정답 입력: ", 1, quiz.CHOICE_COUNT)
            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!\n")
                correct += 1
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer_text()}입니다.\n")

        score = self.show_result(correct, total)
        self.update_best_score(score, correct, total)

    def update_best_score(self, score, correct, total):
        """이번 점수가 최고 점수보다 높으면 갱신하고 True를 반환한다."""
        if self.best_score is not None and score <= self.best_score:
            print(f"(현재 최고 점수: {self.best_score}점)\n")
            return False

        self.best_score = score
        self.best_correct = correct
        self.best_total = total
        print("🎉 새로운 최고 점수입니다!\n")
        return True

    def show_best_score(self):
        """최고 점수를 보여 준다. 아직 퀴즈를 풀지 않았으면 안내한다."""
        if self.best_score is None:
            print("\n📭 아직 퀴즈를 푼 기록이 없습니다. 먼저 퀴즈를 풀어 보세요!\n")
            return
        print(f"\n🏆 최고 점수: {self.best_score}점 "
              f"({self.best_total}문제 중 {self.best_correct}문제 정답)\n")

    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.\n")
        question = read_text("문제를 입력하세요: ")
        choices = [read_text(f"선택지 {index}: ") for index in range(1, Quiz.CHOICE_COUNT + 1)]
        answer = read_number(f"정답 번호 (1-{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT)

        self.quizzes.append(Quiz(question, choices, answer))
        print("\n✅ 퀴즈가 추가되었습니다!\n")

    def list_quizzes(self):
        """등록된 퀴즈의 문제를 번호와 함께 보여 준다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다.\n")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)\n")
        print("-" * 40)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print("-" * 40 + "\n")

    def show_result(self, correct, total):
        """맞힌 개수와 100점 만점 점수를 출력하고 점수를 반환한다."""
        score = round(correct / total * 100)
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        print(LINE)
        return score
