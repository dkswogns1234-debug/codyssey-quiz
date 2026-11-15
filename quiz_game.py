"""퀴즈 게임 전체(메뉴, 진행)를 관리하는 QuizGame 클래스."""

import json
import os
import random
from pathlib import Path

from default_quizzes import get_default_quizzes
from input_utils import read_number, read_text
from quiz import Quiz

LINE = "=" * 40

# 실행 위치와 상관없이 항상 프로젝트 루트(이 파일이 있는 폴더)의 state.json을 쓴다.
STATE_FILE = Path(__file__).resolve().parent / "state.json"


class QuizGame:
    """게임 전체를 관리한다: 퀴즈 목록·최고 점수 보관, 메뉴 표시, 각 기능 실행."""

    # (메뉴 이름, 실행할 메서드 이름). 마지막 항목은 종료라서 메서드가 없다.
    MENU = [
        ("퀴즈 풀기", "play_quiz"),
        ("퀴즈 추가", "add_quiz"),
        ("퀴즈 목록", "list_quizzes"),
        ("점수 확인", "show_best_score"),
        ("종료", None),
    ]

    def __init__(self, state_file=STATE_FILE):
        self.state_file = Path(state_file)
        # 저장 허용 스위치. 불러오기를 마치기 전(예: 불러오는 중 Ctrl+C)이나
        # 파일을 열 수 없을 때 기존 state.json을 기본 데이터로 덮어쓰지 않도록 막는다.
        self.save_enabled = False
        self.quizzes = get_default_quizzes()  # Quiz 인스턴스 목록
        self.best_score = None   # 최고 점수(100점 만점). 아직 안 풀었으면 None
        self.best_correct = 0    # 최고 점수를 냈을 때 맞힌 문제 수
        self.best_total = 0      # 최고 점수를 냈을 때 푼 문제 수

    def run(self):
        """프로그램의 메인 반복. 종료를 고를 때까지 메뉴를 계속 보여 준다."""
        # 불러오기부터 메뉴 반복까지 전부 try 안에 두어, 어느 시점에 Ctrl+C를 눌러도 안전하게 끝낸다.
        try:
            self.show_title()
            self.load_state()
            while True:
                self.show_menu()
                choice = read_number("선택: ", 1, len(self.MENU))
                if not self.handle_choice(choice):
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️ 입력이 중단되어 프로그램을 종료합니다.")
        self.quit()

    def show_title(self):
        """프로그램 제목을 출력한다."""
        print(LINE)
        print("🎯 파이썬 상식 퀴즈 게임 🎯")

    def show_menu(self):
        """메뉴 목록을 번호와 함께 출력한다."""
        print(LINE)
        for number, (label, _) in enumerate(self.MENU, start=1):
            print(f"{number}. {label}")
        print(LINE)

    def handle_choice(self, choice):
        """선택한 번호의 기능을 실행한다. 종료를 골랐으면 False를 반환한다."""
        _, method_name = self.MENU[choice - 1]
        if method_name is None:
            return False
        getattr(self, method_name)()
        return True

    def quit(self):
        """가능하면 데이터를 저장하고 종료 인사를 출력한다."""
        try:
            if self.save_state():
                print("💾 데이터를 저장했습니다.")
        except KeyboardInterrupt:
            # 저장 도중 Ctrl+C를 또 눌러도 임시 파일 방식이라 기존 state.json은 깨지지 않는다.
            print("\n⚠️ 저장이 중단되었습니다. 마지막으로 저장된 데이터는 그대로 남아 있습니다.")
        print("👋 게임을 종료합니다. 다음에 또 만나요!")

    # ---------- 파일 저장/불러오기 (state.json) ----------

    def load_state(self):
        """state.json에서 퀴즈와 최고 점수를 불러온다. 없거나 손상됐으면 기본 데이터를 쓴다."""
        if not self.state_file.exists():
            self.save_enabled = True
            self.reset_to_default()
            print(f"📂 저장된 데이터가 없어 기본 퀴즈 {len(self.quizzes)}개로 시작합니다.")
            self.save_state()
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("최상위 데이터가 {...} 형태(dict)가 아닙니다.")
            if not isinstance(data.get("quizzes"), list):
                raise ValueError("quizzes 항목이 없거나 목록(list)이 아닙니다.")
            if not all(isinstance(item, dict) for item in data["quizzes"]):
                raise ValueError("quizzes 안의 퀴즈가 {...} 형태(dict)가 아닙니다.")
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            best = data.get("best_score")
            best_correct = data.get("best_correct", 0)
            best_total = data.get("best_total", 0)
            if best is not None and (isinstance(best, bool) or not isinstance(best, int)
                                     or not 0 <= best <= 100):
                raise ValueError("best_score는 0~100 사이의 정수 또는 null이어야 합니다.")
            if not all(isinstance(n, int) and not isinstance(n, bool) and n >= 0
                       for n in (best_correct, best_total)):
                raise ValueError("best_correct, best_total은 0 이상의 정수여야 합니다.")
            if best_correct > best_total:
                raise ValueError("맞힌 문제 수(best_correct)가 푼 문제 수(best_total)보다 많습니다.")
            # 세 값이 서로 맞는지 검사: 안 풀었으면 null/0/0, 풀었으면 점수 = 맞힌 수 / 푼 수 × 100
            if best is None and (best_correct, best_total) != (0, 0):
                raise ValueError("최고 점수가 없는데 정답 기록이 남아 있습니다.")
            if best is not None and (best_total == 0 or best != round(best_correct / best_total * 100)):
                raise ValueError("최고 점수가 맞힌 수/푼 수와 맞지 않습니다.")
        except OSError as error:
            # 권한 문제 등으로 '읽기'에 실패한 것은 손상이 아니므로 원본 파일을 건드리지 않는다.
            print(f"⚠️ 저장 파일을 열 수 없습니다. ({error})")
            print("🔒 원본 파일을 보호하기 위해 이번 실행은 기본 퀴즈로 진행하고 저장하지 않습니다.")
            self.reset_to_default()
            return  # save_enabled는 False 그대로 둔다.
        except (json.JSONDecodeError, UnicodeDecodeError, RecursionError,
                KeyError, TypeError, ValueError) as error:
            print(f"⚠️ 저장 파일이 손상되어 읽을 수 없습니다. ({error})")
            self.reset_to_default()
            if self.backup_broken_file():
                self.save_enabled = True
                print(f"🔧 기본 퀴즈 {len(self.quizzes)}개로 복구했습니다.")
                self.save_state()
            else:
                # 백업을 못 했는데 저장하면 원본이 사라지므로, 이번 실행은 저장하지 않는다.
                print("🔒 원본을 보호하기 위해 이번 실행은 기본 퀴즈로 진행하고 저장하지 않습니다.")
            return

        self.save_enabled = True
        self.quizzes = quizzes
        self.best_score = best
        self.best_correct = best_correct
        self.best_total = best_total
        best_text = "없음" if best is None else f"{best}점"
        print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {best_text})")

    def save_state(self):
        """퀴즈와 최고 점수를 state.json에 UTF-8로 저장한다. 성공하면 True를 반환한다."""
        if not self.save_enabled:
            return False
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total,
        }
        temp_file = self.state_file.with_name(self.state_file.name + ".tmp")
        try:
            # 임시 파일에 다 쓴 뒤 바꿔치기해서, 저장 도중 꺼져도 원래 파일이 깨지지 않게 한다.
            with open(temp_file, "w", encoding="utf-8", newline="\n") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            os.replace(temp_file, self.state_file)
            return True
        except OSError as error:
            print(f"⚠️ 데이터를 저장하지 못했습니다. ({error})")
            return False

    def backup_broken_file(self):
        """손상된 state.json을 state.json.bak으로 옮겨 내용을 보존한다. 성공하면 True를 반환한다."""
        backup = self.state_file.with_name(self.state_file.name + ".bak")
        try:
            os.replace(self.state_file, backup)
        except OSError as error:
            print(f"⚠️ 손상된 파일을 백업하지 못했습니다. ({error})")
            return False
        print(f"🗂️ 손상된 파일은 {backup.name}(으)로 백업했습니다.")
        return True

    def reset_to_default(self):
        """퀴즈를 기본 데이터로 되돌리고 최고 점수 기록을 지운다."""
        self.quizzes = get_default_quizzes()
        self.best_score = None
        self.best_correct = 0
        self.best_total = 0

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
        """이번 점수가 최고 점수보다 높으면 갱신하고 True를 반환한다.

        점수가 같으면 더 많은 문제를 푼 기록을 최고 기록으로 남긴다.
        (예: 1문제 중 1개 정답 100점 → 8문제 중 8개 정답 100점으로 갱신)
        """
        is_better = (self.best_score is None or score > self.best_score
                     or (score == self.best_score and total > self.best_total))
        if not is_better:
            print(f"(현재 최고 점수: {self.best_score}점)\n")
            return False

        self.best_score = score
        self.best_correct = correct
        self.best_total = total
        print("🎉 새로운 최고 점수입니다!\n")
        self.save_state()
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
        choices = []
        while len(choices) < Quiz.CHOICE_COUNT:
            choice = read_text(f"선택지 {len(choices) + 1}: ")
            if choice in choices:
                print("⚠️ 이미 입력한 선택지입니다. 다른 내용을 입력하세요.")
                continue
            choices.append(choice)
        answer = read_number(f"정답 번호 (1-{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT)

        self.quizzes.append(Quiz(question, choices, answer))
        if self.save_state():
            print("\n✅ 퀴즈가 추가되었습니다! (state.json에 저장됨)\n")
        else:
            print("\n✅ 퀴즈가 추가되었습니다. (파일 저장은 실패해 이번 실행 동안만 유지됩니다)\n")

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
        print(self.score_comment(score))
        print(LINE)
        return score

    def score_comment(self, score):
        """점수 구간에 따라 다른 격려 메시지를 반환한다."""
        if score == 100:
            return "💯 완벽해요! 모든 문제를 맞혔습니다."
        elif score >= 60:
            return "👍 잘했어요! 틀린 문제만 다시 보면 완벽해요."
        else:
            return "💪 괜찮아요! 다시 도전해 보세요."
