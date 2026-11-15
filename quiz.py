"""퀴즈 한 문제를 표현하는 Quiz 클래스."""


class Quiz:
    """문제(question), 선택지 4개(choices), 정답 번호(answer, 1~4)를 가진 퀴즈."""

    CHOICE_COUNT = 4

    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = list(choices)
        self.answer = answer  # 정답은 1~4 중 하나의 '번호'로 관리한다.

    def display(self, number=None):
        """문제와 선택지를 화면에 출력한다. number가 있으면 [문제 N] 머리말을 붙인다."""
        if number is not None:
            print(f"[문제 {number}]")
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")
        print()

    def is_correct(self, user_answer):
        """사용자가 고른 번호가 정답이면 True를 반환한다."""
        return user_answer == self.answer

    def answer_text(self):
        """정답 번호와 내용을 '3번 (내용)' 형태의 문자열로 반환한다."""
        return f"{self.answer}번 ({self.choices[self.answer - 1]})"
