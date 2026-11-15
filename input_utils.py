"""사용자 입력을 받아 검증하는 함수 모음.

모든 함수는 올바른 값이 들어올 때까지 안내 메시지를 출력하고 다시 묻는다.
Ctrl+C(KeyboardInterrupt)와 입력 종료(EOFError)는 여기서 처리하지 않고
호출한 쪽(QuizGame.run)으로 그대로 올려 보내 안전하게 종료하도록 한다.
"""


def read_text(prompt):
    """앞뒤 공백을 지운, 비어 있지 않은 문자열을 입력받아 반환한다."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("⚠️ 빈 값은 입력할 수 없습니다. 다시 입력하세요.")


def read_number(prompt, low, high):
    """low 이상 high 이하의 정수를 입력받아 반환한다."""
    while True:
        text = input(prompt).strip()

        if not text:
            print(f"⚠️ 입력이 비어 있습니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue

        try:
            number = int(text)
        except ValueError:
            print(f"⚠️ 잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue

        if low <= number <= high:
            return number
        print(f"⚠️ 범위를 벗어났습니다. {low}-{high} 사이의 숫자를 입력하세요.")
