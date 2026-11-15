"""퀴즈 한 문제를 표현하는 Quiz 클래스."""


class Quiz:
    """문제(question), 선택지 4개(choices), 정답 번호(answer, 1~4)를 가진 퀴즈.

    메서드:
        __init__(question, choices, answer)  값을 검사하고 저장 (잘못되면 ValueError)
        display(number)                      문제와 선택지를 화면에 출력
        is_correct(user_answer)              고른 번호가 정답이면 True
        answer_text()                        '2번 (내용)' 형태의 정답 문자열
        to_dict() / from_dict(data)          state.json 저장용 dict ↔ Quiz 변환
    화면 출력(display)만 빼면 입출력에 의존하지 않아 다른 프로그램에서도 그대로 재사용할 수 있다.
    """

    CHOICE_COUNT = 4

    def __init__(self, question, choices, answer):
        # 잘못된 퀴즈가 만들어지지 않도록 생성할 때 바로 검사한다. 틀리면 ValueError.
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제가 비어 있거나 문자열이 아닙니다.")
        if (not isinstance(choices, list) or len(choices) != self.CHOICE_COUNT
                or not all(isinstance(choice, str) and choice.strip() for choice in choices)):
            raise ValueError("선택지는 비어 있지 않은 문자열 4개여야 합니다.")
        # bool은 int의 한 종류(True == 1)라서 따로 걸러 낸다.
        if isinstance(answer, bool) or not isinstance(answer, int) or not 1 <= answer <= self.CHOICE_COUNT:
            raise ValueError("정답은 1~4 사이의 정수여야 합니다.")

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

    def to_dict(self):
        """JSON으로 저장할 수 있도록 dict로 바꿔 반환한다."""
        return {"question": self.question, "choices": self.choices, "answer": self.answer}

    @classmethod
    def from_dict(cls, data):
        """state.json에서 읽은 dict로 Quiz를 만든다. 키가 없으면 KeyError, 값이 틀리면 ValueError."""
        return cls(data["question"], data["choices"], data["answer"])
