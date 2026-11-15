"""퀴즈 게임 자동 테스트 (표준 라이브러리 unittest만 사용).

실행: 프로젝트 루트에서  python -m unittest discover -s tests -v
- 단위 테스트: Quiz 검증, 입력 검증(read_number/read_text), 점수 규칙, 저장/불러오기·복구
- 통합 테스트: 실제 main.py를 새 프로세스로 실행해 메뉴 흐름을 끝까지 확인
- 모든 테스트는 임시 폴더의 state.json을 쓰므로 프로젝트의 state.json은 바뀌지 않는다.
"""

import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import quiz_game  # noqa: E402
from default_quizzes import get_default_quizzes  # noqa: E402
from input_utils import read_number, read_text  # noqa: E402
from quiz import Quiz  # noqa: E402
from quiz_game import QuizGame  # noqa: E402


def quiet(func, *args):
    """화면 출력을 모아서 (반환값, 출력 문자열)로 돌려준다."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = func(*args)
    return result, buffer.getvalue()


class TestQuiz(unittest.TestCase):
    """Quiz 한 문제의 생성 검증과 채점."""

    def test_valid_quiz_and_grading(self):
        q = Quiz("1+1은?", ["1", "2", "3", "4"], 2)
        self.assertTrue(q.is_correct(2))
        self.assertFalse(q.is_correct(3))
        self.assertEqual(q.answer_text(), "2번 (2)")

    def test_invalid_quiz_is_rejected(self):
        bad_cases = [
            ("", ["a", "b", "c", "d"], 1),          # 빈 문제
            ("Q", ["a", "b", "c"], 1),               # 선택지 3개
            ("Q", ["a", "b", "c", " "], 1),          # 빈 선택지
            ("Q", ["a", "b", "c", "d"], 0),          # 정답 범위 밖
            ("Q", ["a", "b", "c", "d"], 5),
            ("Q", ["a", "b", "c", "d"], True),       # bool은 정답 번호로 인정하지 않음
            ("Q", ["a", "b", "c", "d"], "2"),        # 문자열 정답
        ]
        for case in bad_cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                Quiz(*case)

    def test_dict_round_trip(self):
        q = Quiz("문제", ["가", "나", "다", "라"], 4)
        self.assertEqual(Quiz.from_dict(q.to_dict()).to_dict(), q.to_dict())


class TestInputUtils(unittest.TestCase):
    """입력 검증: 공백 제거, 빈 입력, 숫자 아님, 범위 밖 → 다시 묻기."""

    def test_read_number_retries_until_valid(self):
        inputs = iter(["", "abc", "9", "0", " 3 "])
        with mock.patch("builtins.input", lambda prompt="": next(inputs)):
            value, out = quiet(read_number, "선택: ", 1, 5)
        self.assertEqual(value, 3)                      # " 3 " → 공백 제거 후 3
        self.assertIn("입력이 비어 있습니다", out)       # 빈 입력
        self.assertIn("잘못된 입력입니다", out)          # abc
        self.assertEqual(out.count("범위를 벗어났습니다"), 2)  # 9, 0

    def test_read_text_rejects_blank(self):
        inputs = iter(["   ", "", "  문제  "])
        with mock.patch("builtins.input", lambda prompt="": next(inputs)):
            value, out = quiet(read_text, "문제: ")
        self.assertEqual(value, "문제")
        self.assertEqual(out.count("빈 값은 입력할 수 없습니다"), 2)


class TestScoreRule(unittest.TestCase):
    """최고 점수 세 값(best_score, best_correct, best_total)의 일관성 규칙."""

    def test_valid_records(self):
        for record in [(None, 0, 0), (80, 4, 5), (67, 2, 3), (0, 0, 1), (100, 8, 8)]:
            with self.subTest(record=record):
                self.assertIsNone(QuizGame.check_score_record(*record))

    def test_invalid_records(self):
        for record in [(100, 0, 0), (None, 3, 5), (90, 4, 5), (50, 3, 2)]:
            with self.subTest(record=record):
                self.assertIsNotNone(QuizGame.check_score_record(*record))


class TestStateFile(unittest.TestCase):
    """state.json 저장/불러오기와 없음·손상·권한·점수 불일치 처리."""

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.state = self.folder / "state.json"

    def tearDown(self):
        shutil.rmtree(self.folder)

    def new_game(self):
        game = QuizGame(self.state)
        quiet(game.load_state)
        return game

    def test_missing_file_starts_with_defaults_and_creates_file(self):
        game = self.new_game()
        self.assertEqual(len(game.quizzes), len(get_default_quizzes()))
        self.assertTrue(self.state.exists())

    def test_saved_quiz_and_score_survive_restart(self):
        game = self.new_game()
        game.quizzes.append(Quiz("새 문제", ["a", "b", "c", "d"], 1))
        quiet(game.update_best_score, 75, 3, 4)       # 갱신하면서 저장
        again = self.new_game()
        self.assertEqual(again.quizzes[-1].question, "새 문제")
        self.assertEqual((again.best_score, again.best_correct, again.best_total), (75, 3, 4))

    def test_utf8_without_escaping(self):
        self.new_game()
        self.assertIn("파이썬".encode("utf-8"), self.state.read_bytes())

    def test_broken_file_is_backed_up_and_reset(self):
        broken_cases = ["{ broken", "[]", '{"quizzes": ""}',
                        '{"quizzes": [], "best_score": 100, "best_correct": 0, "best_total": 0}']
        for text in broken_cases:
            with self.subTest(text=text):
                self.state.write_text(text, encoding="utf-8")
                game = self.new_game()
                self.assertEqual(len(game.quizzes), len(get_default_quizzes()))
                backup = self.folder / "state.json.bak"
                self.assertEqual(backup.read_text(encoding="utf-8"), text)
                backup.unlink()

    def test_permission_error_keeps_original_and_disables_saving(self):
        self.new_game()
        original = self.state.read_bytes()
        real_open = open

        def deny(path, *args, **kwargs):
            if Path(path) == self.state and (not args or "r" in args[0]):
                raise PermissionError(13, "테스트용 권한 오류")
            return real_open(path, *args, **kwargs)

        with mock.patch.object(quiz_game, "open", deny, create=True):
            game = QuizGame(self.state)
            _, out = quiet(game.load_state)
            saved, _ = quiet(game.save_state)
        self.assertIn("🔒", out)
        self.assertFalse(saved)
        self.assertEqual(self.state.read_bytes(), original)

    def test_inconsistent_score_is_not_saved(self):
        game = self.new_game()
        before = self.state.read_bytes()
        game.best_score = 100                           # 정답 수·푼 수는 아직 0 (갱신 도중 중단 흉내)
        saved, out = quiet(game.save_state)
        self.assertFalse(saved)
        self.assertIn("저장하지 않았습니다", out)
        self.assertEqual(self.state.read_bytes(), before)


class TestReadmeMatchesCode(unittest.TestCase):
    """README에 적힌 숫자가 실제 코드와 같은지 확인 (문서와 코드가 어긋나는 것 방지)."""

    def test_default_quiz_count_in_readme(self):
        count = len(get_default_quizzes())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(count, 5)               # 미션 요구: 5개 이상
        self.assertIn(f"기본 퀴즈 {count}개", readme)
        numbers = set(re.findall(r"기본 퀴즈 (\d+)개", readme))
        self.assertEqual(numbers, {str(count)})         # README 안의 모든 '기본 퀴즈 N개'가 같은 숫자

    def test_repository_state_json_is_valid_initial_state(self):
        data = json.loads((ROOT / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["quizzes"]), len(get_default_quizzes()))
        self.assertIsNone(QuizGame.check_score_record(data["best_score"], data["best_correct"], data["best_total"]))


class TestMainIntegration(unittest.TestCase):
    """실제 main.py를 새 프로세스로 실행하는 통합 테스트 (임시 폴더에 프로젝트를 복사해서 실행)."""

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        for name in ["main.py", "quiz.py", "quiz_game.py", "input_utils.py", "default_quizzes.py"]:
            shutil.copy(ROOT / name, self.folder / name)

    def tearDown(self):
        shutil.rmtree(self.folder)

    def run_main(self, *lines):
        process = subprocess.run([sys.executable, "main.py"], cwd=self.folder, input="\n".join(lines) + "\n",
                                 capture_output=True, text=True, encoding="utf-8", timeout=30)
        return process.returncode, process.stdout + process.stderr

    def test_full_menu_flow_and_persistence(self):
        code, out = self.run_main("abc", "9", "", "2", "새 문제?", "A", "B", "C", "D", "3",
                                  "3", "1", "1", "4", "4", "5")
        self.assertEqual(code, 0)
        self.assertNotIn("Traceback", out)
        for text in ["잘못된 입력", "범위를 벗어났", "입력이 비어", "퀴즈가 추가되었습니다",
                     "[9] 새 문제?", "퀴즈를 시작합니다", "결과:", "최고 점수:", "게임을 종료합니다"]:
            self.assertIn(text, out)
        code, out = self.run_main("3", "5")             # 다시 실행 → 추가한 퀴즈 유지
        self.assertIn("[9] 새 문제?", out)

    def test_eof_exits_safely(self):
        code, out = self.run_main()                     # 입력 없이 끝(EOF)
        self.assertEqual(code, 0)
        self.assertIn("입력이 중단되어", out)
        self.assertNotIn("Traceback", out)


if __name__ == "__main__":
    unittest.main()
