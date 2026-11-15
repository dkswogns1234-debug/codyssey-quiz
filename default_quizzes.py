"""state.json이 없거나 손상됐을 때 사용하는 기본 퀴즈 데이터 (주제: 파이썬·프로그래밍 상식)."""

from quiz import Quiz


def get_default_quizzes():
    """기본 퀴즈를 Quiz 인스턴스 목록으로 새로 만들어 반환한다."""
    return [
        Quiz("파이썬에서 print(type(3.0))을 실행하면 나오는 자료형은?",
             ["int", "float", "str", "bool"], 2),
        Quiz("numbers = [10, 20, 30] 에서 20을 꺼내는 코드는?",
             ["numbers[0]", "numbers[1]", "numbers[2]", "numbers[-1]"], 2),
        Quiz("다음 중 한 번 만들면 내용을 바꿀 수 없는(immutable) 자료형은?",
             ["list", "dict", "set", "tuple"], 4),
        Quiz("반복 횟수가 정해져 있지 않고 '조건이 참인 동안' 반복할 때 주로 쓰는 문은?",
             ["for", "while", "if", "def"], 2),
        Quiz("클래스로 객체를 만들 때 자동으로 실행되는 메서드는?",
             ["__str__", "__init__", "__call__", "__del__"], 2),
        Quiz("print(7 // 2)의 실행 결과는?",
             ["3.5", "3", "4", "1"], 2),
        Quiz("원격 저장소를 내 컴퓨터로 통째로 복제하는 Git 명령어는?",
             ["git pull", "git push", "git clone", "git init"], 3),
        Quiz("JSON 파일을 읽어서 파이썬 객체(dict, list 등)로 바꾸는 함수는?",
             ["json.dump", "json.dumps", "json.load", "json.save"], 3),
    ]
